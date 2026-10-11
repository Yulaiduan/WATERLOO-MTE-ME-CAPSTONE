"""Analytic 2:1 open-guide-belt geometry, material marks and force annotation.

Invocation: import build_loop, point_at, material_phase, material_dots and
tension_state from a browser/native rendering adapter. Inputs: hip/knee centres
in metres, pulley radii in metres, unwrapped angles in radians, lower-pulley
torque in N m and optional known slack-span pretension in N. World y points up;
the path is clockwise. Outputs: JSON-compatible tangencies, path samples,
arc-length stations and explicitly labelled derived force arrows.
Standard library only; no engine imports, force application or integration.
This visualization represents the existing ideal GearJoint torque proxy. Real
belt bearing loads, pretension, tooth engagement, stretch, friction, inertia and
structural stress are not included in that engine model. A torque determines
only Tplus-Tminus. Unknown pretension stays unknown; differential arrows are
torque-equivalent annotations, never measured or uniquely inferred tensions.
Radii default to illustrative 28/14 mm, not confirmed hardware dimensions.
"""
from __future__ import annotations

import math


HIP_RADIUS = .028
TAU = 2*math.pi
SCOPE = ('Analytic 2:1 open-belt visualization of the GearJoint torque proxy. '
         'Individual belt-span bearing forces are not applied to, or included '
         'in, engine pin-load results. No belt elasticity/friction/contact model.')


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number.')
    return float(value)


def _point(value, name):
    try:
        pair = tuple(value)
    except TypeError as error:
        raise ValueError(f'{name} must be an x/y pair.') from error
    if len(pair) != 2:
        raise ValueError(f'{name} must be an x/y pair.')
    return [_finite(pair[0], name+' x'), _finite(pair[1], name+' y')]


def _add(a, b):
    return [a[0]+b[0], a[1]+b[1]]


def _sub(a, b):
    return [a[0]-b[0], a[1]-b[1]]


def _scale(a, k):
    return [a[0]*k, a[1]*k]


def _cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def build_loop(A, B, hip_radius=HIP_RADIUS, knee_radius=None, samples=128):
    """Build exact tangencies and two clockwise arcs for the 2:1 guide.

    A is the hip centre, B the knee centre. The two span force units both point
    hip-to-knee; the minus span's *path* unit points knee-to-hip. Distinguishing
    these directions prevents an incorrect minus-span torque sign.
    """
    hip, knee = _point(A, 'Hip centre'), _point(B, 'Knee centre')
    rh = _finite(hip_radius, 'Hip radius')
    rk = rh/2 if knee_radius is None else _finite(knee_radius, 'Knee radius')
    if rh <= 0 or rk <= 0:
        raise ValueError('Pulley radii must be positive.')
    if not math.isclose(rh, 2*rk, rel_tol=1e-12, abs_tol=0.):
        raise ValueError('This guide requires hip:knee pulley radii of exactly 2:1.')
    if isinstance(samples, bool) or not isinstance(samples, int) or not 8 <= samples <= 4096:
        raise ValueError('Use 8 to 4096 path samples.')
    offset = _sub(knee, hip)
    distance = math.hypot(*offset)
    if distance <= rh+rk:
        raise ValueError('Pulley circles must be separated without overlap or contact.')
    e = _scale(offset, 1/distance)
    n = [-e[1], e[0]]
    delta = (rh-rk)/distance
    beta = math.sqrt(1-delta*delta)
    qplus = _add(_scale(e, delta), _scale(n, beta))
    qminus = _sub(_scale(e, delta), _scale(n, beta))
    hp, kp = _add(hip, _scale(qplus, rh)), _add(knee, _scale(qplus, rk))
    hm, km = _add(hip, _scale(qminus, rh)), _add(knee, _scale(qminus, rk))
    plus_unit = [qplus[1], -qplus[0]]
    minus_path_unit = [qminus[1], -qminus[0]]
    minus_force_unit = _scale(minus_path_unit, -1.)
    alpha = math.atan2(e[1], e[0])
    gamma = math.acos(delta)
    span_length = distance*beta
    knee_arc_length = 2*gamma*rk
    hip_arc_length = (TAU-2*gamma)*rh
    segments = [
        {'name': 'plus_span', 'kind': 'span', 'start': 0., 'length': span_length,
         'a': hp, 'b': kp, 'unit': plus_unit},
        {'name': 'knee_arc', 'kind': 'arc', 'start': span_length, 'length': knee_arc_length,
         'centre': knee, 'radius': rk, 'angle_start': alpha+gamma, 'sweep': -2*gamma,
         'a': kp, 'b': km},
        {'name': 'minus_span', 'kind': 'span', 'start': span_length+knee_arc_length,
         'length': span_length, 'a': km, 'b': hm, 'unit': minus_path_unit},
        {'name': 'hip_arc', 'kind': 'arc', 'start': 2*span_length+knee_arc_length,
         'length': hip_arc_length, 'centre': hip, 'radius': rh,
         'angle_start': alpha-gamma, 'sweep': -(TAU-2*gamma), 'a': hm, 'b': hp},
    ]
    loop = {'hip': hip, 'knee': knee, 'hip_radius': rh, 'knee_radius': rk,
            'ratio': rh/rk, 'centre_distance': distance, 'carrier_angle': alpha,
            'delta': delta, 'gamma': gamma,
            'length': 2*span_length+knee_arc_length+hip_arc_length,
            'span_length': span_length, 'segments': segments,
            'tangencies': {'hip_plus': hp, 'knee_plus': kp, 'knee_minus': km, 'hip_minus': hm},
            'normals': {'plus': qplus, 'minus': qminus},
            'force_units': {'plus': plus_unit, 'minus': minus_force_unit},
            'direction': 'clockwise', 'dimension_status': 'illustrative editable radii',
            'engine_bearing_loads_included': False, 'scope': SCOPE}
    loop['points'] = [point_at(loop, j*loop['length']/samples) for j in range(samples)]+[hp[:]]
    return loop


def station_at(loop, s):
    """Return a periodic arc-length station, point and clockwise unit tangent."""
    wrapped = _finite(s, 'Belt arc-length station') % loop['length']
    for segment in loop['segments']:
        if wrapped < segment['start']+segment['length'] or segment is loop['segments'][-1]:
            along = wrapped-segment['start']
            if segment['kind'] == 'span':
                point = _add(segment['a'], _scale(segment['unit'], along))
                tangent = segment['unit'][:]
            else:
                angle = segment['angle_start']-along/segment['radius']
                radial = [math.cos(angle), math.sin(angle)]
                point = _add(segment['centre'], _scale(radial, segment['radius']))
                tangent = [radial[1], -radial[0]]
            return {'point': point, 'tangent': tangent, 'segment': segment['name'], 's': wrapped}
    raise ValueError('Invalid belt loop segments.')


def point_at(loop, s):
    """World x/y point at signed clockwise arc-length s (metres), periodic."""
    return station_at(loop, s)['point']


def material_phase(upper_angle, initial_upper_angle, hip_radius=HIP_RADIUS):
    """Clockwise material offset for a fixed hip pulley, using unwrapped angles.

    Carrier angle alpha is the upper-link angle. Offset=rH*(alpha-alpha_ref)
    cancels carrier rotation on the fixed hip wrap; on the knee wrap it gives
    absolute pulley rotation -delta(alpha), or +delta(theta) for this leg.
    No wall-clock animation term belongs in this no-slip phase.
    """
    current = _finite(upper_angle, 'Upper-link angle')
    initial = _finite(initial_upper_angle, 'Initial upper-link angle')
    radius = _finite(hip_radius, 'Hip radius')
    if radius <= 0:
        raise ValueError('Hip radius must be positive.')
    return radius*(current-initial)


def material_dots(loop, phase, count=36):
    """Equally spaced material marks, driven by pose-dependent belt phase."""
    phase = _finite(phase, 'Belt material phase')
    if isinstance(count, bool) or not isinstance(count, int) or not 2 <= count <= 2048:
        raise ValueError('Use 2 to 2048 material marks.')
    return [point_at(loop, phase+j*loop['length']/count) for j in range(count)]


def tension_state(loop, lower_torque, pretension=None):
    """Derived span-force annotation; optional pretension is the slack-span load.

    lower_torque is signed torque *on the lower knee pulley*, positive CCW.
    Tplus-Tminus=lower_torque/rK. If slack-span tension is known, both spans
    follow from it; otherwise only their difference is reported. Unknown-case
    arrows use the differential contribution alone, with explicit labels and
    no claim that the selected zero baseline is the real slack-span tension.
    All arrows are visualization data; this function applies no engine force.
    """
    torque = _finite(lower_torque, 'Lower-pulley torque')
    known = pretension is not None
    base = _finite(pretension, 'Slack-span pretension') if known else 0.
    if base < 0:
        raise ValueError('Known slack-span pretension must be nonnegative.')
    difference = torque/loop['knee_radius']
    plus, minus = base+max(difference, 0.), base+max(-difference, 0.)
    arrows = []
    for span, magnitude in (('plus', plus), ('minus', minus)):
        force = _scale(loop['force_units'][span], magnitude)
        arrows.append({'body': 'hip', 'span': span,
                       'point': loop['tangencies']['hip_'+span][:], 'force_N': force,
                       'magnitude_N': magnitude, 'torque_equivalent': not known})
        arrows.append({'body': 'knee', 'span': span,
                       'point': loop['tangencies']['knee_'+span][:], 'force_N': _scale(force, -1.),
                       'magnitude_N': magnitude, 'torque_equivalent': not known})
    hip_force = [sum(arrow['force_N'][axis] for arrow in arrows if arrow['body'] == 'hip') for axis in (0, 1)]
    knee_force = _scale(hip_force, -1.)
    hip_torque = sum(_cross(_sub(arrow['point'], loop['hip']), arrow['force_N']) for arrow in arrows if arrow['body'] == 'hip')
    knee_torque = sum(_cross(_sub(arrow['point'], loop['knee']), arrow['force_N']) for arrow in arrows if arrow['body'] == 'knee')
    carrier_torque = _cross(_sub(loop['knee'], loop['hip']), knee_force)
    return {'pretension_known': known, 'pretension_N': base if known else None,
            'differential_N': difference,
            'tension_plus_N': plus if known else None, 'tension_minus_N': minus if known else None,
            'force_arrows': arrows, 'hip_torque_Nm': hip_torque, 'knee_torque_Nm': knee_torque,
            'carrier_torque_Nm': carrier_torque,
            'hip_resultant_N': hip_force if known else None,
            'knee_resultant_N': knee_force if known else None,
            'torque_equivalent_hip_resultant_N': hip_force if not known else None,
            'torque_equivalent_knee_resultant_N': knee_force if not known else None,
            'legend': ('Derived span tensions using supplied slack-span pretension; bearing loads are outside the engine proxy.'
                       if known else 'Torque-equivalent tension-difference arrows only. Pretension and actual total span/bearing loads are unknown.'),
            'engine_bearing_loads_included': False, 'scope': SCOPE}
