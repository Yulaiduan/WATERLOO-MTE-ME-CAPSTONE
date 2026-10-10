"""Capture actual Pymunk debug primitives and inspect model objects.

Invocation: imported by physics.py; capture(space) and describe(model).
Inputs: engine bodies/constraints in SI; debug coordinates scaled by 600 px/m.
Outputs: serializable shape primitives and model descriptions; no files.
Requires Pymunk; the visualization does not add contact or hardware fidelity.
"""
import math
import pymunk

DEBUG_SCALE=600.

def vector(v): return [float(v.x),float(v.y)]
def color(c): return list(c)

class CaptureDraw(pymunk.SpaceDebugDrawOptions):
    def __init__(self):
        super().__init__()
        self.transform=pymunk.Transform.scaling(DEBUG_SCALE)
        self.primitives=[]
    def draw_circle(self,pos,angle,radius,outline_color,fill_color):
        self.primitives.append({'kind':'circle','pos':vector(pos),'angle':angle,'radius':radius,'outline':color(outline_color),'fill':color(fill_color)})
    def draw_segment(self,a,b,c):
        self.primitives.append({'kind':'segment','a':vector(a),'b':vector(b),'color':color(c)})
    def draw_fat_segment(self,a,b,radius,outline_color,fill_color):
        self.primitives.append({'kind':'capsule','a':vector(a),'b':vector(b),'radius':radius,'outline':color(outline_color),'fill':color(fill_color)})
    def draw_polygon(self,verts,radius,outline_color,fill_color):
        self.primitives.append({'kind':'polygon','vertices':[vector(p) for p in verts],'radius':radius,'outline':color(outline_color),'fill':color(fill_color)})
    def draw_dot(self,size,pos,c):
        self.primitives.append({'kind':'dot','size':size,'pos':vector(pos),'color':color(c)})

def capture(space):
    options=CaptureDraw();space.debug_draw(options)
    return options.primitives

def describe(model):
    def number(x): return x if math.isfinite(x) else 'fixed / infinite'
    bodies=[]
    for key in ['hip','upper','lower','wheel']:
        b=model[key]
        bodies.append({'name':key,'class':type(b).__name__,'type':'static' if b.body_type==pymunk.Body.STATIC else 'dynamic',
                       'mass_kg':number(b.mass),'inertia_kg_m2':number(b.moment),'position_m':vector(b.position),'angle_rad':b.angle})
    joints=[]
    names=['j1','j2','j3','guide','spring','stop']+(['wheel_drive'] if model.get('wheel_drive') else [])
    for key in names:
        j=model[key];info={'name':key,'class':type(j).__name__}
        if isinstance(j,pymunk.PivotJoint): info.update(anchor_a_m=vector(j.anchor_a),anchor_b_m=vector(j.anchor_b))
        elif isinstance(j,pymunk.GearJoint):
            info.update(absolute_ratio=j.ratio,phase_rad=j.phase)
            if key=='guide':info['physical_guide_ratio']=2
        elif isinstance(j,pymunk.DampedSpring):info.update(anchor_a_m=vector(j.anchor_a),anchor_b_m=vector(j.anchor_b),rest_length_m=j.rest_length,stiffness_N_m=j.stiffness,damping_N_s_m=j.damping)
        elif isinstance(j,pymunk.RotaryLimitJoint):info.update(min_relative_rad=j.min,max_relative_rad=j.max)
        joints.append(info)
    return {'bodies':bodies,'constraints':joints,'shapes':[{'name':key,'class':type(shape).__name__,'sensor':shape.sensor} for key,shape in model['shapes'].items()],
            'renderer':'pymunk.Space.debug_draw callbacks','debug_scale':DEBUG_SCALE}
