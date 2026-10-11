"""Build initial suspension geometry without running or reporting a simulation.

Invocation: preview(config) via POST /api/setup-preview. Inputs: normal SI wheel
profile; outputs: initial actual body/debug shapes, spring anchors and lengths.
Uses the existing Pymunk builder/preload rules but never calls Space.step.
No joint forces, acceleration, trace rows or simulated results are inferred.
"""
from debug_view import capture, describe
from physics import config, build
from spring_mechanisms import geometry_from_bodies, guide_pulley_frame, spring_law


def preview(values=None):
    c = config(values)
    model = build(c)
    h, u, l, w = (model[key] for key in ('hip', 'upper', 'lower', 'wheel'))
    A = h.local_to_world(model['j1'].anchor_a)
    B = l.local_to_world(model['j2'].anchor_b)
    C = w.position
    E = l.local_to_world((-(c['length']+c['extension'])/2, 0))
    bodies = {key: model[key] for key in ('hip', 'upper', 'lower')}
    geometry = geometry_from_bodies(bodies, c)
    law = spring_law(geometry['input_length'], 0., dict(c, rest_length=model['rest']), model['spring_input_reference'])
    frame = {'t': 0., 'hip': list(A), 'knee': list(B), 'hub': list(C), 'tip': list(E),
             'upper_angle': u.angle, 'lower_angle': l.angle,
             'debug_draw': capture(model['space']), 'spring_geometry': geometry,
             'spring_coil_length': law['coil_length']}
    if c['guide_pulleys_visible']:
        frame['guide_pulleys'] = guide_pulley_frame(c, A, B, h.angle, u.angle, l.angle)
    if model['auxiliary']['enabled']:
        aux = model['auxiliary']
        g = geometry_from_bodies(bodies, aux['config'])
        frame['auxiliary_spring_geometry'] = g
        frame['auxiliary_spring_coil_length'] = spring_law(g['input_length'], 0., aux['config'], aux['input_ref'])['coil_length']
    return {'kind': 'setup-preview', 'solver_steps': 0, 'config': c,
            'model': describe(model), 'frame': frame,
            'geometry': {'theta_deg': c['theta'], 'height': A.y-C.y,
                         'spring_length': geometry['input_length'],
                         'spring_coil_length': law['coil_length']},
            'scope': 'Initial setup geometry only. No simulation steps or measured loads; press Run for recorded motion and forces.'}
