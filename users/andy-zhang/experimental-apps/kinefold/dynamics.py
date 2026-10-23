"""Run Kinefold floating-chassis analytical and 2D Pymunk quarter models.

Usage: .venv/Scripts/python.exe dynamics.py --request-stdin, or --defaults.
JSON builder inputs use mm/deg/kg/N; run controls use seconds/Nm/kg m².
Outputs finite SI-energy/world-mm trajectories, reactions, events and diagnostics.
The wheel-height actuator is prescribed; xA/pitch are locked, A heaves freely.
Pymunk integrates a real m1 chassis body with a vertical groove; other masses
and inertias are exactly condensed through ideal kinematics, not separate rigid
link bodies. Exact square jumps are limited to massless undamped transmission.
No tire contact, collision, impact law, chassis pitch or hardware validation.
"""
import argparse
import json
import math
import sys

from dynamic_model import Model, R, defaults


def state_observation(model, t, q, v, side='right', actual=None):
    return model.observe(t, q, v, model.acceleration(q, v, t, side), actual, side)


def jump(model, t, q, v):
    """Exact massless transmission jump: real chassis h and hdot stay continuous."""
    before, _ = state_observation(model, t, q, v, 'left')
    h, hd, _ = model.chassis(t, q, v, side='left')
    new_q = model.q_from_chassis(t, h, 'right')
    new_v = -hd / model.sites(new_q)['6'][1][1]
    after, _ = state_observation(model, t, new_q, new_v, 'right')
    actuator = model.motor.joint_command(model.c['hipTorqueNm']) * (new_q - q)
    energy = after['energyJ'] - before['energyJ']
    event = dict(t=t, type='exact-square-jump', before=before, after=after,
                 inputJumpMm=after['appliedInputMm'] - before['appliedInputMm'],
                 theta2JumpDeg=(new_q - q) / R, energyJumpJ=energy,
                 actuatorWorkJumpJ=actuator, inputWorkJumpJ=energy - actuator,
                 chassisPositionJumpMm=after['chassisZMm'] - before['chassisZMm'],
                 chassisVelocityJumpMmS=after['chassisVelocityMmS'] - before['chassisVelocityMmS'],
                 angularVelocityAtJump='undefined; rows contain finite one-sided velocities',
                 inputReactionAtJump='no finite reaction assigned at the discontinuity')
    return new_q, new_v, actuator, energy - actuator, event


def powers(model, t, q, v, side='right'):
    a = model.acceleration(q, v, t, side)
    actuator = model.motor.joint_command(model.c['hipTorqueNm']) * v - model.c['dampingNms'] * v * v
    return actuator, model.reaction(t, q, v, a, side) * model.input(t, side)['velocity']


def finish_diagnostics(model, rows, diagnostics):
    initial = rows[0]['energyJ']
    diagnostics['maxWorkEnergyResidualJ'] = max(abs(r['energyJ'] - initial - r['actuatorDampingWorkJ'] - r['terrainWorkJ'] + r.get('motorFrictionLossJ', 0)) for r in rows)
    diagnostics['minimumInputReactionN'] = min(r['inputReactionN'] for r in rows)
    diagnostics['maximumInputReactionN'] = max(r['inputReactionN'] for r in rows)
    return diagnostics


def analytical(model):
    import numpy as np
    from scipy.integrate import solve_ivp
    c = model.c
    rows, frames, events = [], [], []
    state = [model.q0, c['initialVelocityDegS'] * R, 0., 0.]
    if model.motor_config_supplied:
        state.append(0.)
    start, evaluations, termination = 0., 0, 'duration'
    breaks = model.input_breaks()
    boundaries = sorted(set(breaks + [c['duration']]))

    def append(t, y, side='right'):
        q, v, wa, wi = (float(x) for x in y[:4])
        if q < model.lo - 1e-10 or q > model.hi + 1e-10:
            raise ValueError('Analytical output exceeded the working angle limits.')
        q = min(model.hi, max(model.lo, q))  # Roundoff at an event endpoint only.
        row, frame = state_observation(model, float(t), q, v, side)
        row.update(actuatorDampingWorkJ=wa, terrainWorkJ=wi, inputWorkJ=wi)
        if model.motor_config_supplied:
            row['motorFrictionLossJ'] = row['motorDissipatedJ'] = float(y[4])
        if rows and abs(rows[-1]['t'] - t) < 1e-11 and side != 'left' and rows[-1].get('eventSide') != 'before':
            rows[-1], frames[-1] = row, frame
        else:
            rows.append(row)
            frames.append(frame)
        return row

    # Initial pose is defined before any t=0 input jump.
    append(0, state, 'left' if 0 in breaks and model.exact_square else 'right')
    if 0 in breaks and model.exact_square:
        try:
            nq, nv, wa, wi, event = jump(model, 0, *state[:2])
            rows[-1]['eventSide'] = 'before'
            state = [nq, nv, wa, wi]
            if model.motor_config_supplied:
                state.append(0.)
            append(0, state)['eventSide'] = 'after'
            events.append(event)
        except ValueError:
            termination = 'input-jump-travel-limit'
    for end in boundaries:
        if termination != 'duration':
            break
        if end <= start + 1e-12:
            continue
        exact_end = model.exact_square and end in breaks
        def derivative(t, y):
            q, v = y[:2]
            side = 'left' if exact_end and t >= end - 1e-12 else 'right'
            a = model.acceleration(q, v, t, side)
            wa, wi = powers(model, t, q, v, side)
            derivatives = (v, a, wa, wi)
            if model.motor_config_supplied:
                derivatives += (model.motor.motor_state(q, v, 0)['motorLossPowerW'],)
            return derivatives
        def lower(t, y):
            return y[0] - model.lo
        def upper(t, y):
            return model.hi - y[0]
        lower.terminal = upper.terminal = True
        lower.direction = upper.direction = -1
        solution = solve_ivp(derivative, (start, end), state, method='DOP853', rtol=1e-9, atol=1e-11,
                             max_step=c['dt'], dense_output=True, events=(lower, upper))
        if not solution.success:
            raise ValueError(solution.message)
        evaluations += solution.nfev
        actual_end = float(solution.t[-1])
        times = np.arange(math.floor(start * c['outputHz'] + 1e-9) + 1,
                          math.floor(actual_end * c['outputHz'] + 1e-9) + 1) / c['outputHz']
        for t in times:
            if t < actual_end - 1e-10:
                append(float(t), solution.sol(float(t)))
        state = [float(x) for x in solution.y[:, -1]]
        append(actual_end, state, 'left' if exact_end else 'right')
        start = actual_end
        if solution.status == 1:
            termination = 'travel-limit'
            break
        if exact_end:
            try:
                nq, nv, wa, wi, event = jump(model, end, *state[:2])
            except ValueError:
                termination = 'input-jump-travel-limit'
                events.append(dict(t=end, type='input-jump-rejected', reason='New prescribed wheel height exceeds working travel; stopped at pre-jump state.'))
                break
            rows[-1]['eventSide'] = 'before'
            state = [nq, nv, state[2] + wa, state[3] + wi] + state[4:]
            append(end, state)['eventSide'] = 'after'
            events.append(event)
    diagnostics = dict(termination=termination, elapsedSeconds=rows[-1]['t'],
                       maxConstraintPositionErrorMm=0, maxConstraintAngleErrorDeg=0,
                       evaluations=int(evaluations), integrator='SciPy DOP853 / floating q equation with exact input-event restart',
                       frameSource='exact floating analytical kinematics')
    return rows, frames, events, finish_diagnostics(model, rows, diagnostics)


def pymunk_run(model):
    import pymunk
    c, p = model.c, model.p
    space = pymunk.Space()
    space.gravity = (0, -p['g'])
    space.iterations = int(c['iterations'])
    # Infinite moment enforces the explicitly locked pitch; no artificial
    # rotational inertia or moving link mass is inserted.
    body = pymunk.Body(p['m1'], math.inf)
    initial_side = 'left' if model.exact_square and c['inputDelayS'] == 0 else 'right'
    h, hd, _ = model.chassis(0, model.q0, c['initialVelocityDegS'] * R, side=initial_side)
    body.position, body.velocity = (0, h), (0, hd)
    space.add(body)
    groove = pymunk.GrooveJoint(space.static_body, body, (0, -10000), (0, 10000), (0, 0))
    groove.collide_bodies = False
    space.add(groove)
    rows, frames, events = [], [], []
    t, wa, wi, next_sample = 0., 0., 0., 1 / c['outputHz']
    motor_loss = 0.
    termination, max_x = 'duration', 0.
    boundaries = sorted(set(model.input_breaks() + [c['duration']]))
    def read(side='right'):
        q, v, ha = model.heave_acceleration(t, body.position.y, body.velocity.y, side)
        return q, v, ha
    def append(side='right'):
        nonlocal max_x
        q, v, _ = read(side)
        row, frame = state_observation(model, t, q, v, side,
                                      dict(A=[-body.position.x * 1000, 0, body.position.y * 1000],
                                           bodyPositionsMm={'1': [-body.position.x * 1000, 0, body.position.y * 1000]},
                                           bodyAnglesDeg={'1': body.angle / R},
                                           constraintPositionErrorMm=abs(body.position.x) * 1000,
                                           constraintAngleErrorDeg=abs(body.angle) / R))
        row.update(chassisZMm=body.position.y * 1000, chassisVelocityMmS=body.velocity.y * 1000,
                   actuatorDampingWorkJ=wa, terrainWorkJ=wi, inputWorkJ=wi)
        if model.motor_config_supplied:
            row['motorFrictionLossJ'] = row['motorDissipatedJ'] = motor_loss
        max_x = max(max_x, abs(body.position.x))
        if rows and abs(rows[-1]['t'] - t) < 1e-11 and side != 'left' and rows[-1].get('eventSide') != 'before':
            rows[-1], frames[-1] = row, frame
        else:
            rows.append(row)
            frames.append(frame)
        return row
    def apply_jump():
        nonlocal wa, wi, termination
        q, v, _ = read('left')
        try:
            _, _, da, di, event = jump(model, t, q, v)
        except ValueError:
            termination = 'input-jump-travel-limit'
            events.append(dict(t=t, type='input-jump-rejected', reason='New prescribed wheel height exceeds working travel; stopped at pre-jump state.'))
            return
        rows[-1]['eventSide'] = 'before'
        wa, wi = wa + da, wi + di
        append('right')['eventSide'] = 'after'
        events.append(event)
    append(initial_side)
    if initial_side == 'left':
        apply_jump()
    for end in boundaries:
        if termination != 'duration':
            break
        if end <= t + 1e-12:
            continue
        exact_end = model.exact_square and end in model.input_breaks()
        while t < end - 1e-12:
            step = min(c['dt'], end - t, max(1e-12, next_sample - t))
            q, v, ha = read()
            if (q <= model.lo + 1e-11 and v < 0) or (q >= model.hi - 1e-11 and v > 0):
                termination = 'travel-limit'
                break
            before_power = powers(model, t, q, v)
            saved = body.position, body.velocity
            # Real gravity acts on m1 in Pymunk. Remaining force consists of the
            # spring/actuator and exactly condensed link inertial reactions.
            body.force = (0, p['m1'] * (ha + p['g']))
            space.step(step)
            new_t = t + step
            side = 'left' if exact_end and new_t >= end - 1e-12 else 'right'
            try:
                nq, nv, _ = model.heave_acceleration(new_t, body.position.y, body.velocity.y, side)
            except ValueError:
                body.position, body.velocity = saved
                termination = 'travel-limit'
                break
            after_power = powers(model, new_t, nq, nv, side)
            wa += .5 * (before_power[0] + after_power[0]) * step
            wi += .5 * (before_power[1] + after_power[1]) * step
            if model.motor_config_supplied:
                motor_loss += .5 * (model.motor.motor_state(q, v, 0)['motorLossPowerW']
                                    + model.motor.motor_state(nq, nv, 0)['motorLossPowerW']) * step
            t = new_t
            if t >= next_sample - 1e-10 or t >= end - 1e-10:
                append(side)
                if t >= next_sample - 1e-10:
                    next_sample += 1 / c['outputHz']
            if not math.isfinite(body.position.y + body.velocity.y) or abs(body.velocity.y) > 1e6:
                raise ValueError('Pymunk diverged; reduce timestep and inspect physical inputs.')
        if termination != 'duration':
            if t > rows[-1]['t'] + 1e-10:
                append()
            break
        if exact_end:
            apply_jump()
    diagnostics = dict(termination=termination, elapsedSeconds=t,
                       maxConstraintPositionErrorMm=max_x * 1000, maxConstraintAngleErrorDeg=0,
                       integrator='Pymunk real chassis heave body / transformed h equation / exact inertial condensation',
                       frameSource='actual Pymunk chassis transform; exact ideal linkage reconstruction',
                       rigidBodies=1, chassisBodyMassKg=body.mass, chassisPitchLocked=True,
                       grooveConstraints=1, pivotConstraints=0, gearConstraints=0,
                       linkageFormulation='ideal kinematic transmission; nonzero link inertia exactly condensed into chassis force')
    return rows, frames, events, finish_diagnostics(model, rows, diagnostics)


def simulate(payload):
    if (not isinstance(payload, dict) or set(payload) - {'engine', 'params', 'runConfig', 'motorConfig'}
            or not {'engine', 'params', 'runConfig'} <= set(payload)):
        raise ValueError('Request requires engine, params, runConfig and optional motorConfig.')
    if payload['engine'] not in ('analytical', 'pymunk'):
        raise ValueError('Unknown dynamics engine.')
    if 'motorConfig' in payload and not isinstance(payload['motorConfig'], dict):
        raise ValueError('motorConfig must be an object when supplied.')
    model = Model(payload['params'], payload['runConfig'], payload.get('motorConfig'))
    rows, frames, events, diagnostics = analytical(model) if payload['engine'] == 'analytical' else pymunk_run(model)
    warnings = ['¼ model: chassis A heaves freely; xA and pitch are fixed as by ideal vertical slide rods.',
                'Wheel height is a prescribed actuator input. Signed inputReactionN can be negative; no unilateral tire/terrain contact or rod vertical support is modeled.',
                'Weight-reference static Fn is not reapplied dynamically: gravity acts once on every builder mass. Explicit global/contact loads are additional applied loads.',
                'Ideal massless nonslip belts and cable; fixed drive shaft theta4=0; no collisions, compliance or hardware validation.']
    if model.exact_square:
        warnings.append('Exact square events preserve chassis position/velocity. Massless transmission angles jump; angular velocity and finite reaction at the event itself are undefined. Rows report one-sided states and events report source work.')
    else:
        warnings.append('Applied input uses finite C2 quintic rises inside the nominal square high interval; requested and applied inputs are both returned.')
    if diagnostics['termination'] != 'duration':
        warnings.append('Working travel reached; run stops at the last admissible state without an invented impact response.')
    if payload['engine'] == 'pymunk':
        warnings.append('Pymunk integrates the actual m1 chassis body; linkage masses/inertias use exact inertial condensation, not separate rigid-link bodies. Refine dt before interpreting force peaks.')
    result = dict(schema='kinefold/dynamics-v2', engine=payload['engine'], params=model.p, runConfig=model.c,
                  snapshot=dict(params=model.p, solverConfig=model.c), designHash=model.hash(), rows=rows, frames=frames, events=events,
                  diagnostics={**diagnostics, 'modelRevision': 'floating-chassis-v2',
                               'initialStaticTorqueNm': -model.generalized(model.q0),
                               'initialGeneralizedInertiaKgM2': model.mass(model.q0)[0], 'resolvedInertiasKgM2': model.I,
                               'builderMassesKg': {key: model.p['m' + key] for key in ('1', '2', '3', '5', '6')},
                               'wheelCoefficientK': model.K, 'inputLaw': 'exact-spatial-square' if model.exact_square else 'C2-quintic-spatial-square',
                               'inputSpeedIsStudyAssumption': True}, warnings=warnings,
                  scope=dict(quarterModel=True, fixture='floating-chassis',
                             coordinates='+x front / left in preview; +z up; +y toward viewer',
                             chassis='vertical translation only; fixed horizontal position and pitch',
                             input='prescribed wheel height, no unilateral terrain contact'))
    if model.motor_config_supplied:
        result['motorConfig'] = model.motor.config
        result['snapshot']['motorConfig'] = model.motor.config
        result['diagnostics'].update(reflectedMotorInertiaKgM2=model.motor.reflected_inertia,
                                     legacyJointRotorInertiaKgM2=model.c['hipRotorInertiaKgM2'],
                                     jointCommandNm=model.motor.joint_command(model.c['hipTorqueNm']))
        warnings.append('Optional ideal geared motor: fixed theta_motor=N*q; conservative sinusoidal cogging and regularized Coulomb/viscous drag. Zero defaults are compatibility settings, not hardware measurements.')
    json.dumps(result, allow_nan=False)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request-stdin', action='store_true')
    parser.add_argument('--defaults', action='store_true')
    args = parser.parse_args()
    try:
        if args.defaults:
            result = defaults()
        elif args.request_stdin:
            result = simulate(json.load(sys.stdin))
        else:
            parser.error('Choose --request-stdin or --defaults.')
        print(json.dumps(result, allow_nan=False, separators=(',', ':')))
    except (ValueError, KeyError, TypeError, ArithmeticError, ImportError) as error:
        print(json.dumps({'error': str(error)}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
