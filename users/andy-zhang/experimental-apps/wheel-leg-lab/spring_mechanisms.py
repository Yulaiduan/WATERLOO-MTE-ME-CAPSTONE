"""Reusable geometry and passive force laws for experimental suspension presets.

Invocation: import geometry(theta, config), geometry_from_bodies(bodies, config),
spring_law(input_length, input_speed, config), or generalized(theta,speed,config).
Inputs: metres, seconds, radians, N/m and N s/m; preset angular offsets degrees.
Outputs: local/world force sites, scalar input span/Jacobian, coil travel/load,
energy and generalized force. Standard library only; no Pymunk dependency.
Limitations: illustrative editable geometry, ideal massless drum/rigid pullrod/
zero-stretch rope with 100% transmission efficiency. No cable sag, friction,
coil solid height, real bellcrank bearings, contact or hardware calibration.
Theta is the equal-link angle from horizontal, not an unspecified 'leg extension'.
"""
from __future__ import annotations

import math
from copy import deepcopy


MECHANISM_DEFAULTS = {
    'spring_integration': 'point_force',
    'spring_topology': 'legacy_tip', 'spring_mode': 'captured',
    'spring_transmission': 'direct', 'spring_pulley_radius': .04,
    'spring_direction': 1., 'spring_input_ref': .20, 'spring_coil_ref': .20,
    'spring_upper_fraction': .5, 'spring_lower_fraction': .5,
    'spring_bellcrank_radius': .05, 'spring_bellcrank_offset_deg': 135.,
    'spring_chassis_x': .12, 'spring_chassis_y': .05,
    'spring_force_law': 'hooke', 'spring_effective_free_length': 0.,
    'aux_spring_enabled': False, 'aux_stiffness': 8000., 'aux_damping': 100.,
    'aux_mode': 'captured', 'aux_rest_length': .28, 'aux_auto_rest': True,
    'chassis_shape_enabled': False, 'guide_pulleys_visible': False,
    'guide_hip_radius': .028,
}

CATALOG = {
    'legacy_tip': {'label': 'Original hip-to-extension-tip spring', 'kind': 'direct',
                   'defaults': {'spring_mode': 'captured', 'spring_transmission': 'direct'},
                   'description': 'Hip pivot to the lower-link extension tip; retains the original bilateral spring.'},
    'hip_pulley': {'label': 'Hip pulley', 'kind': 'pulley',
                   'defaults': {'spring_mode': 'extension', 'spring_transmission': 'direct'},
                   'description': 'Massless hip drum payout, with tangent cable forces on upper link and chassis.'},
    'knee_pulley': {'label': 'Knee pulley', 'kind': 'pulley',
                    'defaults': {'spring_mode': 'extension', 'spring_transmission': 'direct'},
                    'description': 'Massless knee drum payout using relative knee rotation; tangent force pair on both links.'},
    'direct_scissor': {'label': 'Direct scissor spring', 'kind': 'direct',
                       'defaults': {'spring_mode': 'compression', 'spring_transmission': 'direct'},
                       'description': 'Spring between editable fractions along upper and lower links.'},
    'hip_bellcrank': {'label': 'Hip bellcrank', 'kind': 'direct',
                      'defaults': {'spring_mode': 'extension', 'spring_transmission': 'direct',
                                   'spring_bellcrank_offset_deg': 135.},
                      'description': 'Rigid crank on upper link at hip; spring to an editable chassis mount.'},
    'knee_bellcrank': {'label': 'Knee bellcrank', 'kind': 'direct',
                       'defaults': {'spring_mode': 'extension', 'spring_transmission': 'direct',
                                    'spring_bellcrank_offset_deg': 180.},
                       'description': 'Rigid crank on lower link at knee; spring to an editable upper-link point.'},
    'chassis_direct': {'label': 'Direct to chassis', 'kind': 'direct',
                       'defaults': {'spring_mode': 'compression', 'spring_transmission': 'direct'},
                       'description': 'Editable lower-link point to a chassis mount.'},
    'knee_capture': {'label': 'Internal knee pulley / captured pull-through coil', 'kind': 'pulley',
                     'defaults': {'spring_mode': 'compression', 'spring_transmission': 'pullrod'},
                     'description': 'Ideal internal knee payout pulls a rigid rod through a compression coil; external force is tension.'},
    'gravity_balance': {'label': 'Constant-lift / zero-effective-length spring', 'kind': 'direct',
                       'defaults': {'spring_mode': 'extension', 'spring_transmission': 'direct',
                                    'spring_force_law': 'zero_effective',
                                    'spring_chassis_x': 0., 'spring_chassis_y': -.15,
                                    'spring_upper_fraction': .5},
                       'description': 'Hip-to-upper-link tension proportional to anchor span; vertical mount geometry converts it to constant generalized lift. Physical coil has positive free length through an ideal preload/routing emulation.'},
}
for _entry in CATALOG.values():
    _entry['status'] = 'Illustrative editable preset; dimensions are not confirmed hardware.'
    _entry['defaults'].update(stiffness=8000., damping=100.)
CATALOG['legacy_tip']['defaults'].update(stiffness=20000., damping=500.)
CATALOG['hip_pulley']['defaults'].update(spring_pulley_radius=.08, damping=500.)
CATALOG['knee_pulley']['defaults'].update(damping=500.)
CATALOG['knee_capture']['defaults'].update(damping=500.)
CATALOG['hip_bellcrank']['defaults'].update(spring_bellcrank_radius=.08, damping=500.)
CATALOG['knee_bellcrank']['defaults'].update(stiffness=24000., damping=1000.)


def apply_preset(config, topology):
    """Return a copy with demo geometry/law settings for a selected topology."""
    if topology not in CATALOG:
        raise ValueError('Unknown spring topology.')
    result = deepcopy(config)
    result.update(MECHANISM_DEFAULTS)
    result.update(CATALOG[topology]['defaults'])
    result['spring_topology'] = topology
    return result


def mechanism_config(c):
    """Resolve and validate explicit experimental mechanism options."""
    resolved = {key: c.get(key, default) for key, default in MECHANISM_DEFAULTS.items()}
    if resolved['spring_topology'] not in CATALOG:
        raise ValueError('Unknown spring topology.')
    if resolved['spring_integration'] not in ('point_force', 'native_legacy'):
        raise ValueError('Spring integration must be point_force or native_legacy.')
    if resolved['spring_integration'] == 'native_legacy' and not (
            resolved['spring_topology'] == 'legacy_tip' and resolved['spring_mode'] == 'captured'
            and resolved['spring_transmission'] == 'direct' and resolved['spring_force_law'] == 'hooke'):
        raise ValueError('native_legacy diagnostic requires legacy_tip/captured/direct/hooke.')
    if resolved['spring_mode'] not in ('compression', 'extension', 'captured'):
        raise ValueError('Spring mode must be compression, extension or captured.')
    if resolved['spring_transmission'] not in ('direct', 'pullrod', 'ideal_rope'):
        raise ValueError('Spring transmission must be direct, pullrod or ideal_rope.')
    if resolved['spring_force_law'] not in ('hooke', 'zero_effective'):
        raise ValueError('Spring force law must be hooke or zero_effective.')
    if resolved['aux_mode'] not in ('compression', 'extension', 'captured'):
        raise ValueError('Auxiliary spring mode must be compression, extension or captured.')
    for key, default in MECHANISM_DEFAULTS.items():
        value = resolved[key]
        if isinstance(default, bool):
            if not isinstance(value, bool):
                raise ValueError(f'{key} must be boolean.')
        elif isinstance(default, (int, float)):
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError(f'{key} must be finite.')
    if resolved['spring_direction'] not in (-1., 1.):
        raise ValueError('Spring payout direction must be +1 or -1.')
    for key in ('spring_pulley_radius', 'spring_bellcrank_radius', 'spring_input_ref', 'spring_coil_ref'):
        if resolved[key] <= 0:
            raise ValueError(f'{key} must be positive.')
    for key in ('spring_upper_fraction', 'spring_lower_fraction'):
        if not 0 <= resolved[key] <= 1:
            raise ValueError(f'{key} must be between zero and one.')
    if not 0 <= resolved['spring_effective_free_length'] <= 1:
        raise ValueError('Effective input free length must be between zero and one metre.')
    if not 0 <= resolved['aux_stiffness'] <= 100000 or not 0 <= resolved['aux_damping'] <= 2000:
        raise ValueError('Auxiliary stiffness/damping must be nonnegative and at most 100000 N/m / 2000 N s/m.')
    if not .005 <= resolved['aux_rest_length'] <= 1:
        raise ValueError('Auxiliary free length must be between 0.005 and one metre.')
    if resolved['aux_spring_enabled'] and resolved['spring_topology'] != 'gravity_balance':
        raise ValueError('The auxiliary ride spring is currently supported only with the gravity_balance primary stage.')
    if not .005 <= resolved['guide_hip_radius'] <= .1:
        raise ValueError('Guide hip radius must be between 0.005 and 0.1 metre; knee radius is half for the ideal 2:1 guide.')
    L, e = c['length'], c['extension']
    if not (math.isfinite(L) and math.isfinite(e) and 0 < e < L):
        raise ValueError('Require finite link length and 0 < extension < length.')
    if resolved['guide_pulleys_visible'] and 1.5*resolved['guide_hip_radius']>=L:
        raise ValueError('Visible guide pulleys must not overlap: use 1.5 times hip radius < link length.')
    return resolved


def _add(a, b): return [a[0]+b[0], a[1]+b[1]]
def _sub(a, b): return [a[0]-b[0], a[1]-b[1]]
def _scale(a, s): return [a[0]*s, a[1]*s]
def _dot(a, b): return a[0]*b[0]+a[1]*b[1]
def _perp(a): return [-a[1], a[0]]
def _rot(a, angle):
    co, si = math.cos(angle), math.sin(angle)
    return [co*a[0]-si*a[1], si*a[0]+co*a[1]]


def _pose(body):
    """Accept a plain pose dictionary or an actual rigid-body object."""
    if isinstance(body, dict):
        return list(body['position']), float(body['angle'])
    return list(body.position), float(body.angle)


def _world(body, local):
    position, angle = _pose(body)
    return _add(position, _rot(local, angle))


def _local(body, world):
    position, angle = _pose(body)
    return _rot(_sub(world, position), -angle)


def _point_velocity(body, world):
    position, _ = _pose(body)
    if isinstance(body, dict):
        if 'velocity' not in body or 'angular_velocity' not in body:
            return None
        velocity, spin = body['velocity'], body['angular_velocity']
    else:
        velocity, spin = body.velocity, body.angular_velocity
    return _add(velocity, _scale(_perp(_sub(world, position)), spin))


def _angular_velocity(body):
    if isinstance(body, dict):
        return body.get('angular_velocity')
    return float(body.angular_velocity)


def equal_poses(theta, c, theta_speed=0., base_height=0., base_speed=0.):
    """Analytical equal-link world poses (y up), also useful for virtual work."""
    L, e = c['length'], c['extension']
    sn, cs = math.sin(theta), math.cos(theta)
    lam = (L+e)/2
    return {
        'hip': {'position': [0., base_height+2*L*sn], 'angle': 0.,
                'velocity': [0., base_speed+2*L*cs*theta_speed], 'angular_velocity': 0.},
        'upper': {'position': [L/2*cs, base_height+1.5*L*sn], 'angle': -theta,
                  'velocity': [-L/2*sn*theta_speed, base_speed+1.5*L*cs*theta_speed],
                  'angular_velocity': -theta_speed},
        'lower': {'position': [lam*cs, base_height+lam*sn], 'angle': theta-math.pi,
                  'velocity': [-lam*sn*theta_speed, base_speed+lam*cs*theta_speed],
                  'angular_velocity': theta_speed},
    }


def direct_anchors(c):
    """Endpoint body keys and body-local metres for direct/crank topologies."""
    s = mechanism_config(c)
    topology = s['spring_topology']
    L, e = c['length'], c['extension']
    upper = [(s['spring_upper_fraction']-.5)*L, 0.]
    lower = [s['spring_lower_fraction']*L-(L-e)/2, 0.]
    mount = [s['spring_chassis_x'], s['spring_chassis_y']]
    arm = _scale([math.cos(math.radians(s['spring_bellcrank_offset_deg'])),
                  math.sin(math.radians(s['spring_bellcrank_offset_deg']))], s['spring_bellcrank_radius'])
    if topology == 'legacy_tip':
        a, b = ('hip', [0., 0.]), ('lower', [-(L+e)/2, 0.])
    elif topology == 'direct_scissor':
        a, b = ('upper', upper), ('lower', lower)
    elif topology == 'hip_bellcrank':
        a, b = ('hip', mount), ('upper', _add([-L/2, 0.], arm))
    elif topology == 'knee_bellcrank':
        a, b = ('upper', upper), ('lower', _add([-(L-e)/2, 0.], arm))
    elif topology == 'chassis_direct':
        a, b = ('hip', mount), ('lower', lower)
    elif topology == 'gravity_balance':
        a, b = ('hip', mount), ('upper', upper)
    else:
        raise ValueError('A pulley topology uses payout and tangent force sites, not direct spring anchors.')
    return {'a': {'body': a[0], 'local': a[1]}, 'b': {'body': b[0], 'local': b[1]}}


def _force_site(body_key, world, direction, bodies):
    return {'body': body_key, 'point': list(world), 'world': list(world),
            'local': _local(bodies[body_key], world), 'direction': list(direction)}


def geometry_from_bodies(bodies, c):
    """Actual pose geometry and force sites; no rigid-body dynamics are imported.

    For direct geometry, length and speed come from the supplied actual poses.
    The reported theta Jacobian uses the ideal equal-2:1 coordinate; a drifting
    arbitrary mechanism need not have that single coordinate. Input speed is
    None if plain pose dictionaries omit velocities, rather than assumed zero.
    """
    s = mechanism_config(c)
    topology = s['spring_topology']
    L, e = c['length'], c['extension']
    _, au = _pose(bodies['upper'])
    _, al = _pose(bodies['lower'])
    _, ah = _pose(bodies['hip'])
    theta = (al-au+math.pi)/2
    qref = math.radians(c['theta'])
    A = _world(bodies['upper'], [-L/2, 0.])
    B = _world(bodies['upper'], [L/2, 0.])
    if CATALOG[topology]['kind'] == 'direct':
        anchors = direct_anchors(c)
        a, b = anchors['a'], anchors['b']
        wa = _world(bodies[a['body']], a['local'])
        wb = _world(bodies[b['body']], b['local'])
        delta = _sub(wb, wa)
        length = math.hypot(*delta)
        if length < 1e-10:
            raise ValueError('Spring anchors coincide; select nondegenerate mount/crank geometry.')
        normal = _scale(delta, 1/length)
        va, vb = _point_velocity(bodies[a['body']], wa), _point_velocity(bodies[b['body']], wb)
        speed = None if va is None or vb is None else _dot(normal, _sub(vb, va))
        ideal = equal_poses(theta, c, theta_speed=1.)
        ia = _world(ideal[a['body']], a['local'])
        ib = _world(ideal[b['body']], b['local'])
        idir = _scale(_sub(ib, ia), 1/math.hypot(*_sub(ib, ia)))
        J = _dot(idir, _sub(_point_velocity(ideal[b['body']], ib), _point_velocity(ideal[a['body']], ia)))
        a = dict(a, world=wa)
        b = dict(b, world=wb)
        sites = [_force_site(a['body'], wa, normal, bodies),
                 _force_site(b['body'], wb, _scale(normal, -1.), bodies)]
        anchors = {'a': a, 'b': b}
    else:
        direction, radius = s['spring_direction'], s['spring_pulley_radius']
        if topology == 'hip_pulley':
            # Unit tension acts +x in the chassis frame at the selected tangent.
            u, n = _rot([1., 0.], ah), _rot([0., 1.], ah)
            pa = _add(A, _scale(n, direction*radius))
            pb = _add(pa, _scale(u, s['spring_input_ref']))
            sites = [_force_site('upper', pa, u, bodies),
                     _force_site('hip', pb, _scale(u, -1.), bodies)]
            angle_delta = (au-ah)+qref
            length = s['spring_input_ref']+direction*radius*angle_delta
            J = -direction*radius
            wu, wh = _angular_velocity(bodies['upper']), _angular_velocity(bodies['hip'])
            speed = None if wu is None or wh is None else direction*radius*(wu-wh)
        else:
            # Knee tangent lies on +direction*n. Cable pulls LOWER toward hip;
            # UPPER receives the opposite force on the same tangent line.
            u, n = _rot([1., 0.], au), _rot([0., 1.], au)
            pa = _add(B, _scale(n, direction*radius))
            pb = _sub(pa, _scale(u, L))
            sites = [_force_site('lower', pa, _scale(u, -1.), bodies),
                     _force_site('upper', pb, u, bodies)]
            angle_delta = al-au+math.pi-2*qref
            length = s['spring_input_ref']-direction*radius*angle_delta
            J = -2*direction*radius
            wl, wu = _angular_velocity(bodies['lower']), _angular_velocity(bodies['upper'])
            speed = None if wl is None or wu is None else -direction*radius*(wl-wu)
        anchors = {'a': {'body': sites[0]['body'], 'local': sites[0]['local'], 'world': pa},
                   'b': {'body': sites[1]['body'], 'local': sites[1]['local'], 'world': pb}}
    if length <= 0:
        raise ValueError('Ideal spring input payout crossed zero; increase input reference span or reduce travel.')
    return {'topology': topology, 'kind': CATALOG[topology]['kind'],
            'theta_rad': theta, 'input_length': length, 'input_speed': speed,
            'jacobian': J, 'jacobian_basis': 'ideal equal-link 2:1 theta coordinate',
            'anchors': anchors, 'force_sites': sites, 'physical_guide_ratio': 2,
            'transmission_efficiency': 1., 'rope_stretch': 0.,
            'dimension_status': CATALOG[topology]['status']}


def geometry(theta, c):
    """Ideal coordinate geometry, with analytic d(input span)/d(theta)."""
    if not isinstance(theta, (float, int)) or not math.isfinite(theta):
        raise ValueError('Theta must be finite radians.')
    return geometry_from_bodies(equal_poses(theta, c), c)


def spring_law(input_length, input_speed, c, input_reference=None):
    """Passive coil force projected onto the input coordinate.

    Positive tension contracts the input span; the applied generalized force is
    -tension*dlength/dtheta. Direct transmission has coil travel=input travel.
    Pullrod/ideal_rope maps increasing input span to decreasing coil length.
    Unloaded one-sided coils relax to free length; nominal_coil_length records
    the geometric span separately. A rope never pushes and has no damper when
    slack. Extension-only plus this compression pull-through rope is slack;
    an extension coil needs direct routing or an explicitly different mechanism.
    zero_effective is an ideal preload/routing emulation: physical coil length
    is free_length + eta*(input_length-effective_input_free_length), while its
    elastic input tension is k*(input_length-effective_input_free_length).
    Physical free length stays positive and is not the effective input offset.
    """
    s = mechanism_config(c)
    numbers = (input_length, input_speed, c['stiffness'], c['damping'], c['rest_length'])
    if not all(isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v) for v in numbers):
        raise ValueError('Spring-law inputs must be finite SI numbers.')
    if input_length <= 0 or c['rest_length'] <= 0 or c['stiffness'] < 0 or c['damping'] < 0:
        raise ValueError('Input/free length must be positive and stiffness/damping nonnegative.')
    if input_reference is None:
        input_reference = (s['spring_input_ref'] if CATALOG[s['spring_topology']]['kind'] == 'pulley'
                           else geometry(math.radians(c['theta']), c)['input_length'])
    if not isinstance(input_reference, (float, int)) or not math.isfinite(input_reference) or input_reference <= 0:
        raise ValueError('Input reference must be positive and finite metres.')
    eta = 1. if s['spring_transmission'] == 'direct' else -1.
    if s['spring_force_law'] == 'zero_effective':
        # Effective free length belongs to the INPUT force law. The actual
        # coil still has positive free length; ideal routing/preload shifts its
        # physical travel so k*coil_strain produces k*(span-effective_free).
        nominal = c['rest_length']+eta*(input_length-s['spring_effective_free_length'])
    else:
        nominal = input_length if eta == 1. else s['spring_coil_ref']-(input_length-input_reference)
    if nominal <= 0:
        raise ValueError('Nominal coil length crossed zero; increase coil reference length or reduce input travel.')
    delta = nominal-c['rest_length']
    mode, rope = s['spring_mode'], s['spring_transmission'] == 'ideal_rope'
    engaged = (mode == 'captured' or (mode == 'compression' and delta <= 0)
               or (mode == 'extension' and delta >= 0))
    if rope:
        engaged = engaged and mode in ('compression', 'captured') and delta <= 0
    coil_length = nominal if engaged else c['rest_length']
    coil_speed = eta*input_speed if engaged else 0.
    elastic_coil = c['stiffness']*delta if engaged else 0.
    total_coil = elastic_coil+c['damping']*coil_speed if engaged else 0.
    if mode == 'compression':
        total_coil = min(0., total_coil)
    elif mode == 'extension':
        total_coil = max(0., total_coil)
    elastic_input = eta*elastic_coil
    tension = eta*total_coil
    if rope:
        tension = max(0., tension)
        total_coil = eta*tension
    damping_input = tension-elastic_input
    energy = .5*c['stiffness']*delta**2 if engaged else 0.
    return {'tension': tension, 'elastic_tension': elastic_input,
            'damper_tension': damping_input, 'coil_length': coil_length,
            'nominal_coil_length': nominal, 'coil_speed': coil_speed,
            'coil_tension': total_coil, 'coil_load': abs(total_coil),
            'coil_elastic_load': abs(elastic_coil), 'energy': energy,
            'denergy_dinput': elastic_input, 'coil_jacobian': eta if engaged else 0.,
            'engaged': bool(engaged), 'slack': not bool(engaged),
            'dissipation_rate': damping_input*input_speed,
            'input_reference': input_reference, 'transmission_efficiency': 1.,
            'rope_stretch': 0., 'mode': mode, 'transmission': s['spring_transmission'],
            'force_law': s['spring_force_law'],
            'effective_free_length': s['spring_effective_free_length']}


def calibrate_zero_effective_rate(c, needed, geom):
    """Resolve k in-place from initial generalized demand, preserving coil free length.

    One-sided/routing incompatibility is tested using the actual passive law.
    This is a declared experimental rate calibration, not hidden coil preload.
    Zero demand resolves zero rate; negative/unbounded rates fail explicitly.
    """
    unit = spring_law(geom['input_length'], 0., {**c, 'stiffness': 1., 'damping': 0.},
                      geom['input_length'])
    unit_force = -unit['elastic_tension']*geom['jacobian']
    if abs(unit_force) < 1e-10:
        if abs(needed) > 1e-9:
            raise ValueError('Zero-effective spring is slack or has zero leverage; choose compatible coil/routing/mounts or disable automatic balance.')
        rate = 0.
    else:
        rate = needed/unit_force
    if not math.isfinite(rate) or rate < 0. or rate > 100000.:
        raise ValueError('Zero-effective rate calibration requires a nonnegative stiffness no greater than 100000 N/m; change geometry/routing or disable automatic balance.')
    c['stiffness'] = rate
    return rate


def mechanism_metadata(c, input_reference):
    """Return portable law, rate-calibration and ideal constant-lift eligibility."""
    s = mechanism_config(c)
    mode_ok = (s['spring_mode'] in ('extension', 'captured') if s['spring_transmission'] == 'direct'
               else s['spring_mode'] in ('compression', 'captured'))
    eligible = (s['spring_topology'] == 'gravity_balance'
                and s['spring_force_law'] == 'zero_effective'
                and s['spring_effective_free_length'] == 0.
                and abs(s['spring_chassis_x']) < 1e-12 and s['spring_chassis_y'] < 0.
                and s['spring_upper_fraction'] > 0. and mode_ok)
    notes = []
    if s['spring_topology'] == 'gravity_balance' and not eligible:
        notes.append('Constant lift requires zero effective input free length, a downward vertical chassis mount and compatible tension-producing routing. This edited arrangement lacks exact constant lift; automatic calibration, if enabled, balances only the initial pose.')
    return {'topology': s['spring_topology'], 'mode': s['spring_mode'],
            'pymunk_integration': s['spring_integration'],
            'transmission': s['spring_transmission'], 'force_law': s['spring_force_law'],
            'effective_free_length_m': s['spring_effective_free_length'],
            'physical_coil_free_length_m': c['rest_length'],
            'resolved_stiffness_N_m': c['stiffness'], 'input_reference_m': input_reference,
            'automatic_balance': ('rate_calibration' if s['spring_force_law'] == 'zero_effective' else 'free_length_preload') if c['balance_spring'] else 'manual',
            'constant_lift_eligible': eligible,
            'constant_elastic_lift_N': (c['stiffness']*(-s['spring_chassis_y'])*s['spring_upper_fraction']/2 if eligible else None),
            'description': CATALOG[s['spring_topology']]['description'],
            'dimension_status': CATALOG[s['spring_topology']]['status'], 'notes': notes}


def generalized(theta, speed, c, input_reference=None):
    """Evaluate scalar spring force for the independent energy ODE."""
    if not isinstance(speed, (int, float)) or not math.isfinite(speed):
        raise ValueError('Theta speed must be finite radians/second.')
    g = geometry(theta, c)
    law = spring_law(g['input_length'], g['jacobian']*speed, c, input_reference)
    return {'geometry': g, 'law': law,
            'generalized_force': -law['tension']*g['jacobian'],
            'generalized_elastic_force': -law['elastic_tension']*g['jacobian'],
            'generalized_damping_force': -law['damper_tension']*g['jacobian']}


def passive_stability(c, rest, input_reference, auxiliary=None):
    """Local elastic stability at the initial ride pose, excluding active control.

    Uses actual calibrated free lengths/rate and distributed gravity. Derivatives
    are one-sided about the initial pose to expose unilateral engagement. This
    local ideal-guide test is neither a global stability proof nor contact safety.
    """
    if c['fixture'] != 'floating':
        return {'classification': 'not_applicable', 'reason': 'Fixed-fixture diagnostic; floating ride height required.'}
    q = math.radians(c['theta']); L = c['length']; eps = 1e-5
    cfg = {**c, 'rest_length': rest}
    aux = auxiliary if auxiliary is not None else auxiliary_parameters(c)
    S = 1.5*L*c['upper_mass'] + .5*(L+c['extension'])*c['lower_mass'] + 2*L*c['chassis_mass']
    def net(theta):
        Q = generalized(theta, 0., cfg, input_reference)['generalized_elastic_force']
        if aux['enabled']:
            Q += generalized(theta, 0., aux['config'], aux['input_ref'])['generalized_elastic_force']
        return (Q-S*c['gravity']*math.cos(theta))/(2*L*math.cos(theta))
    f = net(q); h = 2*L*math.sin(q)
    left = -(f-net(q-eps))/(h-2*L*math.sin(q-eps))
    right = -(net(q+eps)-f)/(2*L*math.sin(q+eps)-h)
    mean = (left+right)/2; tolerance = 1e-3
    classification = ('unstable' if min(left,right) < -tolerance else
                      'restoring' if min(left,right) > tolerance else 'neutral')
    notes = []
    if classification == 'unstable':
        notes.append('Passive initial ride equilibrium is locally unstable: gravity/geometric preload overwhelms restoring stiffness. Automatic preload balances force but does not guarantee stability; edit leverage/rate/mounts.')
    elif classification == 'neutral':
        notes.append('Passive initial ride equilibrium is locally neutral or one-sided: constant gravity compensation alone does not restore ride height. Damping can dissipate motion but cannot provide static restoring stiffness.')
    if abs(f) > .01:
        notes.append('Initial elastic/gravity force is unbalanced; the freely floating chassis will accelerate even if the local stiffness is restoring.')
    return {'classification': classification, 'net_ride_stiffness_N_m': mean,
            'left_ride_stiffness_N_m': left, 'right_ride_stiffness_N_m': right,
            'initial_force_balance_residual_N': f, 'theta_deg': c['theta'],
            'travel_limits_deg': [c['theta_min'], c['theta_max']],
            'active_controller_excluded': True, 'difference_angle_rad': eps,
            'scope': 'Local elastic/gravity test at initial ride height; exact ideal 2:1 guide, calibrated primary/auxiliary free lengths; excludes knee feedback, damping, contact and global travel stability. SciPy stops before limit impact; Pymunk solves rotary-stop reactions.',
            'notes': notes}


def auxiliary_parameters(c):
    """Resolve the optional original-tip ride spring without gravity retuning.

    Automatic free length makes its elastic force zero at the selected initial
    theta. Positive stiffness then supplies restoring force about that pose.
    The primary gravity compensator remains a separate calibrated stage.
    """
    s = mechanism_config(c)
    if not s['aux_spring_enabled']:
        return {'enabled': False, 'config': None, 'input_ref': 0., 'rest': 0.}
    aux = {**c, 'aux_spring_enabled': False, 'spring_topology': 'legacy_tip',
           'spring_mode': s['aux_mode'], 'spring_transmission': 'direct',
           'spring_force_law': 'hooke', 'spring_effective_free_length': 0.,
           'stiffness': s['aux_stiffness'], 'damping': s['aux_damping'],
           'rest_length': s['aux_rest_length'], 'balance_spring': False}
    initial = geometry(math.radians(c['theta']), aux)
    rest = initial['input_length'] if s['aux_auto_rest'] else s['aux_rest_length']
    aux['rest_length'] = rest
    spring_law(initial['input_length'], 0., aux, initial['input_length'])
    return {'enabled': True, 'config': aux, 'input_ref': initial['input_length'], 'rest': rest}


def auxiliary_metadata(c, params=None):
    """Declare passive-stage roles, resolved ride free length and preload caveat."""
    params = auxiliary_parameters(c) if params is None else params
    if not params['enabled']:
        return {'enabled': False, 'role': 'Optional ride restoring spring and damper; disabled.', 'notes': []}
    law = spring_law(params['input_ref'], 0., params['config'], params['input_ref'])
    notes = []
    if abs(law['elastic_tension']) > 1e-8:
        notes.append('Manual auxiliary preload shifts the initial equilibrium. The primary compensator balances gravity alone; it is not silently retuned for this ride-stage preload.')
    if c['aux_mode'] != 'captured':
        notes.append('A one-sided ride coil supplies restoring/damping load only while engaged; bilateral ride stiffness requires captured mode.')
    return {'enabled': True, 'topology': 'legacy_tip', 'mode': c['aux_mode'],
            'actual_rest_length_m': params['rest'], 'automatic_rest': c['aux_auto_rest'],
            'initial_elastic_tension_N': law['elastic_tension'],
            'stiffness_N_m': c['aux_stiffness'], 'damping_N_s_m': c['aux_damping'],
            'role': 'Primary stage provides gravity support; this independent original-tip strut provides ride restoring stiffness and passive damping.',
            'active_control': False, 'notes': notes}


def force_pair_power(force_sites, bodies, tension):
    """Physical tangent/direct force power; useful for integration diagnostics."""
    total = 0.
    for site in force_sites:
        velocity = _point_velocity(bodies[site['body']], site['world'])
        if velocity is None:
            raise ValueError('Body velocities are required for force-pair power.')
        total += tension*_dot(site['direction'], velocity)
    return total


def guide_pulley_frame(c, hip_center, knee_center, hip_angle, upper_angle, lower_angle):
    """Visible actual/analytical guide geometry, distinct from belt force dynamics.

    Angles are world radians. The hip pulley is fixed to chassis; the knee pulley
    is fixed to the lower link, with the upper link as the moving carrier.
    Visibility and massless sensor sizes do not alter the angular constraint.
    """
    return {'ratio': 2., 'carrier_angle': float(upper_angle),
            'hip': {'body': 'hip', 'center': [float(v) for v in hip_center],
                    'angle': float(hip_angle), 'radius': c['guide_hip_radius']},
            'knee': {'body': 'lower', 'center': [float(v) for v in knee_center],
                     'angle': float(lower_angle), 'radius': c['guide_hip_radius']/2},
            'scope': 'Ideal 2:1 angular constraint. Pulley sensors are massless visual/query geometry; no belt stretch, pretension or bearing-load model. Torque-implied tension difference is derived telemetry, not an applied belt force.'}
