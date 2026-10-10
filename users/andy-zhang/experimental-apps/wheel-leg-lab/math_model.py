"""Independent one-coordinate SciPy suspension model for Wheel Leg Lab.

Invocation: import simulate_math(config), or python math_model.py --output run.json.
Inputs: matching experimental bench config in m, kg, s, N, N m; theta in degrees.
Outputs: JSON-compatible time rows, kinematic frames, joint loads, solver metadata.
Requires NumPy/SciPy; imports neither Pymunk nor the rigid-body model. The model
has an exact equal-link 2:1 guide and a prescribed bilateral wheel support, with
chassis pitch held. It supports only floating chassis, smooth position input and
hub-applied biases. Travel-limit events terminate; stop impacts/contact are not
integrated. Linear-ramp velocity jumps require impulse dynamics and are rejected.
"""
from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from motion_input import position_state

# Experimental defaults shared by value, independently resolved without importing
# the Pymunk fixture. Non-mathematical fields remain in exported profiles so the
# same profile can be opened in the physical tab.
DEFAULTS = {
    'length': .273, 'extension': .05, 'radius': .2, 'theta': 45.,
    'load_point': 'hub', 'wheel_drive_locked': False,
    'theta_min': 15., 'theta_max': 80., 'upper_mass': .6, 'lower_mass': .65,
    'wheel_mass': 1.5, 'chassis_mass': 8., 'gravity': 9.80665,
    'fixture': 'floating', 'stiffness': 8000., 'damping': 100.,
    'rest_length': .23, 'balance_spring': True, 'bias_force': 0.,
    'bias_force_x': 0., 'preload_force': 80., 'knee_kp': 0., 'knee_kd': 0.,
    'torque_limit': 80., 'target': 'position', 'wave': 'step', 'amplitude': 5.,
    'position_amplitude': .03, 'ramp_shape': 'quintic', 'impulse': 2.,
    'start': .5, 'period': 1.5, 'duty': .5, 'pulse_width': .7,
    'rise': .25, 'fall': .25, 'duration': 6., 'dt': .001, 'iterations': 80,
}


def config(values=None):
    """Resolve the mathematical subset of the bench profile, failing explicitly."""
    c = deepcopy(DEFAULTS)
    if values is not None:
        if not isinstance(values, dict):
            raise ValueError('Configuration must be an object.')
        unknown = set(values) - set(c)
        if unknown:
            raise ValueError('Unknown configuration fields: ' + ', '.join(sorted(unknown)))
        c.update(values)
    for key, default in DEFAULTS.items():
        value = c[key]
        if isinstance(default, bool):
            if not isinstance(value, bool):
                raise ValueError(f'{key} must be boolean.')
        elif isinstance(default, (int, float)):
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError(f'{key} must be finite.')
    if c['fixture'] != 'floating' or c['target'] != 'position':
        raise ValueError('The mathematical model requires a floating chassis and prescribed wheel position. Use the physical tab for fixed-fixture/force diagnostics.')
    if c['load_point'] != 'hub':
        raise ValueError('The mathematical model supports hub-applied loads only; tire-bottom contact moments require the physical tab.')
    if c['ramp_shape'] != 'quintic':
        raise ValueError('The mathematical model requires smooth quintic ramps. A linear ramp has velocity jumps requiring separate impulse dynamics.')
    if c['wave'] not in ('step', 'square', 'pulse'):
        raise ValueError('Choose a position step, square wave or pulse.')
    limits = {
        'length': (.08, .8), 'extension': (.005, .15), 'radius': (.05, .4),
        'upper_mass': (.01, 20), 'lower_mass': (.01, 20),
        'wheel_mass': (.01, 30), 'chassis_mass': (.01, 100),
        'gravity': (0, 20), 'stiffness': (0, 100000), 'damping': (0, 2000),
        'rest_length': (.005, 1), 'knee_kp': (0, 2000), 'knee_kd': (0, 200),
        'torque_limit': (.01, 2000), 'duration': (.1, 20), 'dt': (.00025, .004),
        'start': (0, 20), 'period': (.02, 10), 'duty': (.01, .99),
        'pulse_width': (.001, 5), 'rise': (0, 5), 'fall': (0, 5),
        'position_amplitude': (-.5, .5), 'bias_force': (-5000, 5000),
        'bias_force_x': (-5000, 5000), 'iterations': (20, 300),
        'amplitude': (-10000, 10000), 'impulse': (-1000, 1000),
        'preload_force': (-5000, 5000),
    }
    for key, (low, high) in limits.items():
        if not low <= c[key] <= high:
            raise ValueError(f'{key} must be between {low} and {high} (SI units).')
    if c['iterations'] != int(c['iterations']):
        raise ValueError('Iterations must be an integer.')
    if c['extension'] >= c['length']:
        raise ValueError('Extension must be shorter than the knee-to-hub link.')
    if not 3 <= c['theta_min'] < c['theta'] < c['theta_max'] <= 87:
        raise ValueError('Use 3 degrees <= minimum < initial angle < maximum <= 87 degrees.')
    if c['duration'] / c['dt'] > 30000:
        raise ValueError('Limit each run to 30,000 output samples.')
    if c['rise'] < 4*c['dt'] or (c['wave'] != 'step' and c['fall'] < 4*c['dt']):
        raise ValueError('Position ramps need finite rise/fall times of at least four output steps.')
    width = c['period']*c['duty'] if c['wave'] == 'square' else c['pulse_width']
    if c['wave'] != 'step' and c['rise']+c['fall'] > width+1e-12:
        raise ValueError('Rise + fall must fit within on-time / pulse width.')
    return c


def parameters(c):
    """Resolve geometry, body inertias and preload directly from equilibrium."""
    L, e = c['length'], c['extension']
    q0 = math.radians(c['theta'])
    S = 1.5*L*c['upper_mass'] + .5*(L+e)*c['lower_mass'] + 2*L*c['chassis_mass']
    Iu = c['upper_mass']*L*L/12
    Il = c['lower_mass']*(L+e)**2/12
    Iw = .5*c['wheel_mass']*c['radius']**2
    s0 = math.sqrt(L*L+e*e+2*L*e*math.cos(2*q0))
    J0 = -2*L*e*math.sin(2*q0)/s0
    rest = c['rest_length']
    if c['balance_spring']:
        if c['stiffness'] <= 0:
            raise ValueError('Automatic spring balance requires positive spring stiffness.')
        rest = s0 + S*c['gravity']*math.cos(q0)/(c['stiffness']*J0)
        if rest < .005:
            raise ValueError('Spring cannot balance this load; increase stiffness or choose a manual free length.')
    return {'S': S, 'Iu': Iu, 'Il': Il, 'Iw': Iw, 'q0': q0, 'rest': rest}


def terms(q, velocity, c, p):
    """Return energy mass, derivative, spring Jacobian and delivered knee torque."""
    L, e, mu, mh = c['length'], c['extension'], c['upper_mass'], c['chassis_mass']
    sn, cs = math.sin(q), math.cos(q)
    inertia = p['Iu']+p['Il']+(p['Iw'] if c['wheel_drive_locked'] else 0.)
    M = inertia + mu*((L/2)**2*sn*sn+(1.5*L)**2*cs*cs)
    M += c['lower_mass']*((L+e)/2)**2 + 4*mh*L*L*cs*cs
    Mp = (mu*((L/2)**2-(1.5*L)**2)-4*mh*L*L)*math.sin(2*q)
    length = math.sqrt(L*L+e*e+2*L*e*math.cos(2*q))
    J = -2*L*e*math.sin(2*q)/length
    elastic = c['stiffness']*(length-p['rest'])
    damper = c['damping']*J*velocity
    raw = c['knee_kp']*(2*p['q0']-2*q)-c['knee_kd']*2*velocity
    torque = max(-c['torque_limit'], min(c['torque_limit'], raw))
    return M, Mp, length, J, elastic, damper, torque, raw


def derivative(t, state, c, p):
    q, velocity = state
    M, Mp, _, J, elastic, damper, torque, _ = terms(q, velocity, c, p)
    _, _, base_accel = position_state(t, c)
    force = -(elastic+damper)*J + 2*torque
    accel = (force-p['S']*math.cos(q)*(c['gravity']+base_accel)-.5*Mp*velocity**2)/M
    return velocity, accel


def cross(a, b):
    return float(a[0]*b[1]-a[1]*b[0])


def observe(t, q, velocity, c, p):
    """Independent Newton-Euler reconstruction of the constrained leg reactions."""
    L, e, g = c['length'], c['extension'], c['gravity']
    z, zv, za = position_state(t, c)
    _, accel = derivative(t, (q, velocity), c, p)
    _, _, length, J, elastic, damper, torque, raw = terms(q, velocity, c, p)
    sn, cs = math.sin(q), math.cos(q)

    def point(xscale, yscale):
        pos = np.array([xscale*cs, z+yscale*sn])
        vel = np.array([-xscale*sn*velocity, zv+yscale*cs*velocity])
        acc = np.array([-xscale*(cs*velocity**2+sn*accel),
                        za+yscale*(cs*accel-sn*velocity**2)])
        return pos, vel, acc

    A, va, aa = point(0., 2*L)
    B, vb, ab = point(L, L)
    C, vc, ac = point(0., 0.)
    E, _, _ = point(L+e, L+e)
    U, vu, au = point(L/2, 1.5*L)
    D, vd, ad = point((L+e)/2, (L+e)/2)
    gravity = np.array([0., -g])
    fs = -(elastic+damper)*(E-A)/length  # force on lower link
    f1 = -(c['chassis_mass']*(aa-gravity)+fs)  # force on upper at J1
    f2 = f1-c['upper_mass']*(au-gravity)      # force on lower at J2
    f3 = f2+fs-c['lower_mass']*(ad-gravity)  # force on wheel at J3
    external = np.array([c['bias_force_x'], c['bias_force']])
    driver = c['wheel_mass']*(ac-gravity)-external-f3
    wheel_reaction = -p['Iw']*accel if c['wheel_drive_locked'] else 0.
    upper_moment = cross(A-U, f1)+cross(B-U, -f2)
    lower_moment = cross(B-D, f2)+cross(C-D, -f3)+cross(E-D, fs)
    upper_guide = -p['Iu']*accel-upper_moment+torque
    lower_guide = p['Il']*accel-lower_moment-torque-wheel_reaction
    guide = .5*(upper_guide+lower_guide)
    # The difference is a useful independent check of the energy ODE against
    # the separate angular balances, rather than a constraint solver reading.
    angular_error = abs(upper_guide-lower_guide)
    total_mass = sum(c[k] for k in ('upper_mass', 'lower_mass', 'wheel_mass', 'chassis_mass'))
    kinetic = .5*(c['chassis_mass']*float(va@va)+c['upper_mass']*float(vu@vu)
                   +c['lower_mass']*float(vd@vd)+c['wheel_mass']*float(vc@vc))
    kinetic += .5*(p['Iu']+p['Il']+(p['Iw'] if c['wheel_drive_locked'] else 0.))*velocity**2
    potential = g*(c['chassis_mass']*A[1]+c['upper_mass']*U[1]
                   +c['lower_mass']*D[1]+c['wheel_mass']*C[1])
    potential += .5*c['stiffness']*(length-p['rest'])**2
    F, knee_load = -f3, -f2
    Min = L*(-F[1]*cs+F[0]*sn)
    Mact = L*(knee_load[1]*cs+knee_load[0]*sn)
    lower_cross, upper_cross = cross(C-B, F), cross(B-A, knee_load)
    lower_total = lower_cross+cross(E-B, fs)+cross(D-B, c['lower_mass']*gravity)+torque+guide+wheel_reaction
    lower_inertia = p['Il']*accel+cross(D-B, c['lower_mass']*ad)
    upper_total = upper_cross+cross(U-A, c['upper_mass']*gravity)-torque+guide
    upper_inertia = -p['Iu']*accel+cross(U-A, c['upper_mass']*au)
    row = {
        't': float(t), 'input': z, 'input_mm': z*1000,
        'theta_deg': math.degrees(q), 'height': float(A[1]-C[1]),
        'driver_force': float(driver[1]), 'driver_fx': float(driver[0]), 'driver_check': 0.,
        'chassis_displacement': float(A[1]-2*L*math.sin(p['q0'])),
        'chassis_displacement_mm': float((A[1]-2*L*math.sin(p['q0']))*1000),
        'hub_vx': float(vc[0]), 'hub_vy': float(vc[1]), 'hub_ax': float(ac[0]), 'hub_ay': float(ac[1]),
        'chassis_vx': float(va[0]), 'chassis_vy': float(va[1]),
        'chassis_ax': float(aa[0]), 'chassis_ay': float(aa[1]),
        'knee_speed': 2*velocity, 'knee_accel': 2*accel,
        'upper_speed': -velocity, 'lower_speed': velocity,
        'upper_accel': -accel, 'lower_accel': accel,
        'spring_tension': elastic+damper, 'spring_length': length,
        'spring_elastic_tension': elastic, 'spring_damper_tension': damper,
        'spring_knee_moment': cross(E-B, fs),
        'actuator_torque': torque, 'actuator_command': raw,
        'guide_link_torque': guide, 'guide_hip_reaction': -2*guide,
        'stop_knee_torque': 0., 'wheel_external_moment': 0.,
        'wheel_drive_reaction': wheel_reaction, 'wheel_drive_check': 0.,
        'wheel_speed': velocity if c['wheel_drive_locked'] else 0.,
        'wheel_accel': accel if c['wheel_drive_locked'] else 0.,
        'hip_mount_fx': float(-f1[0]-fs[0]), 'hip_mount_fy': float(-f1[1]-fs[1]),
        'pin_error': 0., 'phase_error': 0., 'reaction_check': 0., 'angular_check': angular_error,
        'position_command': z, 'position_actual': z, 'position_actual_mm': z*1000,
        'position_error': 0., 'position_velocity_command': zv, 'position_accel_command': za,
        'ref_Fy_horizontal': float(F[0]), 'ref_Fz_vertical': float(F[1]),
        'ref_By_horizontal': float(knee_load[0]), 'ref_Bz_vertical': float(knee_load[1]),
        'ref_Min_wheel_moment': Min, 'ref_Mact_knee_moment': Mact,
        'ref_Br': float(np.linalg.norm(knee_load)),
        'ref_Min_contact_moment': Min+F[0]*c['radius'],
        'ref_wheel_radius_moment': float(F[0]*c['radius']),
        'check_contact_moment_Nm': Min+F[0]*c['radius']-cross(C-B+np.array([0., -c['radius']]), F),
        'check_lower_moment_Nm': Min-lower_cross, 'check_upper_moment_Nm': Mact-upper_cross,
        'check_lower_balance_Nm': lower_total-lower_inertia,
        'check_upper_balance_Nm': upper_total-upper_inertia,
        'check_Br_N': 0.,
        'kinetic_energy_J': kinetic, 'potential_energy_J': float(potential),
        'mechanical_energy_J': float(kinetic+potential),
        'driver_power_W': float(driver@vc), 'bias_power_W': float(external@vc),
        'actuator_power_W': 2*torque*velocity,
        'dissipation_power_W': c['damping']*(J*velocity)**2,
        'total_mass_kg': total_mass,
    }
    for index, (force, vel, acc) in enumerate(((f1, va, aa), (f2, vb, ab), (f3, vc, ac)), 1):
        row.update({f'j{index}_fx': float(force[0]), f'j{index}_fy': float(force[1]),
                    f'j{index}_force': float(np.linalg.norm(force)),
                    f'j{index}_vx': float(vel[0]), f'j{index}_vy': float(vel[1]),
                    f'j{index}_ax': float(acc[0]), f'j{index}_ay': float(acc[1])})
    row = {key: float(value) for key, value in row.items()}
    frame = {'t': float(t), 'hip': A.tolist(), 'knee': B.tolist(),
             'hub': C.tolist(), 'tip': E.tolist(), 'upper_angle': -q,
             'lower_angle': q-math.pi, 'position_target': C.tolist(), 'debug_draw': []}
    return row, frame


def simulate_math(values=None, *, rtol=1e-9, atol=1e-11, max_step=None):
    """Integrate the scalar ODE; stop events end a run before an unmodelled impact."""
    c = config(values)
    p = parameters(c)
    if not (math.isfinite(rtol) and math.isfinite(atol) and 0 < rtol < 1 and 0 < atol < 1):
        raise ValueError('Solver tolerances must be finite, positive and below one.')
    max_step = min(.01, c['dt']*4) if max_step is None else max_step
    if not math.isfinite(max_step) or max_step <= 0:
        raise ValueError('Solver maximum step must be finite and positive.')

    def lower_stop(t, state):
        return state[0]-math.radians(c['theta_min'])

    def upper_stop(t, state):
        return math.radians(c['theta_max'])-state[0]

    lower_stop.terminal = upper_stop.terminal = True
    lower_stop.direction = upper_stop.direction = -1
    solution = solve_ivp(lambda t, state: derivative(t, state, c, p),
                         (0., c['duration']), (p['q0'], 0.), method='DOP853',
                         rtol=rtol, atol=atol, max_step=max_step, dense_output=True,
                         events=(lower_stop, upper_stop))
    if not solution.success:
        raise ValueError('SciPy integration failed: '+solution.message)
    end = float(solution.t[-1])
    times = np.arange(1, math.floor(end/c['dt']+1e-10)+1)*c['dt']
    if not len(times) or end-times[-1] > 1e-9:
        times = np.append(times, end)
    states = solution.sol(times)
    rows, frames = [], []
    frame_stride = max(1, math.ceil(1/(120*c['dt'])))
    for index, (t, q, velocity) in enumerate(zip(times, states[0], states[1])):
        row, frame = observe(float(t), float(q), float(velocity), c, p)
        if not all(math.isfinite(value) for value in row.values()):
            raise ValueError('Non-finite mathematical model state.')
        rows.append(row)
        if index % frame_stride == 0 or index == len(times)-1:
            frame['index'] = index
            frames.append(frame)
    warnings = []
    stop_event = None
    if solution.status == 1:
        name = 'lower' if len(solution.t_events[0]) else 'upper'
        stop_event = {'limit': name, 't_s': end, 'theta_deg': rows[-1]['theta_deg']}
        warnings.append(f'{name.capitalize()} travel limit reached at {end:.6g} s. Run ends before impact; stop/contact forces are not modelled.')
    clipped = sum(abs(row['actuator_torque']-row['actuator_command']) > 1e-9 for row in rows)
    if clipped:
        warnings.append(f'Knee actuator clipped to its torque limit in {clipped} output samples.')
    if any(row['driver_force'] < -.1 for row in rows):
        warnings.append('Prescribed support requires downward/tensile wheel force during part of the run; unilateral ground contact could be lost.')
    keys = ['j1_force', 'j2_force', 'j3_force', 'spring_tension', 'actuator_torque',
            'guide_hip_reaction', 'stop_knee_torque', 'driver_force', 'hub_vy', 'hub_ay',
            'chassis_vy', 'chassis_ay', 'knee_speed', 'knee_accel']
    peaks = {key: {'value': max(rows, key=lambda row: abs(row[key]))[key],
                   't': max(rows, key=lambda row: abs(row[key]))['t']} for key in keys}
    checks = {key: max(abs(row[key]) for row in rows) for key in
              ('check_lower_moment_Nm', 'check_contact_moment_Nm', 'check_upper_moment_Nm',
               'check_lower_balance_Nm', 'check_upper_balance_Nm', 'check_Br_N',
               'wheel_drive_check', 'driver_check')}
    initial, _ = observe(0., p['q0'], 0., c, p)
    ts = np.array([0.]+[r['t'] for r in rows])
    power = np.array([r['driver_power_W']+r['bias_power_W']+r['actuator_power_W']-r['dissipation_power_W']
                      for r in [initial]+rows])
    energy_error = rows[-1]['mechanical_energy_J']-initial['mechanical_energy_J']-float(np.trapezoid(power, ts))
    return {
        'backend': 'math', 'engine': f'SciPy {scipy.__version__} / DOP853', 'config': c,
        'actual_rest_length': p['rest'], 'position_origin': [0., 0.],
        'model': {'renderer': 'independent kinematics (not Pymunk debug draw)',
                  'bodies': [], 'constraints': [], 'shapes': [], 'debug_scale': 600.},
        'rows': rows, 'frames': frames, 'peaks': peaks,
        'equation_reference': {'status': 'Independent scalar energy model; no explicit belt-span bearing forces.',
                              'visible_equations': [
                                  'h_chassis = z_wheel + 2 L sin(theta)',
                                  's^2 = L^2 + e^2 + 2 L e cos(2 theta)',
                                  'J = ds/dtheta = -2 L e sin(2 theta)/s',
                                  'M theta_ddot + 0.5 M_prime theta_dot^2 + S cos(theta)(g + z_ddot) = -[k(s-s0)+c J theta_dot] J + 2 tau_knee',
                                  'S = 1.5 m_upper L + 0.5 m_lower (L+e) + 2 m_chassis L',
                                  'M = I_upper + I_lower [+ I_wheel if locked] + m_upper[(L/2)^2 sin^2(theta)+(3L/2)^2 cos^2(theta)] + m_lower[(L+e)/2]^2 + 4 m_chassis L^2 cos^2(theta)',
                                  'Joint forces: individual body momentum balances; guide torque: independent upper/lower angular balances.']},
        'equation_check_errors': checks,
        'diagnostics': {'max_pin_error_m': 0., 'max_guide_error_rad': 0.,
                        'max_force_check_N': 0.,
                        'max_torque_check_Nm': max(row['angular_check'] for row in rows),
                        'input_integral': float(np.trapezoid([0.]+[r['input'] for r in rows], ts)),
                        'input_unit': 'm', 'input_integral_unit': 'm s',
                        'max_position_error_m': 0., 'stop_steps': 0, 'clipped_steps': clipped,
                        'energy_balance_error_J': energy_error,
                        'nfev': int(solution.nfev), 'actual_duration_s': end,
                        'zero_residual_note': 'Kinematics are imposed analytically; zeros are not rigid-body solver impulse checks.'},
        'solver': {'method': 'DOP853', 'rtol': rtol, 'atol': atol,
                   'max_step_s': max_step, 'output_step_s': c['dt'], 'stop_event': stop_event},
        'warnings': warnings,
        'scope': 'Independent Python/SciPy scalar-energy model, exact equal-link 2:1 guide, lower-link extension spring, floating chassis with pitch held, and prescribed bilateral wheel height. Smooth C2 input only. Reactions are instantaneous Newton-Euler loads; mathematical support tracks exactly. Stops terminate the run before impact. No tire contact, belt elasticity, stress or hardware calibration. Legacy amplitude/impulse, fixed-hip preload and Pymunk iterations are preserved in profiles but do not drive this model.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    values = json.loads(args.config.read_text(encoding='utf-8')) if args.config else None
    if values and 'config' in values:
        values = values['config']
    result = simulate_math(values)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, allow_nan=False), encoding='utf-8')
    print(f"{len(result['rows'])} samples; {result['engine']}; warnings: {len(result['warnings'])}")


if __name__ == '__main__':
    main()
