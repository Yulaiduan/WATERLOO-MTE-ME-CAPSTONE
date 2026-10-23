"""Exact builder-linked V4 geometry and vertical-slide chassis dynamics.

Imported by dynamics.py; inputs are the complete builder mm/deg/kg/N design and
explicit run configuration. Internal positions are source-horizontal/up in m,
angles radians, inertias kg m²; exported coordinates are Kinefold x/y/z in mm.
Outputs geometry, generalized mass, forces and conservative potential in SI.
Experimental quarter model: A translates vertically, x/pitch and drive shaft
are locked; wheel height is prescribed, not unilateral terrain contact. Ideal
massless belts/cable; no friction, tire compliance or hardware validation.
"""
import hashlib
import json
import math
from motor_model import Motor

R = math.pi / 180
TAU = 2 * math.pi
NUMERIC_KEYS = ('L2 L3 ra rb rc rd re rf rw alpha phi0 te tc m1 m2 m3 m5 m6 g beta Fn Ft Fx Fz Tab0 Tcd0 Tef0 springK hornR Sv rs p0 nu Su theta2').split()
BOUNDS = {'duration': (.05, 30), 'dt': (.0001, .01), 'outputHz': (1, 1000),
          'initialVelocityDegS': (-720, 720), 'hipTorqueNm': (-10000, 10000),
          'dampingNms': (0, 10000), 'hipRotorInertiaKgM2': (0, 1000),
          'I2': (0, 1000), 'I3': (0, 1000), 'I5': (0, 1000), 'I6': (0, 1000),
          'iterations': (10, 500), 'inputHeightMm': (0, 1000),
          'inputPlateauMm': (.1, 10000), 'inputGapMm': (.1, 10000),
          'inputSpeedMmS': (.1, 10000), 'inputRiseMm': (0, 1000),
          'inputDelayS': (0, 30)}


def defaults():
    return dict(fixture='floating-chassis', duration=6.5, dt=.001, outputHz=100,
                initialVelocityDegS=0, hipTorqueNm=0, dampingNms=0,
                hipRotorInertiaKgM2=0, inertiaModel='uniform-rods-discs',
                I2=0, I3=0, I5=0, I6=0, iterations=80,
                inputHeightMm=150, inputPlateauMm=150, inputGapMm=150,
                inputSpeedMmS=100, inputRiseMm=0, inputDelayS=.5)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(params, config):
    if not isinstance(params, dict) or not isinstance(config, dict):
        raise ValueError('params and runConfig must be objects.')
    for key in NUMERIC_KEYS:
        if not finite(params.get(key)):
            raise ValueError(f'Builder parameter {key} must be finite and present.')
    allowed = set(NUMERIC_KEYS) | {'springEnabled', 'springLaw', 'loadMode'}
    if set(params) - allowed:
        raise ValueError('Unknown builder parameters: ' + ', '.join(sorted(set(params) - allowed)))
    if type(params.get('springEnabled')) is not bool:
        raise ValueError('springEnabled must be boolean.')
    if params.get('springLaw') not in ('constant', 'v4') or params.get('loadMode') not in ('weight', 'global', 'contact'):
        raise ValueError('Unknown spring law or loading convention.')
    for key in ('L2', 'L3', 'ra', 'rb', 'rc', 'rd', 're', 'rf', 'rw', 'hornR'):
        if params[key] <= 0:
            raise ValueError(key + ' must be positive.')
    for key in ('m1', 'm2', 'm3', 'm5', 'm6', 'g', 'Tab0', 'Tcd0', 'Tef0', 'springK', 'rs', 'p0'):
        if params[key] < 0:
            raise ValueError(key + ' must be nonnegative.')
    for key, hi in (('alpha', 45), ('phi0', 30), ('beta', 90)):
        if not 0 <= params[key] <= hi:
            raise ValueError(f'{key} must be within 0–{hi} degrees.')
    if not 90 <= params['te'] <= params['theta2'] <= params['tc'] <= 270:
        raise ValueError('Require 90 ≤ te ≤ theta2 ≤ tc ≤ 270 degrees.')
    for a, b, length in (('ra', 'rb', 'L2'), ('rc', 'rd', 'L2'), ('re', 'rf', 'L3')):
        if params[a] + params[b] >= params[length]:
            raise ValueError(f'{a}/{b} pulley pitch circles overlap or touch.')
    if set(config) != set(defaults()):
        raise ValueError('runConfig must contain exactly the documented solver configuration keys.')
    if config['fixture'] != 'floating-chassis' or config['inertiaModel'] not in ('uniform-rods-discs', 'custom'):
        raise ValueError('Unknown fixture or inertia model.')
    for key, (lo, hi) in BOUNDS.items():
        if not finite(config[key]) or not lo <= config[key] <= hi:
            raise ValueError(f'{key} must be finite within [{lo}, {hi}].')
    if int(config['iterations']) != config['iterations']:
        raise ValueError('iterations must be an integer.')
    if math.ceil(config['duration'] / config['dt']) > 100000:
        raise ValueError('Run exceeds 100000 integration steps; increase dt or reduce duration.')
    if config['outputHz'] > 1 / config['dt'] + 1e-10:
        raise ValueError('outputHz must not exceed 1/dt.')
    if 2 * config['inputRiseMm'] > config['inputPlateauMm']:
        raise ValueError('Two input rises must fit inside the nominal square high interval.')
    period = (config['inputPlateauMm'] + config['inputGapMm']) / config['inputSpeedMmS']
    if 4 * math.ceil(max(0, config['duration'] - config['inputDelayS']) / period) > 10000:
        raise ValueError('Run exceeds 10000 input transition boundaries; reduce input speed or duration.')


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, n):
    return (a[0] * n, a[1] * n)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


class Model:
    def __init__(self, params, config, motorConfig=None):
        validate(params, config)
        self.motor = Motor.resolve(motorConfig)
        self.motor_config_supplied = motorConfig is not None
        self.p, self.c = dict(params), dict(config)
        p = self.p
        self.q0 = p['theta2'] * R
        self.lo, self.hi = p['te'] * R, p['tc'] * R
        self.ab, self.dc, self.fe = p['ra'] / p['rb'], p['rd'] / p['rc'], p['rf'] / p['re']
        self.k3 = 1 - self.ab
        self.k5 = 1 - 1 / self.dc
        self.K = 1 - self.ab + (self.ab - 1 / self.dc) / self.fe
        self.rates = {'2': 1, '3': self.k3, '5': self.k5, '6': self.K}
        self.I = {'2': p['m2'] * (p['L2'] / 1000) ** 2 / 12,
                  '3': p['m3'] * (p['L3'] / 1000) ** 2 / 12,
                  '5': .5 * p['m5'] * (max(p['rd'], p['re']) / 1000) ** 2,
                  '6': .5 * p['m6'] * (p['rw'] / 1000) ** 2}
        if config['inertiaModel'] == 'custom':
            self.I = {key: config['I' + key] for key in self.I}
        self.I['2'] += config['hipRotorInertiaKgM2']
        self.I['2'] += self.motor.reflected_inertia
        if p['m1'] <= 0:
            raise ValueError('Floating chassis requires positive builder m1; no chassis mass is substituted.')
        self.total_mass = sum(p['m' + key] for key in ('1', '2', '3', '5', '6'))
        self.force, self.Mw = self.loads()
        self.route = self.exit_route() if p['springEnabled'] else dict(applied=0, shift=0)
        self.reference_payout = self.geometry(math.pi / 2, reference=True)['payout'] if p['springEnabled'] else 0
        if p['springEnabled']:
            for q in self.candidates(self.lo, self.hi):
                self.geometry(q)
        # A Lipschitz bound on zC' certifies the gaps between samples as well;
        # dense samples alone could miss a turning point at extreme belt ratios.
        count = 400
        curvature_bound = (p['L2'] + p['L3'] * self.k3 * self.k3) / 1000
        slopes = [self.sites(self.lo + (self.hi - self.lo) * i / count)['6'][1][1] for i in range(count + 1)]
        gap_bound = curvature_bound * (self.hi - self.lo) / (2 * count)
        if min(slopes) <= gap_bound + 1e-7 and max(slopes) >= -gap_bound - 1e-7:
            raise ValueError('Floating heave requires monotonic wheel-relative z with a nonzero slope throughout the working range; adjust geometry/range.')
        self.slope_sign = 1 if slopes[0] > 0 else -1
        self.exact_square = config['inputRiseMm'] == 0
        if self.exact_square and config['inputHeightMm'] > 0:
            if (any(p['m' + key] != 0 or self.I[key] != 0 for key in ('2', '3', '5', '6')) or config['dampingNms'] != 0
                    or (self.motor.enabled and any(self.motor.config[k] != 0 for k in ('coulombFrictionNm', 'viscousFrictionNms')))):
                raise ValueError('Exact square jumps require massless moving links/wheel, zero moving/rotor inertias and zero hip damping. Set positive inputRiseMm (e.g. 10 mm) for a finite C2 rise; no impact law is invented.')
        if self.mass(self.q0)[0] <= 1e-12:
            raise ValueError('Floating generalized inertia is zero at the initial pose.')

    def rotate(self, v):
        a = self.p['alpha'] * R
        return (math.cos(a) * v[0] + math.sin(a) * v[1], -math.sin(a) * v[0] + math.cos(a) * v[1])

    def loads(self):
        p = self.p
        b = p['beta'] * R
        if p['loadMode'] == 'contact':
            f = (p['Fn'] * math.sin(b) + p['Ft'] * math.cos(b), p['Fn'] * math.cos(b) - p['Ft'] * math.sin(b))
            ft = p['Ft']
        else:
            # Static weight-reference Fn is not an additional dynamic force.
            # Every builder mass already experiences gravity exactly once.
            f = (0, 0) if p['loadMode'] == 'weight' else (-p['Fx'], p['Fz'])
            ft = f[0] * math.cos(b) - f[1] * math.sin(b)
        return f, p['rw'] * ft / 1000

    def sites(self, q):
        p, k = self.p, self.k3
        b = p['phi0'] * R + (math.pi - q) * (self.ab - 1)
        L, l = p['L2'] / 1000, p['L3'] / 1000
        B = (-L * math.cos(q), -L * math.sin(q))
        vB, aB = (L * math.sin(q), -L * math.cos(q)), (L * math.cos(q), L * math.sin(q))
        leg = (-l * math.cos(b), -l * math.sin(b))
        C = add(B, leg)
        vC = add(vB, (l * k * math.sin(b), -l * k * math.cos(b)))
        aC = add(aB, (l * k * k * math.cos(b), l * k * k * math.sin(b)))
        pairs = {'2': (mul(B, .5), mul(vB, .5), mul(aB, .5)),
                 '3': (mul(add(B, C), .5), mul(add(vB, vC), .5), mul(add(aB, aC), .5)),
                 '5': (B, vB, aB), '6': (C, vC, aC)}
        return {key: tuple(self.rotate(v) for v in vs) for key, vs in pairs.items()}

    def mass(self, q):
        return self.coefficients(q)[:2]

    def floating_sites(self, q):
        """Position/Jacobian/curvature at fixed prescribed wheel-centre height."""
        sites = self.sites(q)
        C = sites['6']
        sites['1'] = ((0, 0), (0, 0), (0, 0))
        return {key: tuple((v[0], v[1] - C[i][1]) for i, v in enumerate(values))
                for key, values in sites.items()}

    def coefficients(self, q):
        sites = self.floating_sites(q)
        M = sum(self.p['m' + key] * dot(v[1], v[1]) for key, v in sites.items())
        M += sum(self.I[key] * self.rates[key] ** 2 for key in self.I)
        dM = sum(2 * self.p['m' + key] * dot(v[1], v[2]) for key, v in sites.items())
        B = sum(self.p['m' + key] * v[1][1] for key, v in sites.items())
        dB = sum(self.p['m' + key] * v[2][1] for key, v in sites.items())
        return M, dM, B, dB

    def input(self, t, side='right'):
        """Requested square and applied trajectory, SI height/velocity/acceleration.

        Positive rise uses C2 quintic ramps *inside* each nominal high interval.
        Exact square has no finite derivative at events; left/right derivatives
        returned here apply only to the open intervals on either side.
        """
        c = self.c
        speed = c['inputSpeedMmS'] / 1000
        high, period = c['inputPlateauMm'] / c['inputSpeedMmS'], (c['inputPlateauMm'] + c['inputGapMm']) / c['inputSpeedMmS']
        elapsed = t - c['inputDelayS']
        height = c['inputHeightMm'] / 1000
        if elapsed < -1e-12 or (abs(elapsed) < 1e-12 and side == 'left'):
            return dict(requested=0, applied=0, velocity=0, acceleration=0, distance=speed * max(0, elapsed))
        phase = max(0, elapsed) % period
        if phase < 1e-10 or period - phase < 1e-10:
            phase = period if side == 'left' and elapsed > 0 else 0
        if abs(phase - high) < 1e-10:
            phase = high - 1e-11 if side == 'left' else high
        requested = height if phase < high else 0
        if self.exact_square or not requested:
            return dict(requested=requested, applied=requested, velocity=0, acceleration=0, distance=speed * max(0, elapsed))
        rise = c['inputRiseMm'] / c['inputSpeedMmS']
        if phase < rise:
            u, sign = phase / rise, 1
        elif phase > high - rise:
            u, sign = (high - phase) / rise, -1
        else:
            return dict(requested=height, applied=height, velocity=0, acceleration=0, distance=speed * elapsed)
        smooth = u ** 3 * (10 + u * (-15 + 6 * u))
        d = 30 * u * u * (1 - u) ** 2
        dd = 60 * u * (1 - u) * (1 - 2 * u)
        return dict(requested=height, applied=height * smooth, velocity=sign * height * d / rise,
                    acceleration=height * dd / (rise * rise), distance=speed * max(0, elapsed))

    def input_breaks(self):
        c = self.c
        high = c['inputPlateauMm'] / c['inputSpeedMmS']
        period = (c['inputPlateauMm'] + c['inputGapMm']) / c['inputSpeedMmS']
        rise = c['inputRiseMm'] / c['inputSpeedMmS']
        out = set()
        cycle = 0
        while c['inputDelayS'] + cycle * period <= c['duration'] + 1e-12:
            start = c['inputDelayS'] + cycle * period
            for offset in ((0, high) if self.exact_square else (0, rise, high - rise, high)):
                t = start + offset
                if 0 <= t <= c['duration'] + 1e-12:
                    out.add(min(c['duration'], t))
            cycle += 1
        return sorted(out)

    def wheel_height(self, t, side='right'):
        return self.p['rw'] / 1000 + self.input(t, side)['applied']

    def chassis(self, t, q, velocity, acceleration=0, side='right'):
        C = self.sites(q)['6']
        base = self.input(t, side)
        return (self.p['rw'] / 1000 + base['applied'] - C[0][1],
                base['velocity'] - C[1][1] * velocity,
                base['acceleration'] - C[1][1] * acceleration - C[2][1] * velocity * velocity)

    def q_from_chassis(self, t, height, side='right'):
        from scipy.optimize import brentq
        target = self.wheel_height(t, side) - height
        f = lambda q: self.sites(q)['6'][0][1] - target
        a, b = f(self.lo), f(self.hi)
        if abs(a) < 1e-13:
            return self.lo
        if abs(b) < 1e-13:
            return self.hi
        if a * b > 0:
            raise ValueError('Prescribed wheel height and floating chassis exceed working travel.')
        return brentq(f, self.lo, self.hi, xtol=1e-14)

    def raw_geometry(self, q):
        p = self.p
        phi = q + p['nu'] * R
        D = (p['hornR'] * math.cos(phi), p['hornR'] * math.sin(phi))
        v = (D[0] - p['Su'], D[1] - p['Sv'])
        distance = math.hypot(*v)
        if p['rs'] == 0:
            unit = (-v[0] / distance, -v[1] / distance) if distance > 1e-9 else (0, 0)
            return dict(D=D, Q=(p['Su'], p['Sv']), unit=unit, tangent=distance, baseWrap=0,
                        derivative=D[1] * unit[0] - D[0] * unit[1])
        if distance <= p['rs'] + 1e-9:
            raise ValueError('Horn pin lies on/inside the idler; finite tangent does not exist.')
        def polar(angle, vec):
            if math.hypot(p['Su'], p['Sv']) < p['hornR']:
                return angle + math.atan2(p['Su'] * math.sin(angle) - p['Sv'] * math.cos(angle), p['hornR'] - p['Su'] * math.cos(angle) - p['Sv'] * math.sin(angle))
            center = math.atan2(-p['Sv'], -p['Su'])
            raw = math.atan2(vec[1], vec[0])
            return center + math.atan2(math.sin(raw - center), math.cos(raw - center))
        refphi = math.pi / 2 + p['nu'] * R
        refv = (p['hornR'] * math.cos(refphi) - p['Su'], p['hornR'] * math.sin(refphi) - p['Sv'])
        refd = math.hypot(*refv)
        if refd <= p['rs'] + 1e-9:
            raise ValueError('90 degree preload reference lies on/inside the idler.')
        psi = polar(phi, v) - math.acos(p['rs'] / distance)
        psi0 = polar(refphi, refv) - math.acos(p['rs'] / refd)
        turns = math.ceil((math.pi / 2 - psi0 - 1e-12) / TAU)
        Q = (p['Su'] + p['rs'] * math.cos(psi), p['Sv'] + p['rs'] * math.sin(psi))
        tangent = math.sqrt(distance * distance - p['rs'] * p['rs'])
        unit = ((Q[0] - D[0]) / tangent, (Q[1] - D[1]) / tangent)
        return dict(D=D, Q=Q, unit=unit, tangent=tangent, baseWrap=psi - math.pi / 2 + turns * TAU,
                    derivative=D[1] * unit[0] - D[0] * unit[1])

    def candidates(self, lo, hi):
        p = self.p
        out = [lo, hi]
        radius = math.hypot(p['Su'], p['Sv'])
        for A, B, target in ((-p['Sv'], p['Su'], p['rs']), (-p['Sv'], p['Su'], -p['rs']),
                             (p['Su'], p['Sv'], radius), (p['Su'], p['Sv'], -radius),
                             (p['Su'], p['Sv'], p['hornR'] - p['rs']), (p['Su'], p['Sv'], p['hornR'] + p['rs'])):
            mag = math.hypot(A, B)
            if mag < 1e-9 or abs(target) > mag + 1e-9:
                continue
            phase, angle = math.atan2(B, A), math.acos(max(-1, min(1, target / mag)))
            for root in (phase + angle, phase - angle):
                for n in range(math.ceil((lo + p['nu'] * R - root) / TAU), math.floor((hi + p['nu'] * R - root) / TAU) + 1):
                    out.append(root + n * TAU - p['nu'] * R)
        return sorted(set(out))

    def exit_route(self):
        if self.p['rs'] == 0:
            return dict(applied=0, shift=0)
        wraps = [self.raw_geometry(q)['baseWrap'] for q in self.candidates(self.lo, self.hi)]
        shift = TAU * math.floor((TAU - max(wraps) + 1e-12) / TAU)
        applied = max(0, -min(wraps) - shift)
        if max(wraps) + shift + applied > TAU + 1e-8:
            raise ValueError('Working range requires more than one idler wrap.')
        return dict(applied=applied, shift=shift)

    def geometry(self, q, reference=False):
        z = self.raw_geometry(q)
        wrap = z['baseWrap'] + self.route['shift'] + self.route['applied']
        if not reference and self.lo <= q <= self.hi and self.p['rs'] > 0 and not -1e-8 <= wrap <= TAU + 1e-8:
            raise ValueError('Pose exceeds the working idler wrap.')
        z.update(wrap=wrap, payout=z['tangent'] + self.p['rs'] * wrap)
        return z

    def spring(self, q):
        if not self.p['springEnabled']:
            return dict(force=0, torque=0, energy=0)
        z = self.geometry(q)
        delta = z['payout'] - self.reference_payout
        rate = 0 if self.p['springLaw'] == 'constant' else self.p['springK']
        F = max(0, self.p['p0'] + rate * delta)
        if F > 0 and math.hypot(*z['unit']) < .5:
            raise ValueError('Coincident cable pin/idler has no force direction.')
        energy = F * F / (2 * rate) / 1000 if rate else self.p['p0'] * delta / 1000
        return {**z, 'force': F, 'torque': -F * z['derivative'] / 1000, 'energy': energy}

    def generalized(self, q):
        sites = self.floating_sites(q)
        gravity = -self.p['g'] * sum(self.p['m' + key] * v[1][1] for key, v in sites.items())
        return (dot(self.force, sites['6'][1]) + self.Mw * self.K + gravity + self.spring(q)['torque']
                + self.motor.motor_state(q, 0, 0)['jointCoggingNm'])

    def potential(self, q, t=0, side='right'):
        sites = self.floating_sites(q)
        r = self.wheel_height(t, side)
        return (self.p['g'] * sum(self.p['m' + key] * (v[0][1] + r) for key, v in sites.items())
                + self.spring(q)['energy'] - self.force[0] * sites['6'][0][0]
                - self.force[1] * r - self.Mw * self.K * q
                + self.motor.motor_state(q, 0, 0)['coggingPotentialJ'])

    def actuation(self, q, velocity):
        command = self.motor.joint_command(self.c['hipTorqueNm'])
        friction = self.motor.motor_state(q, velocity, command)['jointFrictionNm']
        return command - self.c['dampingNms'] * velocity + friction

    def acceleration(self, q, velocity, t=0, side='right'):
        self.motor.check_step(velocity, self.c['dt'])
        M, derivative, B, _ = self.coefficients(q)
        self.motor.check_friction_step(M, self.c['dt'])
        if not self.motor.enabled:
            return (self.generalized(q) + self.c['hipTorqueNm'] - self.c['dampingNms'] * velocity
                    - .5 * derivative * velocity * velocity - B * self.input(t, side)['acceleration']) / M
        return (self.generalized(q) + self.actuation(q, velocity)
                - .5 * derivative * velocity * velocity - B * self.input(t, side)['acceleration']) / M

    def heave_acceleration(self, t, height, speed, side='right'):
        """Independently transformed h-coordinate equation used by Pymunk."""
        q = self.q_from_chassis(t, height, side)
        C = self.sites(q)['6']
        a, da = -C[1][1], -C[2][1]
        base = self.input(t, side)
        velocity = (speed - base['velocity']) / a
        self.motor.check_step(velocity, self.c['dt'])
        M, dM, B, _ = self.coefficients(q)
        self.motor.check_friction_step(M, self.c['dt'])
        H = M / (a * a)
        dH = dM / (a * a) - 2 * M * da / (a * a * a)
        cross = B / a - H
        force = (self.generalized(q) + self.actuation(q, velocity)) / a
        if not self.motor.enabled:
            force = (self.generalized(q) + self.c['hipTorqueNm'] - self.c['dampingNms'] * velocity) / a
        acceleration = (force - cross * base['acceleration'] - .5 * dH / a * (speed - base['velocity']) ** 2) / H
        return q, velocity, acceleration

    def reaction(self, t, q, velocity, acceleration, side='right'):
        _, _, B, dB = self.coefficients(q)
        return (self.total_mass * (self.input(t, side)['acceleration'] + self.p['g'])
                + B * acceleration + dB * velocity * velocity - self.force[1])

    def hash(self):
        identity = dict(params=self.p, motorConfig=self.motor.config) if self.motor_config_supplied else self.p
        return hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def observe(self, t, q, velocity, acceleration, actual=None, side='right'):
        sites = self.sites(q)
        spring = self.spring(q)
        base = self.input(t, side)
        M, _, Bcross, _ = self.coefficients(q)
        kinetic = .5 * M * velocity * velocity + Bcross * velocity * base['velocity'] + .5 * self.total_mass * base['velocity'] ** 2
        potential = self.potential(q, t, side)
        C, B = sites['6'][0], sites['5'][0]
        world = lambda p: [-p[0] * 1000, 0, p[1] * 1000]
        height, heave_v, heave_a = self.chassis(t, q, velocity, acceleration, side)
        translated = lambda p: world((p[0], p[1] + height))
        frame = dict(t=t, theta2=q / R, A=translated((0, 0)), B=translated(B), C=translated(C),
                     chassisZMm=height * 1000, wheelZMm=self.wheel_height(t, side) * 1000,
                     wheelAngle=self.K * (q - self.p['te'] * R) / R)
        if self.p['springEnabled']:
            frame.update(D=translated(mul(self.rotate(spring['D']), .001)), Q=translated(mul(self.rotate(spring['Q']), .001)))
        if actual:
            frame.update(actual)
        row = dict(t=t, theta2=q / R, velocityDegS=velocity / R, accelerationDegS2=acceleration / R,
                   Fs=spring['force'], tauStatic=-self.generalized(q), tauApplied=self.actuation(q, velocity),
                   kineticJ=kinetic, potentialJ=potential, energyJ=kinetic + potential,
                   CxMm=-C[0] * 1000, CzMm=(C[1] + height) * 1000,
                   chassisZMm=height * 1000, chassisVelocityMmS=heave_v * 1000,
                   chassisAccelerationMmS2=heave_a * 1000, wheelZMm=self.wheel_height(t, side) * 1000,
                   requestedInputMm=base['requested'] * 1000, appliedInputMm=base['applied'] * 1000,
                   inputVelocityMmS=base['velocity'] * 1000, inputAccelerationMmS2=base['acceleration'] * 1000,
                   inputReactionN=self.reaction(t, q, velocity, acceleration, side))
        if self.motor_config_supplied or self.c['hipRotorInertiaKgM2']>0:
            row.update(self.motor.motor_state(q, velocity, self.motor.joint_command(self.c['hipTorqueNm'])))
            row['legacyJointRotorKineticJ'] = .5 * self.c['hipRotorInertiaKgM2'] * velocity ** 2
        return row, frame
