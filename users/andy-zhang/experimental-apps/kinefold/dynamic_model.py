"""Exact builder-linked V4 geometry and fixed-hip generalized dynamics.

Imported by dynamics.py; inputs are the complete builder mm/deg/kg/N design and
explicit run configuration. Internal positions are source-horizontal/up in m,
angles radians, inertias kg m²; exported coordinates are Kinefold x/y/z in mm.
Outputs geometry, generalized mass, forces and conservative potential in SI.
Experimental ideal nonslip belts, fixed hip/drive shaft, prescribed constant
wheel force; no ground contact, chassis translation, friction or hardware claim.
"""
import hashlib
import json
import math

R = math.pi / 180
TAU = 2 * math.pi
NUMERIC_KEYS = ('L2 L3 ra rb rc rd re rf rw alpha phi0 te tc m1 m2 m3 m5 m6 g beta Fn Ft Fx Fz Tab0 Tcd0 Tef0 springK hornR Sv rs p0 nu Su theta2').split()
BOUNDS = {'duration': (.05, 30), 'dt': (.0001, .01), 'outputHz': (1, 1000),
          'initialVelocityDegS': (-720, 720), 'hipTorqueNm': (-10000, 10000),
          'dampingNms': (0, 10000), 'hipRotorInertiaKgM2': (0, 1000),
          'I2': (0, 1000), 'I3': (0, 1000), 'I5': (0, 1000), 'I6': (0, 1000),
          'iterations': (10, 500)}


def defaults():
    return dict(fixture='fixed-hip', duration=2, dt=.001, outputHz=100,
                initialVelocityDegS=0, hipTorqueNm=0, dampingNms=.1,
                hipRotorInertiaKgM2=.05, inertiaModel='uniform-rods-discs',
                I2=0, I3=0, I5=0, I6=0, iterations=80)


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
    if config['fixture'] != 'fixed-hip' or config['inertiaModel'] not in ('uniform-rods-discs', 'custom'):
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


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, n):
    return (a[0] * n, a[1] * n)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


class Model:
    def __init__(self, params, config):
        validate(params, config)
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
        self.force, self.Mw = self.loads()
        self.route = self.exit_route() if p['springEnabled'] else dict(applied=0, shift=0)
        self.reference_payout = self.geometry(math.pi / 2, reference=True)['payout'] if p['springEnabled'] else 0
        if p['springEnabled']:
            for q in self.candidates(self.lo, self.hi):
                self.geometry(q)
        if self.mass(self.q0)[0] <= 1e-12:
            raise ValueError('Moving inertia is zero. Enter positive moving masses/inertias or an explicit hip rotor inertia.')

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
            f = (0, sum(p[k] for k in ('m1', 'm2', 'm3', 'm5', 'm6')) * p['g']) if p['loadMode'] == 'weight' else (-p['Fx'], p['Fz'])
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
        sites = self.sites(q)
        M = sum(self.p['m' + key] * dot(v[1], v[1]) + self.I[key] * self.rates[key] ** 2 for key, v in sites.items())
        derivative = sum(2 * self.p['m' + key] * dot(v[1], v[2]) for key, v in sites.items())
        return M, derivative

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
        sites = self.sites(q)
        gravity = -self.p['g'] * sum(self.p['m' + key] * v[1][1] for key, v in sites.items())
        return dot(self.force, sites['6'][1]) + self.Mw * self.K + gravity + self.spring(q)['torque']

    def potential(self, q):
        sites = self.sites(q)
        return (self.p['g'] * sum(self.p['m' + key] * v[0][1] for key, v in sites.items())
                + self.spring(q)['energy'] - dot(self.force, sites['6'][0]) - self.Mw * self.K * q)

    def acceleration(self, q, velocity):
        M, derivative = self.mass(q)
        return (self.generalized(q) + self.c['hipTorqueNm'] - self.c['dampingNms'] * velocity - .5 * derivative * velocity * velocity) / M

    def hash(self):
        return hashlib.sha256(json.dumps(self.p, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def observe(self, t, q, velocity, acceleration, actual=None):
        sites = self.sites(q)
        spring = self.spring(q)
        kinetic = .5 * self.mass(q)[0] * velocity * velocity
        potential = self.potential(q)
        C, B = sites['6'][0], sites['5'][0]
        world = lambda p: [-p[0] * 1000, 0, p[1] * 1000]
        frame = dict(t=t, theta2=q / R, A=[0, 0, 0], B=world(B), C=world(C), wheelAngle=self.K * (q - self.p['te'] * R) / R)
        if self.p['springEnabled']:
            frame.update(D=world(mul(self.rotate(spring['D']), .001)), Q=world(mul(self.rotate(spring['Q']), .001)))
        if actual:
            frame.update(actual)
        row = dict(t=t, theta2=q / R, velocityDegS=velocity / R, accelerationDegS2=acceleration / R,
                   Fs=spring['force'], tauStatic=-self.generalized(q), tauApplied=self.c['hipTorqueNm'] - self.c['dampingNms'] * velocity,
                   kineticJ=kinetic, potentialJ=potential, energyJ=kinetic + potential, CxMm=-C[0] * 1000, CzMm=C[1] * 1000)
        return row, frame
