"""Run builder-linked analytical or genuine 2D Pymunk fixed-hip tests.

Usage: .venv/Scripts/python.exe dynamics.py --request-stdin (JSON stdin), or
--defaults. Request {engine,params,runConfig}; builder mm/deg/kg/N, run seconds,
Nm, Nms/rad and kg m². Emits JSON finite traces, actual Pymunk body frames,
constraint/energy diagnostics and input snapshot. Experimental quarter-model
fixed-hip prescribed-load mechanism; no chassis translation, terrain, impacts,
cable mass/compliance, friction or hardware validation. Pymunk uses ideal gear
constraints; belt preload bearing forces are not inferred from gear impulses.
"""
import argparse
import json
import math
import sys

from dynamic_model import Model, R, defaults


def analytical(model):
    import numpy as np
    from scipy.integrate import solve_ivp
    c = model.c
    def derivative(t, y):
        q, v, work = y
        return (v, model.acceleration(q, v), c['hipTorqueNm'] * v - c['dampingNms'] * v * v)
    def lower(t, y):
        return y[0] - model.lo
    def upper(t, y):
        return model.hi - y[0]
    lower.terminal = upper.terminal = True
    lower.direction = upper.direction = -1
    initial = (model.q0, c['initialVelocityDegS'] * R, 0)
    solution = solve_ivp(derivative, (0, c['duration']), initial, method='DOP853', rtol=1e-9, atol=1e-11,
                         max_step=c['dt'], dense_output=True, events=(lower, upper))
    if not solution.success:
        raise ValueError(solution.message)
    end = float(solution.t[-1])
    times = list(np.arange(0, end + 1e-12, 1 / c['outputHz']))
    if not times or end - times[-1] > 1e-10:
        times.append(end)
    rows, frames, max_balance = [], [], 0
    initial_energy = model.observe(0, initial[0], initial[1], 0)[0]['energyJ']
    for t in times:
        q, v, work = (float(x) for x in solution.sol(t))
        # Event-root floating error is allowed only at machine precision.
        if model.lo - 1e-10 <= q <= model.hi + 1e-10:
            q = min(model.hi, max(model.lo, q))
        row, frame = model.observe(float(t), q, v, model.acceleration(q, v))
        row['actuatorDampingWorkJ'] = work
        max_balance = max(max_balance, abs(row['energyJ'] - initial_energy - work))
        rows.append(row)
        frames.append(frame)
    return rows, frames, dict(termination='travel-limit' if solution.status == 1 else 'duration',
                             elapsedSeconds=end, maxWorkEnergyResidualJ=max_balance,
                             maxConstraintPositionErrorMm=0, maxConstraintAngleErrorDeg=0,
                             evaluations=int(solution.nfev), integrator='SciPy DOP853',
                             frameSource='exact analytical kinematics')


def pymunk_build(model):
    import pymunk
    p, c, q = model.p, model.c, model.q0
    if p['m5'] == 0 and model.I['5'] != 0:
        raise ValueError('Pymunk cannot represent zero m5 with nonzero I5. Enter positive builder m5 or zero custom I5.')
    for key in ('2', '3', '6'):
        if p['m' + key] <= 0:
            raise ValueError('Pymunk requires positive builder m2, m3 and m6. Select Dynamic example · illustrative masses or enter physical masses; no mass is substituted.')
    for key in ('2', '3', '6') + (('5',) if p['m5'] > 0 else ()):
        if model.I[key] <= 0:
            raise ValueError(f'Pymunk body {key} needs positive rotational inertia; select rod/disc estimates or enter custom I{key}.')
    space = pymunk.Space()
    space.gravity = (0, -p['g'])
    space.iterations = int(c['iterations'])
    sites = model.sites(q)
    angles = {'2': q + math.pi - p['alpha'] * R,
              '3': p['phi0'] * R + (math.pi - q) * (model.ab - 1) + math.pi - p['alpha'] * R,
              '5': model.k5 * (q - p['te'] * R), '6': model.K * (q - p['te'] * R)}
    velocity = c['initialVelocityDegS'] * R
    bodies = {}
    for key in ('2', '3', '6') + (('5',) if p['m5'] > 0 else ()):
        body = pymunk.Body(p['m' + key], model.I[key])
        body.position, body.angle = sites[key][0], angles[key]
        body.velocity = tuple(x * velocity for x in sites[key][1])
        body.angular_velocity = model.rates[key] * velocity
        space.add(body)
        bodies[key] = body
    u, l, w = (bodies[key] for key in ('2', '3', '6'))
    L, L3 = p['L2'] / 1000, p['L3'] / 1000
    pivots = [pymunk.PivotJoint(space.static_body, u, (0, 0), (-L / 2, 0)),
              pymunk.PivotJoint(u, l, (L / 2, 0), (-L3 / 2, 0)),
              pymunk.PivotJoint(l, w, (L3 / 2, 0), (0, 0))]
    if '5' in bodies:
        pivots.append(pymunk.PivotJoint(u, bodies['5'], (L / 2, 0), (0, 0)))
    gears = []
    for key in ('3', '6') + (('5',) if '5' in bodies else ()):
        rate = model.rates[key]
        if abs(rate) < 1e-14:
            gear = pymunk.GearJoint(space.static_body, bodies[key], bodies[key].angle, 1)
        else:
            ratio = 1 / rate
            gear = pymunk.GearJoint(u, bodies[key], bodies[key].angle * ratio - u.angle, ratio)
        gears.append(gear)
    for constraint in pivots + gears:
        constraint.collide_bodies = False
    space.add(*(pivots + gears))
    # Sensor shapes describe the actual 2D bodies; they never introduce contact.
    shapes = [pymunk.Segment(u, (-L / 2, 0), (L / 2, 0), .001),
              pymunk.Segment(l, (-L3 / 2, 0), (L3 / 2, 0), .001), pymunk.Circle(w, p['rw'] / 1000)]
    if '5' in bodies:
        shapes.append(pymunk.Circle(bodies['5'], max(p['rd'], p['re']) / 1000))
    for shape in shapes:
        shape.sensor = True
    space.add(*shapes)
    return space, bodies, pivots, gears


def actual_spring(model, q, horn):
    """Apply the same route to actual Pymunk horn translation/rotation errors."""
    ideal = model.spring(q)
    if not model.p['springEnabled']:
        return ideal
    p = model.p
    alpha = p['alpha'] * R
    D = (1000 * (math.cos(alpha) * horn.x - math.sin(alpha) * horn.y),
         1000 * (math.sin(alpha) * horn.x + math.cos(alpha) * horn.y))
    dx, dy = D[0] - p['Su'], D[1] - p['Sv']
    distance = math.hypot(dx, dy)
    if distance <= p['rs'] + 1e-9:
        raise ValueError('Actual Pymunk horn reached the idler; no tangent exists.')
    if p['rs']:
        psi = math.atan2(dy, dx) - math.acos(p['rs'] / distance)
        psi_ideal = math.atan2(ideal['Q'][1] - p['Sv'], ideal['Q'][0] - p['Su'])
        difference = math.atan2(math.sin(psi - psi_ideal), math.cos(psi - psi_ideal))
        Q = (p['Su'] + p['rs'] * math.cos(psi), p['Sv'] + p['rs'] * math.sin(psi))
        wrap = ideal['wrap'] + difference
        tangent = math.sqrt(distance * distance - p['rs'] * p['rs'])
    else:
        Q, wrap, tangent = (p['Su'], p['Sv']), 0, distance
    delta = tangent + p['rs'] * wrap - model.reference_payout
    rate = 0 if p['springLaw'] == 'constant' else p['springK']
    force = max(0, p['p0'] + rate * delta)
    energy = force * force / (2 * rate) / 1000 if rate else p['p0'] * delta / 1000
    return {**ideal, 'D': D, 'Q': Q, 'force': force, 'energy': energy,
            'unit': ((Q[0] - D[0]) / tangent, (Q[1] - D[1]) / tangent)}


def pymunk_run(model):
    p, c = model.p, model.c
    space, bodies, pivots, gears = pymunk_build(model)
    u, l, w = (bodies[key] for key in ('2', '3', '6'))
    horn_local = (p['hornR'] / 1000 * math.cos(p['nu'] * R - math.pi) - p['L2'] / 2000,
                  p['hornR'] / 1000 * math.sin(p['nu'] * R - math.pi))
    q_of = lambda: u.angle - math.pi + p['alpha'] * R
    world = lambda v: [-v[0] * 1000, 0, v[1] * 1000]
    rows, frames = [], []
    max_pin, max_angle, max_energy = 0, 0, 0
    initial_energy = model.observe(0, model.q0, c['initialVelocityDegS'] * R, 0)[0]['energyJ']
    work, t, next_sample = 0, 0, 0
    termination = 'duration'
    def observe(acceleration):
        nonlocal max_pin, max_angle, max_energy
        q, v = q_of(), u.angular_velocity
        pin = max((j.a.local_to_world(j.anchor_a) - j.b.local_to_world(j.anchor_b)).length for j in pivots)
        angular = max(abs(body.angle - ((q + math.pi - p['alpha'] * R) if key == '2' else
                        p['phi0'] * R + (math.pi - q) * (model.ab - 1) + math.pi - p['alpha'] * R if key == '3' else
                        model.rates[key] * (q - p['te'] * R))) for key, body in bodies.items())
        max_pin, max_angle = max(max_pin, pin), max(max_angle, angular)
        actual = dict(A=world(u.local_to_world((-p['L2'] / 2000, 0))),
                      B=world(u.local_to_world((p['L2'] / 2000, 0))), C=world(w.position),
                      wheelAngle=w.angle / R,
                      bodyAnglesDeg={key: body.angle / R for key, body in bodies.items()},
                      bodyPositionsMm={key: world(body.position) for key, body in bodies.items()},
                      constraintPositionErrorMm=pin * 1000, constraintAngleErrorDeg=angular / R)
        row, frame = model.observe(t, q, v, acceleration, actual)
        spring = actual_spring(model, q, u.local_to_world(horn_local))
        if p['springEnabled']:
            frame.update(D=world(u.local_to_world(horn_local)), Q=world(tuple(v / 1000 for v in model.rotate(spring['Q']))))
        kinetic = sum(.5 * body.mass * body.velocity.length_squared + .5 * body.moment * body.angular_velocity ** 2 for body in bodies.values())
        potential = (p['g'] * sum(body.mass * body.position.y for body in bodies.values()) + spring['energy']
                     - (model.force[0] * w.position.x + model.force[1] * w.position.y) - model.Mw * w.angle)
        # Constant energy gauge: model potential uses -Mw*K*q, body angle uses K*(q-te).
        potential -= model.Mw * model.K * p['te'] * R
        row.update(Fs=spring['force'], kineticJ=kinetic, potentialJ=potential, energyJ=kinetic + potential,
                   CxMm=-w.position.x * 1000, CzMm=w.position.y * 1000, actuatorDampingWorkJ=work)
        max_energy = max(max_energy, abs(row['energyJ'] - initial_energy - work))
        rows.append(row)
        frames.append(frame)
    observe(model.acceleration(model.q0, c['initialVelocityDegS'] * R))
    next_sample = 1 / c['outputHz']
    while t < c['duration'] - 1e-12:
        dt = min(c['dt'], c['duration'] - t, max(1e-12, next_sample - t))
        q, v = q_of(), u.angular_velocity
        if ((q <= model.lo + 1e-12 and v < 0) or (q >= model.hi - 1e-12 and v > 0)):
            termination = 'travel-limit'
            break
        saved = {key: (body.position, body.velocity, body.angle, body.angular_velocity) for key, body in bodies.items()}
        for body in bodies.values():
            body.force = (0, 0)
            body.torque = 0
        u.torque = c['hipTorqueNm'] - c['dampingNms'] * v
        beta = p['beta'] * R
        patch = w.position - (p['rw'] / 1000) * __import__('pymunk').Vec2d(math.sin(beta), math.cos(beta))
        w.apply_force_at_world_point(model.force, patch)
        D = u.local_to_world(horn_local)
        spring = actual_spring(model, q, D)
        if p['springEnabled']:
            # Horn pin is rigid on the femur; tangent direction uses the exact
            # finite-idler path. Positive angular direction is source CCW/+y.
            F = model.rotate(tuple(component * spring['force'] for component in spring['unit']))
            u.apply_force_at_world_point(F, D)
        space.step(dt)
        new_q = q_of()
        if new_q < model.lo or new_q > model.hi:
            # Roll back the inadmissible step; never render an ideal/clipped pose
            # that disagrees with the engine bodies. This test has no impact law.
            for key, state in saved.items():
                bodies[key].position, bodies[key].velocity, bodies[key].angle, bodies[key].angular_velocity = state
            termination = 'travel-limit'
            break
        new_v = u.angular_velocity
        work += c['hipTorqueNm'] * (new_q - q) - .5 * c['dampingNms'] * (v * v + new_v * new_v) * dt
        t += dt
        if t >= next_sample - 1e-10 or t >= c['duration'] - 1e-10:
            observe((new_v - v) / dt)
            next_sample += 1 / c['outputHz']
        if not math.isfinite(new_q + new_v) or abs(new_v) > 1e6:
            raise ValueError('Pymunk diverged; reduce timestep or loading and inspect inertias.')
    if t > rows[-1]['t'] + 1e-10:
        observe(model.acceleration(q_of(), u.angular_velocity))
    return rows, frames, dict(termination=termination, elapsedSeconds=t, maxWorkEnergyResidualJ=max_energy,
                             maxConstraintPositionErrorMm=max_pin * 1000, maxConstraintAngleErrorDeg=max_angle / R,
                             integrator='Pymunk 2D rigid bodies / iterative pivot and gear constraints',
                             frameSource='actual Pymunk body transforms',
                             rigidBodies=len(bodies), pivotConstraints=len(pivots), gearConstraints=len(gears))


def simulate(payload):
    if not isinstance(payload, dict) or set(payload) != {'engine', 'params', 'runConfig'}:
        raise ValueError('Request requires exactly engine, params and runConfig.')
    if payload['engine'] not in ('analytical', 'pymunk'):
        raise ValueError('Unknown dynamics engine.')
    model = Model(payload['params'], payload['runConfig'])
    rows, frames, diagnostics = analytical(model) if payload['engine'] == 'analytical' else pymunk_run(model)
    warnings = ['¼ model · fixed-hip mechanism test: m1 remains fixed at A; prescribed wheel load is not a solved contact reaction.',
                'Ideal massless nonslip belts and cable; fixed drive shaft theta4=0; no ground collision, chassis translation or impact law.',
                'Rod/disc inertias and the entered hip rotor inertia are explicit modeling assumptions, not measured hardware values.']
    if diagnostics['termination'] == 'travel-limit':
        warnings.append('Working travel limit reached; run ends at the last admissible state before impact.')
    if payload['engine'] == 'pymunk':
        warnings.append('Spring force is applied explicitly each timestep. Refine dt and inspect constraint/work-energy residuals before interpreting peaks. Gear constraints do not reproduce belt preload bearing loads.')
    result = dict(schema='kinefold/dynamics-v1', engine=payload['engine'], params=model.p, runConfig=model.c,
                  snapshot=dict(params=model.p, solverConfig=model.c), designHash=model.hash(), rows=rows, frames=frames,
                  diagnostics={**diagnostics, 'initialStaticTorqueNm': -model.generalized(model.q0),
                               'initialGeneralizedInertiaKgM2': model.mass(model.q0)[0], 'resolvedInertiasKgM2': model.I,
                               'wheelCoefficientK': model.K}, warnings=warnings,
                  scope=dict(quarterModel=True, fixture='fixed-hip', coordinates='+x front / left in preview; +z up; +y toward viewer'))
    # Reject NaN/Infinity rather than emitting nonstandard JSON.
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
