"""Independent gravity-balanced lever study and actual Pymunk counterpart.

Invocation: simulate(config, backend='math'|'pymunk'), or python counterbalance.py
--backend math --output run.json. Live viewer: config/build/drive/Space.step/
telemetry/frame. Inputs: m, kg, N/m, N s/m, s; UI angles in degrees, internals
radians. Outputs: JSON rows, geometry/debug frames, reactions and energy checks.
Requires SciPy; Pymunk is imported only by physical build/telemetry/frame paths.
O=(0,0), A=(0,H), B=R(cos(theta),sin(theta)), payload C=L(cos(theta),sin(theta)).
Zero-effective-free-length T=k*d emulates a physical coil length l_phys+d;
it does not assert that an ordinary nonzero-free-length coil has this law.
Uniform lever plus rigid point payload form one exact aggregate rigid body.
No rope friction, pulley mass, contact, coil solid height, structural stress or
hardware calibration. Free travel ends at bounds before modelling an impact.
Prescribed motion uses an ideal speed motor: physical angle tracking and sharp
load peaks converge with timestep, rather than teleporting a body to a pose.
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


DEFAULTS = {
    'length': .4, 'spring_radius': .2, 'anchor_height': .2,
    'payload_mass': 2., 'lever_mass': .4, 'gravity': 9.80665,
    'stiffness': 215.7463, 'stiffness_auto': True,
    'law': 'zero_effective', 'effective_free_length': .15,
    'physical_free_length': .15, 'damping': 0., 'mode': 'prescribed',
    'initial_angle_deg': 30., 'initial_speed_deg': 0.,
    'angle_amplitude_deg': 30., 'theta_min_deg': -80., 'theta_max_deg': 80.,
    'wave': 'step', 'start': .5, 'rise': .25, 'fall': .25,
    'period': 1.5, 'duty': .5, 'pulse_width': .7,
    'duration': 2., 'dt': .001, 'iterations': 80,
}


def config(values=None):
    """Validate a standalone profile and resolve explicit automatic spring rate."""
    c = deepcopy(DEFAULTS)
    if values is not None:
        if not isinstance(values, dict):
            raise ValueError('Counterbalance configuration must be an object.')
        unknown = set(values)-set(c)
        if unknown:
            raise ValueError('Unknown counterbalance fields: '+', '.join(sorted(unknown)))
        c.update(values)
    for key, default in DEFAULTS.items():
        value = c[key]
        if isinstance(default, bool):
            if not isinstance(value, bool):
                raise ValueError(f'{key} must be boolean.')
        elif isinstance(default, (float, int)):
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError(f'{key} must be finite.')
    limits = {'length': (.02, 3.), 'spring_radius': (.005, 3.),
              'anchor_height': (.005, 3.), 'payload_mass': (0., 100.),
              'lever_mass': (.001, 100.), 'gravity': (0., 20.),
              'stiffness': (0., 100000.), 'damping': (0., 2000.),
              'effective_free_length': (0., 5.), 'physical_free_length': (.001, 5.),
              'duration': (.1, 20.), 'dt': (.00025, .004),
              'start': (0., 20.), 'rise': (0., 5.), 'fall': (0., 5.),
              'period': (.02, 10.), 'duty': (.01, .99), 'pulse_width': (.001, 5.),
              'initial_speed_deg': (-720., 720.), 'angle_amplitude_deg': (-300., 300.),
              'iterations': (20, 300)}
    for key, (lo, hi) in limits.items():
        if not lo <= c[key] <= hi:
            raise ValueError(f'{key} must lie between {lo} and {hi} (SI unless labelled degrees).')
    if c['spring_radius'] > c['length']:
        raise ValueError('Spring attachment radius must fit on the lever.')
    if not -179 <= c['theta_min_deg'] < c['initial_angle_deg'] < c['theta_max_deg'] <= 179:
        raise ValueError('Use -179 <= minimum < initial angle < maximum <= 179 degrees.')
    if c['iterations'] != int(c['iterations']):
        raise ValueError('Iterations must be an integer.')
    if c['duration']/c['dt'] > 30000:
        raise ValueError('Limit each run to 30,000 samples.')
    if c['law'] not in ('zero_effective', 'ordinary'):
        raise ValueError('Choose zero_effective or ordinary spring law.')
    if c['mode'] not in ('prescribed', 'free'):
        raise ValueError('Choose prescribed angle or free lever dynamics.')
    if c['wave'] not in ('step', 'square', 'pulse'):
        raise ValueError('Choose a finite angle step, square wave or pulse.')
    if c['mode'] == 'prescribed':
        endpoint = c['initial_angle_deg']+c['angle_amplitude_deg']
        if not c['theta_min_deg'] < endpoint < c['theta_max_deg']:
            raise ValueError('Prescribed angle exceeds the travel bounds.')
        if c['rise'] < 4*c['dt'] or c['wave'] != 'step' and c['fall'] < 4*c['dt']:
            raise ValueError('Prescribed motion needs finite rise/fall of at least four timesteps.')
        if c['initial_speed_deg'] != 0.:
            raise ValueError('Prescribed angle begins at rest; initial_speed_deg applies to free mode.')
        lo, hi = sorted((c['initial_angle_deg'], endpoint))
        if lo <= 90. <= hi and abs(c['anchor_height']-c['spring_radius']) < 1e-8:
            raise ValueError('The prescribed path crosses a zero-length spring span; change H/R or angle range.')
    width = c['period']*c['duty'] if c['wave'] == 'square' else c['pulse_width']
    if c['wave'] != 'step' and c['rise']+c['fall'] > width+1e-12:
        raise ValueError('Rise and fall must fit inside wave on-time.')
    if c['stiffness_auto']:
        c['stiffness'] = c['gravity']*c['length']*(c['payload_mass']+.5*c['lever_mass'])/(c['anchor_height']*c['spring_radius'])
        if c['stiffness'] > 100000.:
            raise ValueError('Automatic rate exceeds the study stiffness range; change geometry or load.')
    geometry(math.radians(c['initial_angle_deg']), c)
    return c


def parameters(c):
    """Exact aggregate COM, inertia and required constant support for the lever."""
    mass = c['payload_mass']+c['lever_mass']
    first = c['length']*(c['payload_mass']+.5*c['lever_mass'])
    com = first/mass
    inertia = c['length']**2*(c['payload_mass']+c['lever_mass']/3.)
    return {'mass': mass, 'first_moment': first, 'com_radius': com,
            'pivot_inertia': inertia, 'com_inertia': inertia-mass*com*com,
            'required_support_N': c['gravity']*first/c['length'],
            'zero_length_rate_N_m': c['gravity']*first/(c['anchor_height']*c['spring_radius'])}


def geometry(theta, c):
    """Ideal geometry and d(span)/d(theta), with theta from horizontal in radians."""
    L, R, H = c['length'], c['spring_radius'], c['anchor_height']
    sn, cs = math.sin(theta), math.cos(theta)
    span = math.hypot(R*cs, H-R*sn)
    if span < 1e-9:
        raise ValueError('Spring span is singular (attachment meets anchor).')
    return {'pivot': [0., 0.], 'anchor': [0., H], 'attach': [R*cs, R*sn],
            'tip': [L*cs, L*sn], 'span': span,
            'span_jacobian': -H*R*cs/span,
            'direction': [-R*cs/span, (H-R*sn)/span]}


def spring_state(span, span_speed, c):
    """Tension-only extension law; zero-effective routing reverses no power sign."""
    free = 0. if c['law'] == 'zero_effective' else c['effective_free_length']
    stretch = max(0., span-free)
    engaged = span >= free
    elastic = c['stiffness']*stretch
    tension = max(0., elastic+c['damping']*span_speed) if engaged else 0.
    damper = tension-elastic
    return {'spring_force_N': tension, 'spring_elastic_N': elastic,
            'spring_damper_N': damper, 'span_m': span, 'span_speed_m_s': span_speed,
            'coil_length_m': c['physical_free_length']+span if c['law'] == 'zero_effective' else max(span, free),
            'coil_extension_m': stretch, 'spring_energy_J': .5*c['stiffness']*stretch*stretch,
            'dissipation_W': damper*span_speed, 'engaged': float(engaged),
            'effective_free_length_m': free}


def forces(theta, speed, c):
    """Independent scalar force, virtual-work moment and gravitational moment."""
    geom = geometry(theta, c)
    state = spring_state(geom['span'], geom['span_jacobian']*speed, c)
    Fx, Fy = (state['spring_force_N']*x for x in geom['direction'])
    spring_moment = -state['spring_force_N']*geom['span_jacobian']
    gravity_moment = -c['gravity']*parameters(c)['first_moment']*math.cos(theta)
    nonsingular = abs(c['length']*math.cos(theta)) > 1e-8
    equivalent = state['spring_force_N']*c['anchor_height']*c['spring_radius']/(c['length']*geom['span']) if nonsingular else 0.
    elastic_equivalent = state['spring_elastic_N']*c['anchor_height']*c['spring_radius']/(c['length']*geom['span']) if nonsingular else 0.
    return {**state, 'spring_fx': Fx, 'spring_fy': Fy, 'spring_moment_Nm': spring_moment,
            'gravity_moment_Nm': gravity_moment, 'net_passive_moment_Nm': spring_moment+gravity_moment,
            'equivalent_support_N': equivalent, 'elastic_equivalent_support_N': elastic_equivalent,
            'equivalent_defined': float(nonsingular), 'geometry': geom}


def angle_state(t, c):
    """Prescribed C2 angle step/square/pulse, outputs radians/rad s/rad s2."""
    delta, speed, accel = position_state(t, dict(c, position_amplitude=math.radians(c['angle_amplitude_deg']), ramp_shape='quintic'))
    return math.radians(c['initial_angle_deg'])+delta, speed, accel


def math_observe(t, theta, speed, accel, c):
    p = parameters(c)
    state = forces(theta, speed, c)
    sn, cs = math.sin(theta), math.cos(theta)
    ax = p['com_radius']*(-cs*speed*speed-sn*accel)
    ay = p['com_radius']*(-sn*speed*speed+cs*accel)
    joint_fx = p['mass']*ax-state['spring_fx']
    joint_fy = p['mass']*(ay+c['gravity'])-state['spring_fy']
    driver = p['pivot_inertia']*accel-state['net_passive_moment_Nm'] if c['mode'] == 'prescribed' else 0.
    command = angle_state(t, c)[0] if c['mode'] == 'prescribed' else math.radians(c['initial_angle_deg'])
    energy = .5*p['pivot_inertia']*speed*speed+c['gravity']*p['first_moment']*sn+state['spring_energy_J']
    return {**{key: value for key, value in state.items() if key != 'geometry'},
            't': t, 'theta_deg': math.degrees(theta), 'angular_velocity_rad_s': speed,
            'angular_acceleration_rad_s2': accel, 'joint_fx': joint_fx, 'joint_fy': joint_fy,
            'joint_force_N': math.hypot(joint_fx, joint_fy), 'driver_torque_Nm': driver,
            'lever_reaction_moment_Nm': -driver, 'angle_command_deg': math.degrees(command),
            'angle_error_deg': math.degrees(theta-command) if c['mode'] == 'prescribed' else 0.,
            'com_vx': -p['com_radius']*sn*speed, 'com_vy': p['com_radius']*cs*speed,
            'com_ax': ax, 'com_ay': ay,
            'tip_velocity_y': c['length']*cs*speed,
            'tip_acceleration_y': c['length']*(cs*accel-sn*speed*speed),
            'mechanical_energy_J': energy, 'driver_power_W': driver*speed,
            'force_check_N': 0., 'moment_check_Nm': 0., 'pin_error_m': 0.}


def build(c):
    """Build one dynamic aggregate lever, fixed pivot and optional actual motor."""
    import pymunk
    p = parameters(c)
    theta = math.radians(c['initial_angle_deg'])
    space = pymunk.Space()
    space.gravity = (0., -c['gravity'])
    space.iterations = int(c['iterations'])
    lever = pymunk.Body(p['mass'], p['com_inertia'])
    lever.position = p['com_radius']*math.cos(theta), p['com_radius']*math.sin(theta)
    lever.angle = theta
    lever.angular_velocity = math.radians(c['initial_speed_deg'])
    lever.velocity = (-p['com_radius']*math.sin(theta)*lever.angular_velocity,
                      p['com_radius']*math.cos(theta)*lever.angular_velocity)
    pivot_joint = pymunk.PivotJoint(space.static_body, lever, (0., 0.), (-p['com_radius'], 0.))
    motor = pymunk.SimpleMotor(space.static_body, lever, 0.) if c['mode'] == 'prescribed' else None
    local = {'pivot': (-p['com_radius'], 0.), 'attach': (c['spring_radius']-p['com_radius'], 0.),
             'tip': (c['length']-p['com_radius'], 0.)}
    rod = pymunk.Segment(lever, local['pivot'], local['tip'], .009)
    payload = pymunk.Circle(lever, .04, local['tip'])
    mount = pymunk.Circle(space.static_body, .012, (0., c['anchor_height']))
    for shape, color in ((rod, (39, 174, 96, 255)), (payload, (241, 196, 15, 200)), (mount, (160, 160, 160, 255))):
        shape.sensor = True
        shape.color = color
    space.add(lever, pivot_joint, rod, payload, mount)
    if motor:
        space.add(motor)
    return {'space': space, 'lever': lever, 'pivot_joint': pivot_joint, 'motor': motor,
            'anchors': local, 'parameters': p, 'spring_state': None,
            'shapes': {'lever': rod, 'payload': payload, 'anchor': mount}}


def physical_geometry(model, c):
    """Read transformed mount geometry and extension speed from actual bodies."""
    body = model['lever']
    actual = {key: list(body.local_to_world(local)) for key, local in model['anchors'].items()}
    anchor = np.array([0., c['anchor_height']])
    delta = anchor-np.array(actual['attach'])
    span = float(np.linalg.norm(delta))
    if span < 1e-9:
        raise ValueError('Actual spring attachment meets its anchor; span is singular.')
    n = delta/span
    speed = -float(np.dot(n, body.velocity_at_local_point(model['anchors']['attach'])))
    return {**actual, 'anchor': anchor.tolist(), 'span': span,
            'span_speed': speed, 'direction': n.tolist()}


def drive(model, c, t, dt):
    """Apply point spring force and optional interval-average angular-speed input."""
    from pymunk import Vec2d
    geom = physical_geometry(model, c)
    state = spring_state(geom['span'], geom['span_speed'], c)
    body = model['lever']
    model['old_tip_velocity'] = tuple(body.velocity_at_local_point(model['anchors']['tip']))
    model['applied_angle'] = body.angle
    force = Vec2d(*geom['direction'])*state['spring_force_N']
    body.apply_force_at_world_point(force, geom['attach'])
    state.update(spring_fx=force.x, spring_fy=force.y,
                 spring_com_moment_Nm=(Vec2d(*geom['attach'])-body.position).cross(force),
                 spring_moment_Nm=Vec2d(*geom['attach']).cross(force),
                 gravity_moment_Nm=-model['parameters']['mass']*c['gravity']*body.position.x,
                 geometry=geom)
    state['net_passive_moment_Nm'] = state['spring_moment_Nm']+state['gravity_moment_Nm']
    model['spring_state'] = state
    if model['motor']:
        q0, _, _ = angle_state(t, c)
        q1, _, _ = angle_state(t+dt, c)
        # Chipmunk SimpleMotor rate is omega_a-omega_b.
        model['motor'].rate = -(q1-q0)/dt
    return state


def telemetry(model, c, t, old_velocity, old_spin, dt):
    """Post-step signed forces/torque recovered from independent body balances."""
    from pymunk import Vec2d
    body, p = model['lever'], model['parameters']
    accel = (body.velocity-Vec2d(*old_velocity))/dt
    angular_accel = (body.angular_velocity-old_spin)/dt
    state = model['spring_state']
    force = Vec2d(state['spring_fx'], state['spring_fy'])
    reaction = p['mass']*(accel-Vec2d(0., -c['gravity']))-force
    # Pymunk solves impulses at the post-position-update configuration.
    pivot = body.local_to_world(model['anchors']['pivot'])
    pin_moment = (pivot-body.position).cross(reaction)
    motor_torque = p['com_inertia']*angular_accel-pin_moment-state['spring_com_moment_Nm']
    motor_error = abs(abs(motor_torque)-model['motor'].impulse/dt) if model['motor'] else abs(motor_torque)
    current = physical_geometry(model, c)
    current_law = spring_state(current['span'], current['span_speed'], c)
    energy = (.5*p['mass']*body.velocity.length_squared+.5*p['com_inertia']*body.angular_velocity**2
              +p['mass']*c['gravity']*body.position.y+current_law['spring_energy_J'])
    theta = body.angle
    angular_row = math_observe(t, theta, body.angular_velocity, angular_accel, c)
    tip_velocity = body.velocity_at_local_point(model['anchors']['tip'])
    tip_accel = (tip_velocity-Vec2d(*model['old_tip_velocity']))/dt
    equivalent_defined = abs(c['length']*math.cos(model['applied_angle'])) > 1e-8
    support_factor = c['anchor_height']*c['spring_radius']/(c['length']*state['span_m']) if equivalent_defined else 0.
    return {**angular_row, **{key: value for key, value in state.items() if key not in ('geometry', 'spring_com_moment_Nm')},
            'joint_fx': reaction.x, 'joint_fy': reaction.y, 'joint_force_N': model['pivot_joint'].impulse/dt,
            'driver_torque_Nm': motor_torque if model['motor'] else 0.,
            'lever_reaction_moment_Nm': -motor_torque if model['motor'] else 0.,
            'com_vx': body.velocity.x, 'com_vy': body.velocity.y,
            'com_ax': accel.x, 'com_ay': accel.y,
            'tip_velocity_y': tip_velocity.y, 'tip_acceleration_y': tip_accel.y,
            'equivalent_support_N': state['spring_force_N']*support_factor,
            'elastic_equivalent_support_N': state['spring_elastic_N']*support_factor,
            'equivalent_defined': float(equivalent_defined),
            'mechanical_energy_J': energy,
            'driver_power_W': motor_torque*body.angular_velocity if model['motor'] else 0.,
            'force_check_N': abs(reaction.length-model['pivot_joint'].impulse/dt),
            'moment_check_Nm': motor_error, 'pin_error_m': pivot.length}


def frame(model, c, t):
    """Actual physics geometry and Space.debug_draw; no fabricated body rendering."""
    from debug_view import capture
    geom = physical_geometry(model, c)
    return {**{key: geom[key] for key in ('pivot', 'anchor', 'attach', 'tip')},
            't': t, 'theta_rad': model['lever'].angle, 'debug_draw': capture(model['space'])}


def describe(model):
    """Serializable description of actual engine body, joint, motor and shapes."""
    return {'renderer': 'pymunk.Space.debug_draw callbacks', 'debug_scale': 600.,
            'bodies': [{'name': 'lever_and_payload', 'class': type(model['lever']).__name__,
                        'type': 'dynamic', 'mass_kg': model['lever'].mass,
                        'inertia_kg_m2': model['lever'].moment}],
            'constraints': [{'name': 'pivot_joint', 'class': type(model['pivot_joint']).__name__}]
                           + ([{'name': 'motor', 'class': type(model['motor']).__name__}] if model['motor'] else []),
            'shapes': [{'name': key, 'class': type(shape).__name__, 'sensor': shape.sensor}
                       for key, shape in model['shapes'].items()]}


def static_screen(c, samples=161):
    """Quasistatic sweep: extension tension, equivalent support and hold torque.

    Uses zero velocity/acceleration even when the run's mode is free. Singular
    spring spans are omitted; equivalent support at a vertical lever is flagged
    undefined rather than dividing a zero moment by a zero vertical lever arm.
    """
    if not isinstance(samples, int) or not 2 <= samples <= 2001:
        raise ValueError('Static sweep needs 2 to 2001 samples.')
    result = []
    for angle in np.linspace(c['theta_min_deg'], c['theta_max_deg'], samples):
        try:
            row = math_observe(0., math.radians(float(angle)), 0., 0., dict(c, mode='prescribed'))
        except ValueError as error:
            if 'singular' not in str(error):
                raise
            continue
        row['required_support_N'] = parameters(c)['required_support_N']
        row['hold_torque_Nm'] = -row['net_passive_moment_Nm']
        result.append(row)
    return result


def simulate(values=None, backend='pymunk'):
    """Run independent SciPy or actual Pymunk and return portable study data."""
    c, rows, frames = config(values), [], []
    if backend not in ('math', 'pymunk'):
        raise ValueError('Counterbalance backend must be math or pymunk.')
    p = parameters(c)
    stride = max(1, math.ceil(1/(120*c['dt'])))
    event = None
    solution = None
    if backend == 'math':
        def rhs(t, state):
            return state[1], forces(state[0], state[1], c)['net_passive_moment_Nm']/p['pivot_inertia']
        if c['mode'] == 'free':
            def lower(t, state):
                return state[0]-math.radians(c['theta_min_deg'])
            def upper(t, state):
                return math.radians(c['theta_max_deg'])-state[0]
            lower.terminal = upper.terminal = True
            lower.direction = upper.direction = -1
            solution = solve_ivp(rhs, (0., c['duration']),
                                 (math.radians(c['initial_angle_deg']), math.radians(c['initial_speed_deg'])),
                                 method='DOP853', rtol=1e-10, atol=1e-12,
                                 max_step=min(.01, c['dt']*4), dense_output=True, events=(lower, upper))
            if not solution.success:
                raise ValueError('SciPy counterbalance solve failed: '+solution.message)
            end = float(solution.t[-1])
            if end < c['duration']-1e-9:
                event = {'t': end, 'theta_deg': math.degrees(solution.y[0, -1]), 'kind': 'travel_limit'}
        else:
            end = c['duration']
        times = np.arange(c['dt'], end+1e-12, c['dt'])
        if event and (not len(times) or end-times[-1] > 1e-9):
            times = np.append(times, end)
        for i, t in enumerate(times):
            if c['mode'] == 'prescribed':
                q, speed, accel = angle_state(float(t), c)
            else:
                q, speed = solution.sol(t)
                accel = rhs(t, (q, speed))[1]
            rows.append(math_observe(float(t), float(q), float(speed), float(accel), c))
            if i % stride == 0 or i == len(times)-1:
                frames.append({**{key: geometry(q, c)[key] for key in ('pivot', 'anchor', 'attach', 'tip')},
                               't': float(t), 'theta_rad': float(q), 'renderer': 'independent analytical geometry'})
        engine = f'SciPy {scipy.__version__} / DOP853' if solution else 'Independent analytical prescribed-angle dynamics'
        model_info = {'renderer': 'independent analytical geometry', 'bodies': [], 'constraints': [], 'shapes': []}
    else:
        import pymunk
        model = build(c)
        model_info = describe(model)
        for i in range(math.ceil(c['duration']/c['dt'])):
            t, dt = i*c['dt'], min(c['dt'], c['duration']-i*c['dt'])
            old_velocity = tuple(model['lever'].velocity)
            old_spin = model['lever'].angular_velocity
            drive(model, c, t, dt)
            model['space'].step(dt)
            row = telemetry(model, c, t+dt, old_velocity, old_spin, dt)
            rows.append(row)
            if i % stride == 0 or i == math.ceil(c['duration']/c['dt'])-1:
                frames.append(frame(model, c, t+dt))
            if c['mode'] == 'free' and not c['theta_min_deg'] < row['theta_deg'] < c['theta_max_deg']:
                event = {'t': row['t'], 'theta_deg': row['theta_deg'], 'kind': 'travel_limit',
                         'resolution_s': dt}
                if frames[-1]['t'] != row['t']:
                    frames.append(frame(model, c, row['t']))
                break
        engine = f'Pymunk {pymunk.version}'
    if not rows or any(not all(math.isfinite(value) for value in row.values()) for row in rows):
        raise ValueError('Counterbalance produced missing or non-finite state.')
    initial_q = math.radians(c['initial_angle_deg'])
    initial_v = math.radians(c['initial_speed_deg'])
    initial_a = forces(initial_q, initial_v, c)['net_passive_moment_Nm']/p['pivot_inertia'] if c['mode'] == 'free' else 0.
    initial = math_observe(0., initial_q, initial_v, initial_a, c)
    ts = [0.]+[row['t'] for row in rows]
    power = [row['driver_power_W']-row['dissipation_W'] for row in [initial]+rows]
    energy_error = rows[-1]['mechanical_energy_J']-initial['mechanical_energy_J']-float(np.trapezoid(power, ts))
    warnings = ['Illustrative standalone lever; dimensions and spring implementation require hardware confirmation.']
    if c['law'] == 'ordinary' and c['effective_free_length'] > 0.:
        warnings.append('An ordinary coil with finite effective free length does not provide constant equivalent vertical support; automatic rate is the zero-length reference, not an exact ordinary-coil balance.')
    if backend == 'pymunk':
        warnings.append('Spring point forces and speed-motor motion use finite timesteps. Refine dt for angle tracking, energy and peak loads; the body is never teleported.')
    if event:
        warnings.append('Free motion ended at a travel bound; stop impact is not modelled. Pymunk detects crossing after one finite step.')
    keys = ('spring_force_N', 'equivalent_support_N', 'joint_force_N', 'driver_torque_Nm',
            'angular_velocity_rad_s', 'angular_acceleration_rad_s2', 'tip_acceleration_y')
    peaks = {key: {'value': max(rows, key=lambda row: abs(row[key]))[key],
                   't': max(rows, key=lambda row: abs(row[key]))['t']} for key in keys}
    return {'study': 'gravity_counterbalance', 'backend': 'counterbalance_'+backend, 'engine': engine,
            'config': c, 'parameters': p, 'rows': rows, 'frames': frames, 'model': model_info,
            'static_rows': static_screen(c), 'peaks': peaks, 'warnings': warnings,
            'diagnostics': {'max_pin_error_m': max(row['pin_error_m'] for row in rows),
                            'max_force_check_N': max(row['force_check_N'] for row in rows),
                            'max_moment_check_Nm': max(row['moment_check_Nm'] for row in rows),
                            'max_angle_error_deg': max(abs(row['angle_error_deg']) for row in rows),
                            'energy_balance_error_J': energy_error, 'stop_event': event,
                            'actual_duration_s': rows[-1]['t']},
            'equations': ['d²=H²+R²−2HR sin(theta)', 'T=k d (zero effective free length)',
                          'M_spring=T HR cos(theta)/d', 'F_equiv=M_spring/(L cos(theta))=kHR/L',
                          'kHR=gL(m_payload+m_lever/2)',
                          'I_pivot theta_ddot=M_spring−gL(m_payload+m_lever/2)cos(theta)+M_driver'],
            'scope': 'Standalone ideal lever and point payload, fixed pivot, massless ideal zero-effective-length routing or ordinary tension-only spring. Zero-length equivalent support is constant; spring tension itself varies. Free dynamics has no holding motor; prescribed mode uses an unlimited ideal angular-speed motor. Physical force/coil samples describe the applied pre-step spring, with post-step body motion and independent momentum checks; equivalent support uses the nominal analytical lever geometry, and physical tip velocity/acceleration use actual point velocity differences. Undefined equivalent support at vertical lever is flagged. No wheel-leg adaptation, contacts, pulley friction, stress or impact model.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--backend', choices=('math', 'pymunk'), default='math')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    values = json.loads(args.config.read_text(encoding='utf-8')) if args.config else None
    if values and 'config' in values:
        values = values['config']
    result = simulate(values, args.backend)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, allow_nan=False), encoding='utf-8')
    print(f"{result['engine']}: {len(result['rows'])} samples; {len(result['warnings'])} scope warnings")


if __name__ == '__main__':
    main()
