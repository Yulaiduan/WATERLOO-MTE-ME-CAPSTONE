"""General carrier-belt geometry for the original wheel suspension backends.

Invocation: imported by physics.py, math_model.py and spring_mechanisms.py.
Inputs: original SI profile plus explicit link lengths, pitch radii, kg and angles.
Outputs: exact poses/derivatives, inertias, force conversion and validated options.
No engine imports: independent math and Pymunk share geometry, not integration.
Limits: ideal open belts, held chassis pitch, prescribed wheel support; no contact.
Jonathan theta2=180-theta, theta3=phi0+(qab-1)*theta; angles are degrees in config.
"""
import math

DEFAULTS = {'linkage_design':'original','lower_length':.273,'guide_knee_radius':.014,
 'drive_hip_radius':.035,'drive_knee_radius':.035,'drive_output_radius':.035,'wheel_pulley_radius':.035,
 'mount_angle':0.,'link_phase':0.,'compound_mass':0.,'compound_inertia_radius':.035,
 'belt_preload_ab':0.,'belt_preload_cd':0.,'belt_preload_ef':0.,
 'contact_beta':0.,'contact_beta_min':0.,'contact_beta_max':90.,'contact_force_mode':'yz','contact_normal_force':0.,'contact_tangent_force':0.,
 'linkage_driven_lengths':'ratio','linkage_driven_guide':'ratio','linkage_driven_cd':'ratio','linkage_driven_ef':'ratio'}

def enabled(c):return c.get('linkage_design','original')=='general'

def ratios(c):
    return c['guide_hip_radius']/c['guide_knee_radius'],c['drive_hip_radius']/c['drive_knee_radius'],c['drive_output_radius']/c['wheel_pulley_radius']

def coefficient(c):
    ab,cd,ef=ratios(c);return 1-ab+ef*(ab-cd)

def validate(c):
    if c['linkage_design'] not in ('original','general'):raise ValueError('Unknown linkage design.')
    if c['contact_force_mode'] not in ('yz','nt'):raise ValueError('Unknown contact force convention.')
    for key in ('linkage_driven_lengths','linkage_driven_guide','linkage_driven_cd','linkage_driven_ef'):
        if c[key] not in ('ratio','first','second'):raise ValueError('Invalid driven linkage dimension.')
    for key in ('lower_length','guide_knee_radius','drive_hip_radius','drive_knee_radius','drive_output_radius','wheel_pulley_radius','compound_inertia_radius'):
        if not isinstance(c[key],(float,int)) or isinstance(c[key],bool) or not math.isfinite(c[key]) or c[key]<=0:raise ValueError(key+' must be positive finite metres.')
    if not .08<=c['lower_length']<=.8:raise ValueError('L3 must be between 80 and 800 mm in the dynamic bench.')
    if c['compound_mass']>20 or not 1e-6<=c['compound_inertia_radius']<=.25:raise ValueError('Compound mass/rim radius exceeds the experimental dynamic bounds.')
    for key in ('guide_knee_radius','drive_hip_radius','drive_knee_radius','drive_output_radius','wheel_pulley_radius'):
        if c[key]<1e-6:raise ValueError(key+' must be at least 0.001 mm.')
    for key in ('compound_mass','belt_preload_ab','belt_preload_cd','belt_preload_ef'):
        if not math.isfinite(c[key]) or c[key]<0:raise ValueError(key+' must be finite and nonnegative.')
    for key,maximum in (('mount_angle',45),('link_phase',30),('contact_beta',90)):
        if not math.isfinite(c[key]) or not 0<=c[key]<=maximum:raise ValueError(key+' is outside its degree domain.')
    if not 0<=c['contact_beta_min']<=c['contact_beta_max']<=90:raise ValueError('Require 0 ≤ beta sweep minimum ≤ maximum ≤ 90 degrees.')
    if enabled(c):
        if c['fixture']!='floating' or c['target']!='position':raise ValueError('The general linkage uses the original floating-chassis wheel-position fixture.')
        if c['spring_integration']=='native_legacy':raise ValueError('General linkage requires the original explicit point-force spring integration.')
        if c['aux_spring_enabled']:raise ValueError('General linkage retains the original single primary spring; disable the auxiliary strut.')
        if c['wheel_drive_locked']:raise ValueError('General wheel rotation comes from the three belt ratios; turn off the legacy lower-link wheel lock.')
        if c['extension']>=c['lower_length']:raise ValueError('Lower extension must be shorter than L3.')
        for first,second,distance in (('guide_hip_radius','guide_knee_radius',c['length']),('drive_hip_radius','drive_knee_radius',c['length']),('drive_output_radius','wheel_pulley_radius',c['lower_length'])):
            if c[first]+c[second]>=distance:raise ValueError('Pitch circles overlap in '+first+'/'+second+'.')

def loads(c):
    beta=math.radians(c['contact_beta']);s,co=math.sin(beta),math.cos(beta)
    if c['contact_force_mode']=='nt':
        fn,ft=c['contact_normal_force'],c['contact_tangent_force'];fy,fz=fn*s+ft*co,fn*co-ft*s
    else:
        fy,fz=c['bias_force_x'],c['bias_force'];fn,ft=fy*s+fz*co,fy*co-fz*s
    moment=c['radius']*ft if c['load_point']=='contact' else 0.
    return fy,fz,fn,ft,moment

def points(q,c):
    """C-relative world positions, first/second q derivatives and absolute angles."""
    a=math.radians(c['mount_angle']);phi=math.radians(c['link_phase']);ab,cd,_=ratios(c);k=ab-1
    reference=math.radians(c['theta_max'])
    angles={'hip':0.,'upper':-q-a,'lower':k*q+phi-math.pi-a,'compound':(cd-1)*(q-reference)-a,'wheel':-coefficient(c)*(q-reference)-a}
    rates={'hip':0.,'upper':-1.,'lower':k,'compound':cd-1,'wheel':-coefficient(c)}
    def vec(L,angle,speed):
        x,y=L*math.cos(angle),L*math.sin(angle)
        return (x,y),(-speed*y,speed*x),(-speed*speed*x,-speed*speed*y)
    av=vec(c['length'],angles['upper'],-1);bv=vec(c['lower_length'],angles['lower'],k)
    def linear(ca,cb):return tuple(tuple(ca*av[j][i]+cb*bv[j][i] for i in (0,1)) for j in range(3))
    lam=(c['lower_length']+c['extension'])/(2*c['lower_length'])
    sites={'hip':linear(-1,-1),'knee':linear(0,-1),'hub':linear(0,0),'upper':linear(-.5,-1),'lower':linear(0,-lam),'compound':linear(0,-1),'wheel':linear(0,0),'tip':linear(0,-1-c['extension']/c['lower_length'])}
    return sites,angles,rates

def poses(q,c,theta_speed=0.,base_height=0.,base_speed=0.):
    sites,angles,rates=points(q,c)
    return {key:{'position':[sites[key][0][0],sites[key][0][1]+base_height],'angle':angles[key],
                 'velocity':[sites[key][1][0]*theta_speed,sites[key][1][1]*theta_speed+base_speed],'angular_velocity':rates[key]*theta_speed} for key in ('hip','upper','lower')}

def inertias(c):
    return {'upper':c['upper_mass']*c['length']**2/12,'lower':c['lower_mass']*(c['lower_length']+c['extension'])**2/12,
            'compound':c['compound_mass']*c['compound_inertia_radius']**2,'wheel':c['wheel_mass']*c['radius']**2,'hip':0.}

def masses(c):return {'hip':c['chassis_mass'],'upper':c['upper_mass'],'lower':c['lower_mass'],'compound':c['compound_mass'],'wheel':c['wheel_mass']}

def energy_terms(q,c):
    sites,_,rates=points(q,c);ms=masses(c);Is=inertias(c)
    M=sum(ms[key]*sum(x*x for x in sites[key][1])+Is[key]*rates[key]**2 for key in ms)
    Mp=sum(2*ms[key]*sum(x*y for x,y in zip(sites[key][1],sites[key][2])) for key in ms)
    Gy=sum(ms[key]*sites[key][1][1] for key in ms)
    return M,Mp,Gy
