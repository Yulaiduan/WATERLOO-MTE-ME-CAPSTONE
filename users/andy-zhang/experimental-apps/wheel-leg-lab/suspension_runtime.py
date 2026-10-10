"""Apply ideal suspension-preset forces to actual Pymunk bodies.

Imported by physics.py. Inputs: validated SI config, actual body poses/velocities.
Outputs: equal/opposite forces, exact applied body torques and spring telemetry.
Nonlegacy springs use explicit force integration; refinement is required for
sharp/high-stiffness cases. Massless cranks/ropes preserve virtual work, with no
rope stretch/friction or hardware coil-bound/contact model. Legacy stays native.
"""
import math
from pymunk import Vec2d
from spring_mechanisms import geometry, geometry_from_bodies, spring_law, calibrate_zero_effective_rate

def manual(c):
    return not(c['spring_topology']=='legacy_tip' and c['spring_mode']=='captured' and c['spring_transmission']=='direct' and c['spring_force_law']=='hooke')

def free_length(c,needed):
    g=geometry(math.radians(c['theta']),c);J=g['jacobian']
    if c['spring_force_law']=='zero_effective':
        if c['balance_spring']:calibrate_zero_effective_rate(c,needed,g)
        # Validate physical coil geometry, including manual incompatible/slack
        # modes and pull-through coil length, before stepping a rigid-body space.
        spring_law(g['input_length'],0.,c,g['input_length'])
        return c['rest_length'],g['input_length']
    eta=1. if c['spring_transmission']=='direct' else -1.
    coil=g['input_length'] if eta==1 else c['spring_coil_ref']
    if c['balance_spring']:
        if abs(J)<1e-8:raise ValueError('Selected spring has zero leverage at the initial pose; move its anchors or crank.')
        tension=-needed/J
        if c['stiffness']<=0:raise ValueError('Automatic balance requires positive spring stiffness.')
        coil_force=tension/eta
        if (c['spring_mode']=='compression' and coil_force>1e-8) or (c['spring_mode']=='extension' and coil_force<-1e-8) or (c['spring_transmission']=='ideal_rope' and tension<-1e-8):
            raise ValueError('This spring/routing direction cannot support the initial load. Reverse pulley direction/change mounts, or disable automatic balance to study its motion.')
        rest=coil-coil_force/c['stiffness']
    else:rest=c['rest_length']
    if rest<=.005:raise ValueError('Required coil free length is nonpositive; increase stiffness or change leverage/preload.')
    return rest,g['input_length']

def update(model,c):
    bodies={key:model[key] for key in ['hip','upper','lower']}
    g=geometry_from_bodies(bodies,c);cfg=dict(c,rest_length=model['rest'])
    law=spring_law(g['input_length'],g['input_speed'],cfg,model['spring_input_reference'])
    forces={key:Vec2d(0,0) for key in ['hip','upper','lower']};torques={key:0. for key in forces}
    for site in g['force_sites']:
        key=site['body'];body=bodies[key];F=Vec2d(*site['direction'])*law['tension'];point=Vec2d(*site['world'])
        forces[key]+=F;torques[key]+=(point-body.position).cross(F)
        body.apply_force_at_world_point(F,point)
    model['spring_loads']=forces;model['spring_torques']=torques
    model['spring_state']={**law,'input_length':g['input_length'],'input_speed':g['input_speed'],'jacobian':g['jacobian'],'geometry':g}
    model['cache']['distance']=g['input_length']

def visual(model,c):
    if not model.get('manual_spring'):return None
    g=geometry_from_bodies({key:model[key] for key in ['hip','upper','lower']},c)
    state=model.get('spring_state',{})
    return {'topology':c['spring_topology'],'kind':g['kind'],'mode':c['spring_mode'],'transmission':c['spring_transmission'],
            'a':g['anchors']['a']['world'],'b':g['anchors']['b']['world'],
            'coil_length':state.get('coil_length',g['input_length']),'tension':state.get('tension',0.),'pulley_radius':c['spring_pulley_radius'],
            'force_law':c['spring_force_law'],'effective_free_length':c['spring_effective_free_length'],'physical_coil_free_length':model['rest']}
