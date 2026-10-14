"""Generalized Jonathan-V2 leg and Andy spring/motor-sizing experiment.

Invocation: import study(payload), inverse_dynamics(), or verify_pymunk(); CLI
python generalized_leg.py [input.json] writes JSON to stdout. Geometry inputs
use V2 mm/degrees/kg/N, spring inputs use SI metres/N-per-m, and trajectory
outputs label seconds, radians, Nm, N and mm. Requires NumPy/SciPy; Pymunk is
loaded only for rigid-body verification. Outputs are JSON-compatible studies.
Limitations: ideal open belts, massless spring transmissions, prescribed
bilateral fixtures, no rolling/contact feasibility, damping, friction, impacts,
strength, coil bind, hardware rating or canonical robot validation. Legacy
solvers and the rejected IMPOSSIBLE dual-rope design are never modified.
"""
from __future__ import annotations

import json
import math
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize

# Reuse the existing experimental force laws without importing this study into
# Motion Lab or copying its established mechanism definitions.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'wheel-leg-lab'))
from spring_mechanisms import CATALOG, MECHANISM_DEFAULTS, spring_law


DEFAULT_CONFIG = dict(L2=250., L3=250., ra=100., rb=60., rc=35., rd=35.,
                      re=35., rf=35., rw=200., phi0=0., alpha=0., beta=13.5,
                      te=100., tc=165., m1=10., m2=0., m3=0., m5=0., m6=0.,
                      r5I=35., g=9.81, Fy=100., Fz=100., Fn=98.1, Ft=0.,
                      loadMode='yz')
BODY_KEYS = ('hip', 'upper', 'lower', 'compound', 'wheel')


def config(values=None):
    """Resolve a V2 demonstration profile, explicitly recording its assumptions."""
    c = {**DEFAULT_CONFIG, **(values or {})}
    for key in DEFAULT_CONFIG:
        if key != 'loadMode' and (isinstance(c[key], bool) or not isinstance(c[key], (int, float))
                                  or not math.isfinite(c[key])):
            raise ValueError(f'{key} must be a finite number.')
    for key in ('L2', 'L3', 'ra', 'rb', 'rc', 'rd', 're', 'rf', 'rw', 'r5I'):
        if c[key] <= 0:
            raise ValueError(f'{key} must be positive mm.')
    if min(c[k] for k in ('m1', 'm2', 'm3', 'm5', 'm6', 'g')) < 0:
        raise ValueError('Masses and gravity must be nonnegative.')
    if not c['te'] < c['tc'] or c['tc']-c['te'] > 180:
        raise ValueError('Require te < tc and an angle interval no wider than 180 degrees.')
    if c['ra']+c['rb'] >= c['L2'] or c['rc']+c['rd'] >= c['L2'] or c['re']+c['rf'] >= c['L3']:
        raise ValueError('V2 pitch circles overlap; repair radii/link lengths.')
    if c['loadMode'] not in ('yz', 'nt'):
        raise ValueError('loadMode must be yz or nt.')
    c.update(qab=c['ra']/c['rb'], qcd=c['rc']/c['rd'], qef=c['re']/c['rf'])
    c['K'] = 1-c['qab']+c['qef']*(c['qab']-c['qcd'])
    beta = math.radians(c['beta'])
    if c['loadMode']=='yz':
        c.update(Fn=c['Fy']*math.sin(beta)+c['Fz']*math.cos(beta),
                 Ft=c['Fy']*math.cos(beta)-c['Fz']*math.sin(beta))
    else:
        c.update(Fy=c['Fn']*math.sin(beta)+c['Ft']*math.cos(beta),
                 Fz=c['Fn']*math.cos(beta)-c['Ft']*math.sin(beta))
    return c


def _rot(v, angle):
    co, si = math.cos(angle), math.sin(angle)
    return np.array((co*v[0]-si*v[1], si*v[0]+co*v[1]))


def kinematics(q, c, fixture='fixed_a'):
    """Exact V2 positions and their first/second q derivatives in SI units."""
    if fixture not in ('fixed_a', 'supported_chassis'):
        raise ValueError('fixture must be fixed_a or supported_chassis.')
    L2, L3 = c['L2']/1000, c['L3']/1000
    h = 1-c['qab']; a = math.radians(c['alpha'])
    t3 = math.radians(c['phi0'])+(math.pi-q)*(c['qab']-1)
    B = -L2*_rot((math.cos(q), math.sin(q)), -a)
    D = -L3*_rot((math.cos(t3), math.sin(t3)), -a)
    Bp = L2*_rot((math.sin(q), -math.cos(q)), -a)
    Dp = h*L3*_rot((math.sin(t3), -math.cos(t3)), -a)
    Bpp = -B; Dpp = -h*h*D
    C, Cp, Cpp = B+D, Bp+Dp, Bpp+Dpp
    A, Ap, App = (np.zeros(2), np.zeros(2), np.zeros(2))
    if fixture == 'supported_chassis':
        A, Ap, App = -C, -Cp, -Cpp
    points = dict(A=A, B=A+B, C=A+C)
    deriv = dict(A=Ap, B=Ap+Bp, C=Ap+Cp)
    second = dict(A=App, B=App+Bpp, C=App+Cpp)
    positions = dict(hip=A, upper=A+B/2, lower=A+B+D/2,
                     compound=A+B, wheel=A+C)
    jacobians = dict(hip=Ap, upper=Ap+Bp/2, lower=Ap+Bp+Dp/2,
                     compound=Ap+Bp, wheel=Ap+Cp)
    curvature = dict(hip=App, upper=App+Bpp/2, lower=App+Bpp+Dpp/2,
                     compound=App+Bpp, wheel=App+Cpp)
    angles = dict(hip=-a, upper=q+math.pi-a, lower=t3+math.pi-a,
                  compound=(1-c['qcd'])*(q-math.radians(c['te']))-a,
                  wheel=c['K']*(q-math.radians(c['te']))-a)
    angular_jacobian = dict(hip=0., upper=1., lower=h,
                            compound=1-c['qcd'], wheel=c['K'])
    return dict(points=points, positions=positions, jacobians=jacobians,
                curvature=curvature, angles=angles, angular_jacobian=angular_jacobian,
                relative_C=C, relative_C_jacobian=Cp, relative_C_curvature=Cpp,
                q=q, theta3=t3, fixture=fixture)


def body_properties(c):
    """V2 rod-centroid/rim inertias; m1 at A has fixed pitch."""
    masses = dict(zip(BODY_KEYS, (c['m1'], c['m2'], c['m3'], c['m5'], c['m6'])))
    inertias = dict(hip=0., upper=c['m2']*(c['L2']/1000)**2/12,
                    lower=c['m3']*(c['L3']/1000)**2/12,
                    compound=c['m5']*(c['r5I']/1000)**2,
                    wheel=c['m6']*(c['rw']/1000)**2)
    return masses, inertias


def resolved_spring(c, topology='gravity_balance', overrides=None):
    """New generalized spring profile; defaults are documented illustrations."""
    if topology not in CATALOG and topology != 'symmetric_knee_bellcrank':
        raise ValueError('Unknown generalized topology; dual_rope is IMPOSSIBLE/rejected.')
    seed = deepcopy(CATALOG['knee_bellcrank' if topology == 'symmetric_knee_bellcrank' else topology]['defaults'])
    s = {**MECHANISM_DEFAULTS, **seed, 'stiffness': 8000., 'damping': 0.,
         'rest_length': .20, 'extension': .05, 'spring_topology': topology,
         'spring_coil_ref': .60, 'spring_input_ref': .60,
         'length': c['L2']/1000, 'theta': 180-c['te']}
    # New variant preserves the existing symmetric attachment's femur-distance.
    if topology == 'symmetric_knee_bellcrank':
        s.update(spring_upper_fraction=.05/(c['L2']/1000), spring_bellcrank_offset_deg=0.)
    s.update(overrides or {})
    s['spring_topology'] = topology
    if s['damping'] != 0:
        raise ValueError('This generalized sizing study is explicitly undamped; damping must be zero.')
    if not 0 < s['extension'] < c['L3']/1000:
        raise ValueError('Extension must be positive and shorter than L3.')
    if not all(math.isfinite(s[k]) for k in ('stiffness', 'rest_length', 'spring_coil_ref',
                                            'spring_input_ref', 'spring_pulley_radius',
                                            'spring_bellcrank_radius', 'spring_chassis_x', 'spring_chassis_y')):
        raise ValueError('Spring dimensions must be finite SI numbers.')
    if min(s[k] for k in ('rest_length', 'spring_coil_ref', 'spring_input_ref',
                          'spring_pulley_radius', 'spring_bellcrank_radius')) <= 0 or s['stiffness'] < 0:
        raise ValueError('Spring dimensions must be positive and rate nonnegative.')
    if s['spring_direction'] not in (-1, 1):
        raise ValueError('spring_direction must be +1 or -1.')
    if s['spring_transmission'] not in ('direct', 'pullrod', 'ideal_rope'):
        raise ValueError('Unknown spring transmission.')
    if s['spring_mode'] not in ('extension', 'compression', 'captured'):
        raise ValueError('Unknown spring mode.')
    for key in ('spring_upper_fraction', 'spring_lower_fraction'):
        if not 0 <= s[key] <= 1:
            raise ValueError(f'{key} must lie in [0,1].')
    return s


def spring_geometry(q, c, s, fixture='fixed_a', bodies=None):
    """Actual generalized direct anchors/payout and force sites, no 2:1 reuse.

    Body axes run A→B and B→C. Direct sites adapt each link's own length.
    Hip payout derivative is direction*r; relative-knee payout is direction*
    qab*r. The Jacobian is calculated from independent analytical site speeds.
    When bodies are supplied, locations/spans use their actual engine poses.
    """
    k = kinematics(q, c, fixture); L2, L3 = c['L2']/1000, c['L3']/1000
    topology = s['spring_topology']; qref = math.radians(c['te'])
    def point(key, local):
        local = np.array(local)
        if bodies is None:
            world = k['positions'][key]+_rot(local, k['angles'][key])
            velocity = k['jacobians'][key]+k['angular_jacobian'][key]*_rot((-local[1], local[0]), k['angles'][key])
        else:
            body = bodies[key]; world = np.array(body.local_to_world(tuple(local)))
            velocity = np.array(body.velocity_at_world_point(tuple(world)))
        return world, velocity
    uf = ((s['spring_upper_fraction']-.5)*L2, 0.)
    lf = ((s['spring_lower_fraction']-.5)*L3, 0.)
    mount = (s['spring_chassis_x'], s['spring_chassis_y'])
    arm = s['spring_bellcrank_radius']*np.array((math.cos(math.radians(s['spring_bellcrank_offset_deg'])),
                                                math.sin(math.radians(s['spring_bellcrank_offset_deg']))))
    if topology in ('hip_pulley', 'knee_pulley', 'knee_capture'):
        radius, direction = s['spring_pulley_radius'], s['spring_direction']
        if topology == 'hip_pulley':
            J = direction*radius; key1, key2 = 'upper', 'hip'
            center, _ = point('upper', (-L2/2, 0))
            angle = k['angles']['hip'] if bodies is None else bodies['hip'].angle
            u = _rot((1., 0.), angle); n = _rot((0., 1.), angle)
            pa = center+direction*radius*n; pb = pa+s['spring_input_ref']*u
            dir1, dir2 = u, -u
            delta_q = q-qref if bodies is None else bodies['upper'].angle-k['angles']['upper']+q-qref
        else:
            J = direction*radius*c['qab']; key1, key2 = 'lower', 'upper'
            center, _ = point('upper', (L2/2, 0))
            angle = k['angles']['upper'] if bodies is None else bodies['upper'].angle
            u = _rot((1., 0.), angle); n = _rot((0., 1.), angle)
            pa = center+direction*radius*n; pb = pa-L2*u
            dir1, dir2 = -u, u
            if bodies is None:
                delta_q = q-qref
            else:
                initial = kinematics(qref, c)['angles']
                delta_q = -((bodies['lower'].angle-bodies['upper'].angle)-(initial['lower']-initial['upper']))/c['qab']
        length = s['spring_input_ref']+J*delta_q
        sites = [dict(body=key1, world=pa.tolist(), direction=dir1.tolist()),
                 dict(body=key2, world=pb.tolist(), direction=dir2.tolist())]
        kind = 'pulley'
    else:
        if topology == 'legacy_tip':
            a, b = ('hip', (0., 0.)), ('lower', (-L3/2-s['extension'], 0.))
        elif topology == 'direct_scissor':
            a, b = ('upper', uf), ('lower', lf)
        elif topology == 'hip_bellcrank':
            a, b = ('hip', mount), ('upper', arm+(-L2/2, 0.))
        elif topology in ('knee_bellcrank', 'symmetric_knee_bellcrank'):
            a, b = ('upper', uf), ('lower', arm+(-L3/2, 0.))
        elif topology == 'chassis_direct':
            a, b = ('hip', mount), ('lower', lf)
        elif topology == 'gravity_balance':
            a, b = ('hip', mount), ('upper', uf)
        else:
            raise ValueError('Unknown topology.')
        pa, va = point(*a); pb, vb = point(*b); delta = pb-pa
        length = np.linalg.norm(delta)
        if length < 1e-9:
            raise ValueError('Spring anchors coincide.')
        n = delta/length
        # Actual force geometry and analytical q-Jacobian are distinct inputs.
        if bodies is None:
            J = float(n@(vb-va))
        else:
            J = spring_geometry(q, c, s, fixture)['jacobian']
        sites = [dict(body=a[0], world=pa.tolist(), direction=n.tolist()),
                 dict(body=b[0], world=pb.tolist(), direction=(-n).tolist())]
        kind = 'direct'
    if length <= 0:
        raise ValueError('Spring payout crossed zero.')
    return dict(topology=topology, kind=kind, input_length=float(length), jacobian=float(J),
                force_sites=sites, jacobian_basis='generalized theta2 radians',
                physical_guide_ratio=c['qab'], absolute_lower_slope=1-c['qab'])


def spring_state(q, qd, c, s, fixture='fixed_a', bodies=None):
    geom = spring_geometry(q, c, s, fixture, bodies)
    reference = spring_geometry(math.radians(c['te']), c, s)['input_length']
    # Existing passive coil law is shared; its equal-link geometry is not called.
    law_config = {**s, 'spring_topology': ('knee_bellcrank' if s['spring_topology'] == 'symmetric_knee_bellcrank' else s['spring_topology'])}
    law = spring_law(geom['input_length'], geom['jacobian']*qd, law_config, reference)
    return dict(geometry=geom, law=law, generalized_force=-law['tension']*geom['jacobian'])


def load(c):
    beta = math.radians(c['beta']); n = np.array((math.sin(beta), math.cos(beta)))
    t = np.array((math.cos(beta), -math.sin(beta)))
    F = np.array((c['Fy'], c['Fz'])) if c['loadMode'] == 'yz' else c['Fn']*n+c['Ft']*t
    Ft = float(F@t); return F, c['rw']/1000*Ft


def inverse_dynamics(q, qd, qdd, c, fixture='fixed_a', s=None):
    """Independent energy inverse dynamics, with explicit fixture work.

    M=sum(m|R'|²+I angle'²), H=sum(m R'·R''); tau=M qdd+H qd²+
    V'-Qcontact-Qspring. Fixed-A m1 performs no work. Supported chassis uses
    A=-C, C fixed, m1 gravity exactly once and no prescribed wheel-force work.
    """
    k = kinematics(q, c, fixture); masses, inertias = body_properties(c)
    M = H = Vp = 0.
    for key in BODY_KEYS:
        j, a = k['jacobians'][key], k['curvature'][key]
        M += masses[key]*float(j@j)+inertias[key]*k['angular_jacobian'][key]**2
        H += masses[key]*float(j@a)
        Vp += masses[key]*c['g']*j[1]
    contact = 0.
    if fixture == 'fixed_a':
        F, Mw = load(c)
        contact = float(F@k['jacobians']['wheel'])+Mw*c['K']
    state = spring_state(q, qd, c, s, fixture) if s else None
    Qspring = state['generalized_force'] if state else 0.
    _, moments = body_properties(c)
    _, Mw = load(c)
    drive_ratio = c['qcd']*c['qef']
    tau4 = (moments['compound']*c['qcd']*(1-c['qcd'])*qdd
            +moments['wheel']*drive_ratio*c['K']*qdd
            -(drive_ratio*Mw if fixture=='fixed_a' else 0.))
    return dict(tau_q_Nm=M*qdd+H*qd**2+Vp-contact-Qspring, tau4_Nm=tau4, inertia_kg_m2=M,
                centrifugal_Nm=H*qd**2, gravity_Nm=Vp, contact_Nm=contact,
                spring_Nm=Qspring, spring=state)


def interval(c, start_buffer_mm=20., end_buffer_mm=20.):
    """Trim a strictly monotonic V2 wheel-height path using vertical reserves."""
    if min(start_buffer_mm, end_buffer_mm) < 0:
        raise ValueError('Buffers must be nonnegative mm.')
    lo, hi = math.radians(c['te']), math.radians(c['tc'])
    grid = np.linspace(lo, hi, 501)
    heights = np.array([kinematics(q, c)['relative_C'][1] for q in grid])
    laterals = np.array([kinematics(q, c)['relative_C'][0] for q in grid])
    slopes = np.array([kinematics(q, c)['relative_C_jacobian'][1] for q in grid])
    sign = 1 if heights[-1] > heights[0] else -1
    if np.min(sign*slopes) <= 1e-7:
        raise ValueError('Working height path reverses or approaches a singularity; choose a monotonic nonsingular interval.')
    total = abs(heights[-1]-heights[0]); reserve = (start_buffer_mm+end_buffer_mm)/1000
    if total <= reserve:
        raise ValueError('Buffers consume the full vertical capacity.')
    z0 = heights[0]+sign*start_buffer_mm/1000
    z1 = heights[-1]-sign*end_buffer_mm/1000
    def inverse(z):
        return brentq(lambda q: kinematics(q, c)['relative_C'][1]-z, lo, hi,
                      xtol=1e-13, rtol=1e-13)
    return dict(q_start=inverse(z0), q_end=inverse(z1), z_start=z0, z_end=z1,
                total_capacity_mm=total*1000, usable_lift_mm=(total-reserve)*1000,
                lateral_travel_mm=float((kinematics(hi, c)['relative_C'][0]-kinematics(lo, c)['relative_C'][0])*1000),
                lateral_excursion_mm=float(np.max(np.abs(laterals-laterals[0]))*1000),
                lateral_range_mm=float(np.ptp(laterals)*1000),
                start_buffer_mm=start_buffer_mm, end_buffer_mm=end_buffer_mm,
                inverse=inverse, direction=sign)


def trajectory(c, duration_s=1., sample_count=201, start_buffer_mm=20., end_buffer_mm=20.):
    """C2 quintic vertical lift and exact chain-rule angular speed/acceleration."""
    if not .05 <= duration_s <= 30 or not 21 <= sample_count <= 1001:
        raise ValueError('Use duration .05–30 s and sample_count 21–1001.')
    p = interval(c, start_buffer_mm, end_buffer_mm); rows = []
    for time in np.linspace(0, duration_s, int(sample_count)):
        u = time/duration_s; S = 10*u**3-15*u**4+6*u**5
        Sd = (30*u**2-60*u**3+30*u**4)/duration_s
        Sdd = (60*u-180*u**2+120*u**3)/duration_s**2
        z = p['z_start']+(p['z_end']-p['z_start'])*S
        zd = (p['z_end']-p['z_start'])*Sd; zdd = (p['z_end']-p['z_start'])*Sdd
        q = p['inverse'](z); k = kinematics(q, c)
        jz, hz = k['relative_C_jacobian'][1], k['relative_C_curvature'][1]
        qd = zd/jz; qdd = (zdd-hz*qd**2)/jz
        rows.append(dict(time_s=float(time), theta2_deg=math.degrees(q), q_rad=q,
                         qdot_rad_s=float(qd), qddot_rad_s2=float(qdd),
                         lift_mm=(z-p['z_start'])*p['direction']*1000,
                         vertical_speed_mm_s=zd*1000, vertical_accel_mm_s2=zdd*1000,
                         relative_knee_speed_rad_s=-c['qab']*qd,
                         relative_knee_accel_rad_s2=-c['qab']*qdd))
    return rows, {key: value for key, value in p.items() if key != 'inverse'}


def reverse_trajectory(rows):
    """Time reverse a C2 compression path to raise anchored-wheel chassis A."""
    reverse = []
    for original, source in zip(rows, reversed(rows)):
        row = {**source, 'time_s': original['time_s'], 'lift_mm': original['lift_mm']}
        for key in ('qdot_rad_s', 'relative_knee_speed_rad_s', 'vertical_speed_mm_s'):
            row[key] = -row[key]
        reverse.append(row)
    return reverse


def fit_spring(c, topology, q_values, fixture='supported_chassis', overrides=None):
    """Constrained passive fit, rejecting invalid free lengths and rope pushing.

    A linear input tension T=k*(ell-ell_ref)+b is fit in torque space, k>=0.
    Direct Hooke coils require positive free length; reversing compression
    requires positive physical coil lengths and tension throughout. Geometry
    is held fixed; a zero-load fit is reported, never advertised as assistance.
    """
    s = resolved_spring(c, topology, overrides)
    qs = np.array(q_values); gs = [spring_geometry(q, c, s, fixture) for q in qs]
    ell = np.array([g['input_length'] for g in gs]); J = np.array([g['jacobian'] for g in gs])
    ref = spring_geometry(math.radians(c['te']), c, s)['input_length']
    target = np.array([inverse_dynamics(q, 0., 0., c, fixture)['tau_q_Nm'] for q in qs])
    # Force sign follows the configured passive law rather than a free signed fit.
    eta = 1 if s['spring_transmission'] == 'direct' else -1
    nominal = ell if eta == 1 else s['spring_coil_ref']-(ell-ref)
    if np.min(nominal) <= .005:
        return dict(topology=topology, feasible=False, reason='Coil reference travel crosses zero.', config=s)
    zero = s['spring_force_law'] == 'zero_effective'
    if zero:
        design = (J*(ell-s['spring_effective_free_length']))[:, None]
        rate = max(0., float(-design[:, 0]@target/(design[:, 0]@design[:, 0]+1e-30)))
        s['stiffness'] = rate
    else:
        # Scale rate as N/mm for a well-conditioned two-variable optimization.
        design = np.column_stack((J*(ell-ref)*1000, J))
        def objective(x):
            residual = target+design@x
            return float(residual@residual/len(qs))
        def jac(x):
            return 2*design.T@(target+design@x)/len(qs)
        def constraints(x):
            rate, preload = x[0]*1000, x[1]
            T = rate*(ell-ref)+preload
            # free = ref-b/k (direct), coil_ref+b/k (reversing).
            # Multiplying by k permits the zero-rate/zero-load limiting case.
            free_k = rate*(ref if eta == 1 else s['spring_coil_ref'])-eta*preload
            values = [free_k-.005*rate, 1.*rate-free_k]
            if s['spring_transmission'] == 'ideal_rope' or s['spring_mode'] == 'extension':
                values.extend(T if eta == 1 or s['spring_transmission'] == 'ideal_rope' else -T)
            elif s['spring_mode'] == 'compression':
                values.extend(-eta*T)
            return np.array(values)
        result = minimize(objective, np.array((1., 0.)), jac=jac, method='SLSQP',
                          bounds=((0., 200.), (-20000., 20000.)),
                          constraints=dict(type='ineq', fun=constraints),
                          options=dict(ftol=1e-10, maxiter=180))
        if not result.success or np.min(constraints(result.x)) < -1e-5:
            return dict(topology=topology, feasible=False, reason='No converged physically admissible passive fit: '+result.message, config=s)
        rate, preload = result.x[0]*1000, result.x[1]
        s['stiffness'] = max(0., rate)
        s['rest_length'] = (ref if eta == 1 else s['spring_coil_ref'])-eta*preload/rate if rate > 1e-6 else .20
    try:
        states = [spring_state(q, 0., c, s, fixture) for q in qs]
        residual = np.array([target[i]-x['generalized_force'] for i, x in enumerate(states)])
        forces = np.array([x['law']['coil_load'] for x in states])
        lengths = np.array([x['law']['coil_length'] for x in states])
        if s['rest_length'] < .005-1e-9 or np.min(lengths) <= 0:
            raise ValueError('Invalid physical coil free/travel length.')
        if s['spring_transmission'] == 'ideal_rope' and any(x['law']['tension'] < -1e-9 for x in states):
            raise ValueError('Rope cannot push.')
    except ValueError as error:
        return dict(topology=topology, feasible=False, reason=str(error), config=s)
    no_rms = float(np.sqrt(np.mean(target**2))); rms = float(np.sqrt(np.mean(residual**2)))
    return dict(topology=topology, label=CATALOG.get(topology, {}).get('label', 'Separate symmetric knee bellcrank'),
                feasible=True, useful_assistance=rms < .99*no_rms,
                stiffness_N_mm=s['stiffness']/1000,
                preload_N=float(states[0]['law']['coil_load']),
                physical_free_length_mm=s['rest_length']*1000,
                stroke_mm=float(np.ptp(lengths)*1000), peak_force_N=float(np.max(np.abs(forces))),
                coil_force_signed_at_peak_N=float(states[int(np.argmax(np.abs(forces)))]['law']['coil_tension']),
                installed_coil_force_signed_N=float(states[0]['law']['coil_tension']),
                peak_residual_torque_Nm=float(np.max(np.abs(residual))), residual_rms_Nm=rms,
                unassisted_rms_Nm=no_rms, config=s,
                exact_constant_lift=(topology == 'gravity_balance' and abs(c['qab']-2)<1e-12
                                     and abs(c['L2']-c['L3'])<1e-9 and abs(c['alpha'])<1e-12
                                     and abs(c['phi0'])<1e-12 and abs(s['spring_chassis_x'])<1e-12
                                     and s['spring_chassis_y']<0 and s['spring_upper_fraction']>0
                                     and s['spring_effective_free_length']==0
                                     and s['spring_force_law']=='zero_effective'
                                     and ((s['spring_transmission']=='direct' and s['spring_mode'] in ('extension','captured'))
                                          or (s['spring_transmission']!='direct' and s['spring_mode'] in ('compression','captured')))),
                fit_weighting='Uniform theta2 angle, 81 samples; trajectory RMS separately uses time.',
                geometry_feasible=True, ideal_coil_feasible=True,
                hardware_clearance_verified=False, coil_solid_height_verified=False,
                force_and_stroke_constraints='Physical positivity and passive force sign enforced; no supplied hardware force/stroke rating.',
                notes=['Passive torque fit with nonnegative rate and physical free length; geometry/hardware not optimized.',
                       'No damping; zero-effective law requires ideal routing/preload emulation.'] if zero else
                      ['Passive torque fit with nonnegative rate, unilateral sign and physical free length constraints; no damping.'])


def _metrics(rows):
    channels = dict(torque='tau_motor_Nm', speed='motor_speed_rad_s', accel='motor_accel_rad_s2',
                    joint_torque='tau_q_Nm', joint_speed='qdot_rad_s', joint_accel='qddot_rad_s2')
    result = {}
    times = np.array([row['time_s'] for row in rows]); duration = times[-1]-times[0]
    for label, key in channels.items():
        data = np.array([row[key] for row in rows]); i = int(np.argmax(np.abs(data)))
        result[label+'_peak_abs'] = float(abs(data[i])); result[label+'_signed_at_peak'] = float(data[i])
        result[label+'_rms'] = float(np.sqrt(np.trapezoid(data*data, times)/duration))
    return result


def size_fixture(c, base_rows, fixture, s=None, actuator_coordinate='hip', reduction=1., efficiency=1.):
    if actuator_coordinate not in ('hip', 'relative_knee') or not math.isfinite(reduction) or reduction <= 0 or not 0 < efficiency <= 1:
        raise ValueError('Choose hip/relative_knee coordinate, positive reduction and 0<efficiency<=1.')
    factor = 1 if actuator_coordinate == 'hip' else -c['qab']
    rows = []
    for row in base_rows:
        d = inverse_dynamics(row['q_rad'], row['qdot_rad_s'], row['qddot_rad_s2'], c, fixture, s)
        spring = d['spring']; kin = kinematics(row['q_rad'], c, fixture)
        rows.append({**row, 'tau_q_Nm': d['tau_q_Nm'], 'tau4_Nm': d['tau4_Nm'], 'tau_joint_Nm': d['tau_q_Nm']/factor,
                     'tau_motor_Nm': d['tau_q_Nm']/factor/reduction/efficiency,
                     'motor_speed_rad_s': row['qdot_rad_s']*factor*reduction,
                     'motor_accel_rad_s2': row['qddot_rad_s2']*factor*reduction,
                     'spring_force_N': spring['law']['coil_load'] if spring else 0.,
                     'spring_coil_force_signed_N': spring['law']['coil_tension'] if spring else 0.,
                     'spring_coil_length_mm': spring['law']['coil_length']*1000 if spring else 0.,
                     'spring_input_length_mm': spring['geometry']['input_length']*1000 if spring else 0.,
                     'spring_tension_N': spring['law']['tension'] if spring else 0.,
                     'spring_torque_Nm': d['spring_Nm'], 'gravity_torque_Nm': d['gravity_Nm'],
                     'inertial_torque_Nm': d['tau_q_Nm']+d['contact_Nm']+d['spring_Nm']-d['gravity_Nm'],
                     'A_mm': (kin['points']['A']*1000).tolist(), 'B_mm': (kin['points']['B']*1000).tolist(),
                     'C_mm': (kin['points']['C']*1000).tolist(),
                     'spring_geometry': spring['geometry'] if spring else None})
    return dict(fixture=fixture, trajectory=rows, metrics=_metrics(rows),
                actuator_coordinate=actuator_coordinate, reduction=reduction, efficiency=efficiency,
                assumed_efficiency_model='Conservative motoring torque /eta in both signs; regeneration not modeled.',
                prescribed_contact=fixture=='fixed_a',
                fixture_description=('Fixed A; prescribed contact force at P; m1 at A contributes zero suspension torque.'
                                     if fixture=='fixed_a' else 'Wheel C fully anchored; chassis A follows -C(q); m1 gravity once; wheel support reaction does no translational work.'))


def virtual_work_checks(c, s, q_values):
    """Independent position/energy finite differences and actual-site power."""
    max_j = max_energy = max_power = 0.; eps = 1e-6
    for q in q_values:
        st = spring_state(q, 1., c, s); geom = st['geometry']
        plus = spring_state(q+eps, 0., c, s); minus = spring_state(q-eps, 0., c, s)
        fd = (plus['geometry']['input_length']-minus['geometry']['input_length'])/(2*eps)
        max_j = max(max_j, abs(fd-geom['jacobian']))
        energy_derivative = (plus['law']['energy']-minus['law']['energy'])/(2*eps)
        max_energy = max(max_energy, abs(energy_derivative+st['generalized_force']))
        k = kinematics(q, c)
        power = 0.
        for site in geom['force_sites']:
            key = site['body']; arm = np.array(site['world'])-k['positions'][key]
            speed = k['jacobians'][key]+k['angular_jacobian'][key]*np.array((-arm[1], arm[0]))
            power += st['law']['tension']*np.array(site['direction'])@speed
        max_power = max(max_power, abs(power-st['generalized_force']))
    return dict(jacobian_fd_error_m_rad=max_j, energy_fd_error_Nm=max_energy,
                actual_site_virtual_work_error_Nm=float(max_power), samples=len(q_values),
                passed=bool(max_j < 1e-7 and max_energy < 1e-4 and max_power < 1e-7))


def _engine_run(c, s, fixture, dt, duration_s, buffers, hold_q=None, direction='compression'):
    """Advance actual constrained bodies, observing motor impulse independently.

    Only the initial state is assigned. Subsequent motion comes from Space.step
    and motor/guide/pivot constraints. No pose reset or copied analytical torque
    is applied. Dynamic body masses must be positive; no hidden regularization.
    """
    import pymunk
    ec = dict(c)
    required = ('m2', 'm3', 'm5', 'm6')+ (('m1',) if fixture == 'supported_chassis' else ())
    if min(ec[key] for key in required) <= 0:
        raise ValueError('Pymunk requires positive dynamic body masses; use the explicit physical mass allocation, not the massless screenshot limit.')
    path = interval(ec, *buffers)
    q0 = (path['q_start'] if direction=='compression' else path['q_end']) if hold_q is None else hold_q
    initial = kinematics(q0, ec, fixture); masses, moments = body_properties(ec)
    space = pymunk.Space(); space.gravity = (0., -ec['g']); space.iterations = 800
    space.damping = 1.
    bodies = {}
    for key in BODY_KEYS:
        if key == 'hip' and fixture == 'fixed_a':
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            body = pymunk.Body(masses[key], float('inf') if key == 'hip' else moments[key])
        body.position = tuple(initial['positions'][key]); body.angle = initial['angles'][key]
        space.add(body); bodies[key] = body
    L2, L3 = ec['L2']/1000, ec['L3']/1000
    pivots = [pymunk.PivotJoint(bodies['hip'], bodies['upper'], (0., 0.), (-L2/2, 0.)),
              pymunk.PivotJoint(bodies['upper'], bodies['lower'], (L2/2, 0.), (-L3/2, 0.)),
              pymunk.PivotJoint(bodies['lower'], bodies['wheel'], (L3/2, 0.), (0., 0.)),
              pymunk.PivotJoint(bodies['upper'], bodies['compound'], (L2/2, 0.), (0., 0.))]
    if fixture == 'supported_chassis':
        pivots.append(pymunk.PivotJoint(space.static_body, bodies['wheel'], tuple(initial['positions']['wheel'])))
    # Chipmunk GearJoint is b.angle*ratio-a.angle=phase. ratio=1-qab
    # here acts on UPPER (b); physical guide ratio qab is a different number.
    gears = []
    for key in ('lower', 'compound', 'wheel'):
        slope = initial['angular_jacobian'][key]
        if abs(slope) < 1e-12:
            # Chipmunk divides by ratio internally: zero slope uses a genuine
            # locked rotor, never an invalid zero-ratio gear.
            gears.append(pymunk.GearJoint(space.static_body, bodies[key], bodies[key].angle, 1.))
        else:
            phase = slope*bodies['upper'].angle-bodies[key].angle
            gears.append(pymunk.GearJoint(bodies[key], bodies['upper'], phase, slope))
    motor = pymunk.SimpleMotor(bodies['upper'], bodies['hip'], 0.)
    constraints = pivots+gears+[motor]
    for constraint in constraints:
        constraint.collide_bodies = False
        constraint.error_bias = (1-.2)**60
    space.add(*constraints)
    def commanded(t):
        if hold_q is not None:
            return hold_q, 0., 0.
        u = min(1., max(0., t/duration_s)); smooth = 10*u**3-15*u**4+6*u**5
        sd = (30*u**2-60*u**3+30*u**4)/duration_s
        sdd = (60*u-180*u**2+120*u**3)/duration_s**2
        z_start, z_end = ((path['z_start'],path['z_end']) if direction=='compression' else
                          (path['z_end'],path['z_start']))
        z = z_start+(z_end-z_start)*smooth
        zd = (z_end-z_start)*sd; zdd = (z_end-z_start)*sdd
        q = path['inverse'](z); kin = kinematics(q, ec)
        jz, hz = kin['relative_C_jacobian'][1], kin['relative_C_curvature'][1]
        qd = zd/jz
        return q, qd, (zdd-hz*qd*qd)/jz
    errors = []; trace = []; max_phase = max_pin = max_pose = max_force_power = 0.
    steps = math.ceil(duration_s/dt)
    for i in range(steps):
        time = i*dt; command, qd, qdd = commanded(time)
        next_q = commanded(min(duration_s, time+dt))[0]
        motor.rate = (next_q-command)/dt
        # Body forces use actual spring locations and actual payout; no ideal
        # forcing torque is copied onto upper/lower bodies.
        actual_q = bodies['upper'].angle-math.pi+math.radians(ec['alpha'])
        if s:
            state = spring_state(actual_q, qd, ec, s, fixture, bodies)
            for site in state['geometry']['force_sites']:
                body = bodies[site['body']]
                force = state['law']['tension']*np.array(site['direction'])
                body.apply_force_at_world_point(tuple(force), tuple(site['world']))
        if fixture == 'fixed_a':
            F, Mw = load(ec); wheel = bodies['wheel']
            wheel.apply_force_at_world_point(tuple(F), wheel.position)
            wheel.torque += Mw
        predicted = inverse_dynamics(command, qd, qdd, ec, fixture, s)['tau_q_Nm']
        space.step(dt)
        measured = motor.impulse/dt
        # impulse is a magnitude in Pymunk; torque sign below is explicitly the
        # independent inverse-dynamics sign, not claimed signed engine telemetry.
        # Avoid the initial solver warm-up and endpoint acceleration discretization.
        if time >= max(.015, 3*dt) and time < duration_s-2*dt:
            errors.append(abs(measured-abs(predicted)))
            if i % max(1, steps//100) == 0:
                trace.append(dict(time_s=time, theta2_deg=math.degrees(command),
                                  analytical_tau_q_Nm=predicted, analytical_tau_abs_Nm=abs(predicted),
                                  pymunk_tau_abs_Nm=measured, error_abs_Nm=measured-abs(predicted),
                                  engine_motor_impulse_torque_abs_Nm=measured))
        for gear in gears:
            phase_error = abs(gear.b.angle*gear.ratio-gear.a.angle-gear.phase)
            max_phase = max(max_phase, phase_error)
        for pivot in pivots:
            max_pin = max(max_pin, (pivot.a.local_to_world(pivot.anchor_a)-pivot.b.local_to_world(pivot.anchor_b)).length)
        max_pose = max(max_pose, abs(bodies['upper'].angle-math.pi+math.radians(ec['alpha'])-next_q))
    if not errors:
        raise ValueError('Verification duration too short for impulse sampling.')
    return dict(dt_s=dt, steps=steps, max_torque_error_Nm=max(errors),
                rms_torque_error_Nm=float(np.sqrt(np.mean(np.array(errors)**2))),
                max_pin_error_m=max_pin, max_guide_phase_error_rad=max_phase,
                max_command_angle_error_rad=max_pose, trace=trace,
                mass_regularization_kg={}, resolved_config=ec,
                actual_absolute_guide_slope=1-ec['qab'],
                engine='Pymunk '+pymunk.version,
                scope='Actual Space.step with motor impulses versus independent energy inverse dynamics; no pose resets after initialization.')


def verify_pymunk(c, s, fixture='supported_chassis', duration_s=1., buffers=(20., 20.),
                  timesteps=(.002, .001), hold_q=None, direction='compression'):
    """Actual Pymunk constraint-impulse cross-check with timestep refinement."""
    if duration_s > 8 or duration_s < .1:
        raise ValueError('Rigid-body verification duration must be .1–8 s.')
    if direction not in ('compression','extension'):
        raise ValueError('Verification direction must be compression or extension.')
    runs = [_engine_run(c, s, fixture, dt, duration_s, buffers, hold_q, direction) for dt in timesteps]
    fine = runs[-1]; coarse = runs[0]
    # Absolute and relative resolution limits make failure visible, including
    # poor mass ratios/ill-conditioned user geometries; no unearned certification.
    scale = max((abs(x['analytical_tau_q_Nm']) for x in fine['trace']), default=1.)
    tolerance = max(.15, .015*scale)
    tracking_tolerance = .0001 if hold_q is not None else 2*max(abs(x['qdot_rad_s']) for x in trajectory(c, duration_s, 51, *buffers)[0])*fine['dt_s']+.0001
    passed = (fine['max_torque_error_Nm'] < tolerance and fine['max_pin_error_m'] < .002
              and fine['max_guide_phase_error_rad'] < .002
              and fine['max_command_angle_error_rad'] < tracking_tolerance
              and fine['rms_torque_error_Nm'] <= coarse['rms_torque_error_Nm']*1.1+1e-6)
    return dict(fixture=fixture, motion_direction=direction, topology=s['spring_topology'] if s else 'none',
                passed=bool(passed), torque_tolerance_Nm=tolerance, tracking_tolerance_rad=tracking_tolerance, refinement=runs,
                error_reduction=coarse['rms_torque_error_Nm']/max(1e-15, fine['rms_torque_error_Nm']),
                sign_note='Pymunk reports motor impulse magnitude; signed torque is independently analytical.',
                limitations=['Prescribed bilateral fixtures, ideal belts/springs; no tire rolling or hardware claim.',
                             'Positive dynamic body masses required; massless screenshot remains an analytical limit only.'])


def physical_allocation(c, corner_mass_kg=10.):
    """Explicit assumed design masses, totaling the user-specified per-leg mass."""
    moving = dict(m2=.35, m3=.35, m5=.10, m6=.90)
    chassis = corner_mass_kg-sum(moving.values())
    if chassis <= 0:
        raise ValueError('Corner mass must exceed assumed moving mass 1.70 kg.')
    return config({**c, **moving, 'm1': chassis})


def impact_envelope(c, s, qs, reduction=1., efficiency=1., actuator_coordinate='hip', entered_factor=None):
    """Separate held-geometry support stress, not a multiplied motion trajectory.

    N*g means TOTAL support N*m*g, so upward net acceleration would (N-1)*g.
    Extra support is modeled as an equivalent downward inertial load at chassis
    A, on top of ordinary gravity. The 1g-fitted spring remains unchanged.
    """
    factor_coordinate = 1 if actuator_coordinate == 'hip' else -c['qab']
    cases = []; factors = [1., 3., 4., 5.]
    if entered_factor is not None:
        if not isinstance(entered_factor, (int,float)) or not math.isfinite(entered_factor) or not 1 <= entered_factor <= 8:
            raise ValueError('impact_factor must be finite total support factor in [1,8].')
        if entered_factor not in factors:
            factors.append(float(entered_factor)); factors.sort()
    for corner_mass in (10., 11.25):
        case_config = physical_allocation(c, corner_mass)
        for factor in factors:
            values = []
            for q in qs:
                kin = kinematics(q, case_config, 'supported_chassis')
                tau = inverse_dynamics(q, 0., 0., case_config, 'supported_chassis', s)['tau_q_Nm']
                tau += (factor-1)*corner_mass*case_config['g']*kin['jacobians']['hip'][1]
                values.append(tau/factor_coordinate/reduction/efficiency)
            i = int(np.argmax(np.abs(values)))
            cases.append(dict(corner_mass_kg=corner_mass, total_support_factor_g=factor,
                              total_support_force_N=factor*corner_mass*c['g'],
                              implied_upward_net_accel_g=factor-1,
                              motor_peak_abs_Nm=abs(values[i]), motor_signed_at_peak_Nm=values[i],
                              theta2_peak_deg=math.degrees(qs[i]),
                              spring_preload_retuned=False,
                              assumed_coil_travel='Same held poses as normal working window; impact compression dynamics not integrated.'))
    return dict(cases=cases, worst_motor_peak_abs_Nm=max(x['motor_peak_abs_Nm'] for x in cases),
                definition='3g/4g TOTAL support, separate quasi-static equivalent inertial stress at A; 1g spring unchanged.',
                four_g_net_acceleration_alternative_total_factor=5.,
                limitations=['Peak support is not mean stopping force; no impact waveform/stopping distance supplied.',
                             'Zero damping stores/rebounds energy; this stress envelope cannot certify impact dissipation.'])


def study(payload=None):
    """Bounded API-ready study: two fixtures, nine passive fits and motor traces."""
    payload = payload or {}; nested = payload.get('config', {})
    if payload.get('action', 'size') not in ('size','validate'):
        raise ValueError('action must be size or validate.')
    c = config({**{key: value for key, value in payload.items() if key in DEFAULT_CONFIG}, **nested})
    duration = float(payload.get('duration_s', 1.)); count = int(payload.get('sample_count', 201))
    base_rows, travel = trajectory(c, duration, count, float(payload.get('start_buffer_mm', 20.)),
                                  float(payload.get('end_buffer_mm', 20.)))
    qs = np.linspace(base_rows[0]['q_rad'], base_rows[-1]['q_rad'], 81)
    override = payload.get('spring', {}); selected = override.get('topology', override.get('spring_topology', 'gravity_balance'))
    override = {key: value for key, value in override.items() if key not in ('topology', 'spring_topology')}
    preload_mm = override.pop('preload_mm', None)
    comparisons = [fit_spring(c, key, qs, overrides=override if key == selected else None) for key in CATALOG]
    if selected == 'symmetric_knee_bellcrank':
        comparisons.append(fit_spring(c, selected, qs, overrides=override))
    chosen = next((x for x in comparisons if x['topology'] == selected), None)
    if chosen is None or not chosen['feasible']:
        raise ValueError('Selected spring fit infeasible: '+(chosen['reason'] if chosen else 'Unknown topology.'))
    chosen = deepcopy(chosen)
    # Explicit manual rate/free length override bypasses fitting for the selected
    # mechanism only, retaining comparison fits and reporting the actual coil.
    if 'stiffness' in override or 'rest_length' in override or preload_mm is not None:
        chosen['config'] = resolved_spring(c, selected, override)
        chosen['manual_override'] = True
        if preload_mm is not None:
            if not math.isfinite(preload_mm) or preload_mm < 0:
                raise ValueError('Installed preload_mm must be finite nonnegative mm.')
            manual = chosen['config']; manual['spring_force_law'] = 'hooke'
            initial_length = spring_geometry(base_rows[0]['q_rad'], c, manual)['input_length']
            reference = spring_geometry(math.radians(c['te']), c, manual)['input_length']
            nominal = (initial_length if manual['spring_transmission']=='direct' else
                       manual['spring_coil_ref']-(initial_length-reference))
            sign = -1 if manual['spring_mode']=='compression' or manual['spring_transmission']=='ideal_rope' else 1
            manual['rest_length'] = nominal-sign*preload_mm/1000
            if manual['rest_length'] <= 0:
                raise ValueError('Installed preload requires nonpositive physical free length.')
            chosen['manual_preload_mm'] = preload_mm
    s = chosen['config']; coord = payload.get('actuator_coordinate', 'hip')
    reduction, efficiency = float(payload.get('reduction', 1.)), float(payload.get('efficiency', 1.))
    fixed = size_fixture(c, base_rows, 'fixed_a', None, coord, reduction, efficiency)
    supported = size_fixture(c, base_rows, 'supported_chassis', s, coord, reduction, efficiency)
    supported_no_spring = size_fixture(c, base_rows, 'supported_chassis', None, coord, reduction, efficiency)
    raising = size_fixture(c, reverse_trajectory(base_rows), 'supported_chassis', s, coord, reduction, efficiency)
    supported['motion_direction'] = 'Compression: wheel-relative lift, anchored-wheel chassis lowering.'
    raising['motion_direction'] = 'Extension: anchored-wheel chassis raising; exact time-reversed geometry.'
    cycle_rows = deepcopy(supported['trajectory'])
    cycle_rows.extend({**row, 'time_s': row['time_s']+duration} for row in raising['trajectory'][1:])
    # Chosen summary always describes the actual selected law, including manual
    # overrides; comparison entries retain their individually fitted values.
    chosen = deepcopy(chosen)
    lengths = np.array([row['spring_coil_length_mm'] for row in supported['trajectory']])
    chosen.update(stiffness_N_mm=s['stiffness']/1000,
                  preload_N=supported['trajectory'][0]['spring_force_N'],
                  physical_free_length_mm=s['rest_length']*1000,
                  stroke_mm=float(np.ptp(lengths)),
                  peak_force_N=max(abs(row['spring_force_N']) for row in supported['trajectory']),
                  installed_coil_force_signed_N=supported['trajectory'][0]['spring_coil_force_signed_N'],
                  coil_force_signed_at_peak_N=max(supported['trajectory'],key=lambda row: abs(row['spring_force_N']))['spring_coil_force_signed_N'],
                  trajectory_motor_peak_abs_Nm=supported['metrics']['torque_peak_abs'],
                  trajectory_motor_rms_Nm=supported['metrics']['torque_rms'])
    check = virtual_work_checks(c, s, qs[::10])
    result = dict(schema='wheel-leg/generalized-study/v1', config=c, travel=travel,
                  fixed_fixture=fixed, supported_fixture=supported, supported_raising_fixture=raising,
                  supported_unassisted=supported_no_spring,
                  spring_comparisons=comparisons, selected_spring=chosen, trajectory=supported['trajectory'],
                  metrics=supported['metrics'], virtual_work=check,
                  cycle_trajectory=cycle_rows, cycle_metrics=_metrics(cycle_rows),
                  cycle_duration_s=duration*2,
                  assumptions=dict(duration_s=duration, chassis_corner_mass_kg=c['m1'], reduction=reduction,
                                   efficiency=efficiency, gravity_m_s2=c['g'], damping_N_s_m=0.,
                                   wheel_fixture='fully anchored hub, bilateral support, no rolling'),
                  limitations=['Experimental analytical and rigid-body fixtures; no canonical robot/hardware certification.',
                               'Generalized non-2:1/unequal-link gravity_balance is a passive fit; constant lift is not assumed.',
                               'Corner mass is an editable 10 kg assumption; motor reduction/efficiency default to explicitly assumed 1.',
                               'Dual-rope knee design remains IMPOSSIBLE/rejected; legacy profiles/solvers unchanged.',
                               'No tire rolling/friction, coil solid height, cable stretch or 3D clearance is solved.'])
    sensitivity = []
    for seconds in (.5, 1., 2.):
        time_rows, _ = trajectory(c, seconds, 101, travel['start_buffer_mm'], travel['end_buffer_mm'])
        fitted_run = size_fixture(c, time_rows, 'supported_chassis', s, coord, reduction, efficiency)
        sensitivity.append(dict(duration_s=seconds, metrics=fitted_run['metrics'],
                                raising_metrics=size_fixture(c, reverse_trajectory(time_rows), 'supported_chassis', s, coord, reduction, efficiency)['metrics'],
                                lift_mm=travel['usable_lift_mm']))
    result['time_sensitivity'] = sensitivity
    result['impact_cases'] = impact_envelope(c, s, qs, reduction, efficiency, coord, payload.get('impact_factor'))
    if payload.get('action', 'size') == 'validate':
        # A massless screenshot is not an executable rigid-body baseline.
        physical_c = (physical_allocation(c, float(payload.get('corner_mass_kg', 10.)))
                      if min(c[key] for key in ('m1','m2','m3','m5','m6')) <= 0 else c)
        if physical_c != c:
            result['physical_mass_allocation'] = dict(config=physical_c, total_corner_mass_kg=sum(physical_c[k] for k in ('m1','m2','m3','m5','m6')),
                                                     status='Explicit assumed nonzero physical sensitivity; massless input preserved analytically.')
        result['pymunk_validation'] = verify_pymunk(physical_c, s, 'supported_chassis', duration_s=duration,
                                                  buffers=(travel['start_buffer_mm'], travel['end_buffer_mm']))
        result['pymunk_raising_validation'] = verify_pymunk(physical_c, s, 'supported_chassis', duration_s=duration,
                                                          buffers=(travel['start_buffer_mm'], travel['end_buffer_mm']), direction='extension')
        matrix = []
        for comparison in comparisons:
            if not comparison['feasible']:
                matrix.append(dict(topology=comparison['topology'], passed=False, reason=comparison['reason']))
                continue
            spring_cfg = s if comparison['topology']==selected else comparison['config']
            physical_check = verify_pymunk(physical_c, spring_cfg, 'supported_chassis', duration_s=.12,
                                          buffers=(travel['start_buffer_mm'], travel['end_buffer_mm']), hold_q=float(np.mean(qs)))
            matrix.append(dict(topology=comparison['topology'], passed=physical_check['passed'],
                               virtual_work=virtual_work_checks(c, spring_cfg, qs[::10]),
                               actual_force_sites=spring_geometry(float(np.mean(qs)), physical_c, spring_cfg)['force_sites'],
                               fixture='Held midpoint pose with actual motor and pivot/gear constraint impulses.',
                               refinement=physical_check['refinement']))
        result['pymunk_topology_checks'] = matrix
        result['physical_supported_fixture'] = size_fixture(physical_c, base_rows, 'supported_chassis', s,
                                                           coord, reduction, efficiency)
    return result


if __name__ == '__main__':
    data = json.loads(open(sys.argv[1], encoding='utf-8').read()) if len(sys.argv) > 1 else {}
    print(json.dumps(study(data), allow_nan=False))
