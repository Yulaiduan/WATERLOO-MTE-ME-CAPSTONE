"""Geometry/virtual work for experimental invertible one-cap suspensions.

Invocation: prepare(config), state(theta_rad, omega_rad_s, config, prepared).
Inputs: SI lengths/rates, degrees only for configured attachment offset.
Outputs: routed red/blue cable paths, slack/tension, cap travel, spring energy,
and conservative generalized torque. No Pymunk/ODE dependency.
Limitations: massless piston/ropes; ideal shortest external paths around two
explicit routing pulleys and the knee drum. No winding history, rope crossover,
groove friction/stretch, piston binding, structural or packaging validation.
One taut rope selects the common cap; exact ties use the outgoing branch.
"""
import math

TAU = 2*math.pi
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def mul(a,k): return (a[0]*k,a[1]*k)
def dot(a,b): return a[0]*b[0]+a[1]*b[1]
def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def rot(a,q): return (a[0]*math.cos(q)-a[1]*math.sin(q),a[0]*math.sin(q)+a[1]*math.cos(q))
def norm(a): return math.hypot(*a)
def unit(a): return mul(a,1/norm(a))
def polar(q): return (math.cos(q),math.sin(q))

def _line_clear(a,b,R):
    v=sub(b,a);t=max(0,min(1,dot(mul(a,-1),v)/dot(v,v)))
    return norm(add(a,mul(v,t)))>=R-1e-9

def _clear_other(a,b,center,radius):
    v=sub(b,a);t=max(0,min(1,dot(sub(center,a),v)/dot(v,v)))
    return norm(sub(add(a,mul(v,t)),center))>=radius-1e-9

def route(phi,c,side):
    """Actual offset attachment geometry with an explicit linear-feed idler.

    Cylinder yoke eyes feed two parallel straight runs; red upper idler turns
    clockwise and blue lower idler turns counterclockwise. Candidate external/
    crossed common tangents and visible direct anchor paths avoid the drum.
    The shortest valid route is selected; stored branch history is not modeled.
    """
    R,r=c['pulley_radius'],c['routing_radius'];sgn=1 if side=='red' else -1
    G=(-c['routing_distance'],sgn*c['routing_offset']);S=add(G,(0,sgn*r))
    winding=-sgn;start=sgn*math.pi/2
    angle=phi+sgn*math.radians(c['attachment_offset_deg']);E=mul(polar(angle),R)
    candidates=[]
    def candidate(N,T,end,arc_main=None):
        v=sub(end,T);distance=norm(v)
        if distance<1e-12 or winding*cross(N,unit(v))<.999999:return
        if not _clear_other(T,end,(G[0],-G[1]),r):return
        arc=(winding*(math.atan2(N[1],N[0])-start))%TAU
        pieces=[{'kind':'arc','center':G,'radius':r,'start':start,'sweep':winding*arc},
                {'kind':'line','a':T,'b':end}]
        length=r*arc+distance
        if arc_main:
            mainN,w=arc_main;initial=math.atan2(mainN[1],mainN[0]);sweep=(w*(angle-initial))%TAU
            length+=R*sweep;derivative=w*R
            pieces.append({'kind':'arc','center':(0,0),'radius':R,'start':initial,'sweep':w*sweep})
        else:
            if not _line_clear(T,E,R):return
            derivative=dot(unit(v),(-E[1],E[0]))
        candidates.append({'length':length,'derivative':derivative,'pieces':pieces,
                           'upper_contact':T,'lower_contact':end,'direction':mul(unit(v),-1)})
    delta=sub(E,G);distance=norm(delta)
    if distance>r:
        beta=math.atan2(delta[1],delta[0]);gamma=math.acos(r/distance)
        for q in (beta-gamma,beta+gamma):
            N=polar(q);candidate(N,add(G,mul(N,r)),E)
    delta=mul(G,-1);distance=norm(delta);base=unit(delta);perp=(-base[1],base[0])
    for sign in (1,-1):
        projection=(r-sign*R)/distance
        if abs(projection)>=1:continue
        for branch in (-1,1):
            N=add(mul(base,projection),mul(perp,branch*math.sqrt(1-projection**2)))
            T=add(G,mul(N,r));mainN=mul(N,sign);end=mul(mainN,R);v=unit(sub(end,T))
            w=1 if cross(mainN,v)>0 else -1
            candidate(N,T,end,(mainN,w))
    if not candidates:raise ValueError('No valid routed cable path; change routing pulley placement.')
    result=min(candidates,key=lambda a:a['length'])
    return {**result,'anchor':E,'guide_center':G,'feed':S,'colour':side,'attachment_angle':angle}

def prepare(c):
    p={'arm':c['length']-(c['cap_reference_distance'] if c['preset']=='dual_rope' else c['femur_anchor_distance'])}
    if c['preset']=='dual_rope':
        if c['routing_offset']<=c['routing_radius']+.001:
            raise ValueError('Red and blue routing pulley circles must be separated.')
        if c['routing_offset']+c['routing_radius']<=c['pulley_radius']:
            raise ValueError('Parallel rope feeds must lie outside the knee drum: routing offset + radius > drum radius.')
        if math.hypot(c['routing_distance'],c['routing_offset'])<=c['pulley_radius']+c['routing_radius']:
            raise ValueError('The two routing pulleys must clear the knee drum.')
        p['reference']={colour:route(math.pi,c,colour)['length'] for colour in ('red','blue')}
    else:
        p['minimum']=abs(p['arm']-c['crank_radius'])
        if p['minimum']<.005:raise ValueError('Bellcrank tip must not coincide with femur anchor at straight knee.')
    return p

def state(theta,omega,c,p):
    phi=2*theta
    if c['preset']=='dual_rope':
        routes={colour:route(phi,c,colour) for colour in ('red','blue')}
        takeup={colour:g['length']-p['reference'][colour] for colour,g in routes.items()}
        active=max(takeup,key=takeup.get);x=max(0,takeup[active])
        if abs(takeup['red']-takeup['blue'])<1e-10 and abs(omega)>1e-10:
            upcoming={colour:route(phi+math.copysign(1e-7,omega),c,colour)['length']-p['reference'][colour] for colour in routes}
            active=max(upcoming,key=upcoming.get)
        J=2*routes[active]['derivative'] if x>1e-12 else 0.
        if p['arm']-c['routing_distance']-x<.005:
            raise ValueError('Piston take-up exhausted the parallel rope span; move its mount toward J1 or routing pulleys toward the knee.')
        geometry={'routes':routes,'active':active if x>1e-12 else 'none',
                  'slack':{key:x-takeup[key] for key in takeup},'cap_x':-p['arm']+x,
                  'piston_cap_x':-p['arm']-c['rod_length']+x,
                  'fixed_seat_x':-p['arm']-c['rod_length']+c['coil_free_length']-c['preload']}
    else:
        a,b=p['arm'],c['crank_radius'];psi=phi-math.pi
        distance=math.sqrt(a*a+b*b-2*a*b*math.cos(psi))
        x=distance-p['minimum'];J=2*a*b*math.sin(psi)/distance
        geometry={'femur_anchor':(-a,0),'crank_tip':mul(polar(phi),b),'active':'bellcrank','slack':{},'cap_x':-a+x}
    z=c['preload']+x;coil=c['coil_free_length']-z
    if coil<.005:raise ValueError('Compression coil reached the configured travel limit; increase free length or reduce preload/take-up.')
    elastic=c['stiffness']*z;speed=J*omega;force=max(0,elastic+c['damping']*speed)
    tensions={colour:force if geometry['active']==colour else 0. for colour in ('red','blue')}
    return {'compression':z,'takeup':x,'coil_length':coil,'cap_force':force,'elastic_force':elastic,
            'torque':-force*J,'jacobian':J,'energy':.5*c['stiffness']*z*z,
            'dissipation':max(0,(force-elastic)*speed),'red_tension':tensions['red'],'blue_tension':tensions['blue'],
            'geometry':geometry}

def samples(piece,count=20):
    if piece['kind']=='line':return [piece['a'],piece['b']]
    return [add(piece['center'],mul(polar(piece['start']+piece['sweep']*i/count),piece['radius'])) for i in range(count+1)]
