"""Finite-ramp prescribed-position inputs for the experimental wheel fixture.

Invocation: imported by physics.py; position_state(t, config).
Inputs: seconds, metre displacement amplitude, explicit timing and ramp shape.
Outputs: displacement (m), instantaneous velocity (m/s), acceleration (m/s2).
Dependencies: standard library. Linear ramp joins have velocity jumps; no finite
impact force is implied. Quintic ramps are C2 continuous with zero end v/a.
"""
def ramp(t,duration,shape):
    if t<=0:return 0.,0.,0.
    if t>=duration:return 1.,0.,0.
    u=t/duration
    if shape=='linear':return u,1/duration,0.
    return (10*u**3-15*u**4+6*u**5,
            (30*u**2-60*u**3+30*u**4)/duration,
            (60*u-180*u**2+120*u**3)/duration**2)

def position_state(t,c):
    t-=c['start'];A=c['position_amplitude']
    if t<0:return 0.,0.,0.
    if c['wave']=='step':
        z,v,a=ramp(t,c['rise'],c['ramp_shape']);return A*z,A*v,A*a
    width=c['period']*c['duty'] if c['wave']=='square' else c['pulse_width']
    if c['wave']=='square':t%=c['period']
    if t>=width:return 0.,0.,0.
    if t<c['rise']:
        z,v,a=ramp(t,c['rise'],c['ramp_shape']);return A*z,A*v,A*a
    if t<=width-c['fall']:return A,0.,0.
    z,v,a=ramp(t-(width-c['fall']),c['fall'],c['ramp_shape'])
    return A*(1-z),-A*v,-A*a
