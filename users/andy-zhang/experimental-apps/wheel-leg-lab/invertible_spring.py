"""Geometry/virtual work for experimental invertible one-cap suspensions.

Invocation: prepare(config), state(theta_rad, omega_rad_s, config, prepared).
Inputs: SI lengths/rates, degrees only for configured attachment offset.
Outputs: routed red/blue cable paths, slack/tension, cap travel, spring energy,
and conservative generalized torque. No Pymunk/ODE dependency.
Limitations: massless piston/ropes; central leads between two rollers, with
outward flare, tangent spans and knee-rim wrap to the anchors. No rope crossover,
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

def attachment_phase(c):
    # Old exported profiles lack the marker and retain their original phase.
    return math.pi if c.get('rope_neutral_pose','straight')=='folded' else 0.

def _line_clear(a,b,R):
    v=sub(b,a);t=max(0,min(1,dot(mul(a,-1),v)/dot(v,v)))
    return norm(add(a,mul(v,t)))>=R-1e-9

def _clear_other(a,b,center,radius):
    v=sub(b,a);t=max(0,min(1,dot(sub(center,a),v)/dot(v,v)))
    return norm(sub(add(a,mul(v,t)),center))>=radius-1e-9

def _outer_route(phi,c,side):
    """Actual offset attachment geometry with an explicit linear-feed idler.

    Cylinder yoke eyes feed two parallel straight runs; red upper idler turns
    clockwise and blue lower idler turns counterclockwise. Candidate external/
    crossed common tangents and visible direct anchor paths avoid the drum.
    The shortest valid route is selected; stored branch history is not modeled.
    """
    R,r=c['pulley_radius'],c['routing_radius'];sgn=1 if side=='red' else -1
    G=(-c['routing_distance'],sgn*c['routing_offset']);S=add(G,(0,sgn*r))
    winding=-sgn;start=sgn*math.pi/2
    angle=phi+attachment_phase(c)+sgn*math.radians(c['attachment_offset_deg']);E=mul(polar(angle),R)
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

def _central_route(phi,c,side,cap_x):
    """Shortest centre-channel cable to a knee attachment, with optional rim wrap.

    The cap eye translates along x. Either small roller can guide an outward
    flare; a rope inside the channel can lose roller contact. Current central_wrap treats the knee circle as an obstacle and adds rim arcs;
    explicit central_face retains the previous face-crossing study. Return length partial
    derivatives so cap travel and cable tension account for the lead angle.
    """
    sign=1 if side=='red' else -1
    angle=phi+attachment_phase(c)+sign*math.radians(c['attachment_offset_deg'])
    E=mul(polar(angle),c['pulley_radius']);P=(cap_x,sign*c['rope_eye_offset'])
    radius=c['routing_radius'];gap=c['routing_offset']-radius
    guides={key:(-c['routing_distance'],s*c['routing_offset']) for key,s in [('red',1),('blue',-1)]}
    candidates=[];wrapped=c.get('rope_routing')=='central_wrap';R=c['pulley_radius']
    def append(length,pieces,feed,upper_contact,u_in,u_out,roller,lower_contact=None,derivative=None):
        candidates.append({'length':length,'derivative':dot(u_out,(-E[1],E[0])) if derivative is None else derivative,
          'cap_projection':u_in[0],'pieces':pieces,'eye':P,'feed':feed,
          'upper_contact':upper_contact,'lower_contact':E if lower_contact is None else lower_contact,'direction':mul(u_out,-1),
          'contact_roller':roller,'anchor':E,'colour':side,'attachment_angle':angle,
          'routing':'central_wrap' if wrapped else 'central_face'})
    straight=sub(E,P)
    if straight[0]<=0:raise ValueError('Cylinder rope eyes must stay before the knee anchors.')
    u=unit(straight)
    gate_y=P[1]+straight[1]*(-c['routing_distance']-P[0])/straight[0]
    if abs(gate_y)<=gap+1e-10 and all(_clear_other(P,E,G,radius) for G in guides.values()) and (not wrapped or _line_clear(P,E,R)):
        append(norm(straight),[{'kind':'line','a':P,'b':E}],P,P,u,u,None)
    if wrapped:
        distance=norm(P);beta=math.atan2(P[1],P[0]);gamma=math.acos(R/distance)
        for tangent_angle in (beta-gamma,beta+gamma):
            N=polar(tangent_angle);T=mul(N,R);incoming=unit(sub(T,P))
            gate=P[1]+incoming[1]*(-c['routing_distance']-P[0])/incoming[0]
            if abs(gate)>gap+1e-10 or not all(_clear_other(P,T,G,radius) for G in guides.values()):continue
            winding=1 if cross(N,incoming)>0 else -1;sweep=(winding*(angle-tangent_angle))%TAU
            pieces=[{'kind':'line','a':P,'b':T},{'kind':'arc','center':(0,0),'radius':R,'start':tangent_angle,'sweep':winding*sweep}]
            append(norm(sub(T,P))+R*sweep,pieces,P,P,incoming,incoming,None,T,winding*R)
    for key,G in guides.items():
        winding=1 if key=='red' else -1
        delta_in=sub(P,G);delta_out=sub(E,G);din,dout=norm(delta_in),norm(delta_out)
        if min(din,dout)<=radius:continue
        bin=math.atan2(delta_in[1],delta_in[0]);bout=math.atan2(delta_out[1],delta_out[0])
        ain=math.acos(radius/din);aout=math.acos(radius/dout)
        other=guides['blue' if key=='red' else 'red']
        for qi in (bin-ain,bin+ain):
            Ni=polar(qi);Ti=add(G,mul(Ni,radius));uin=unit(sub(Ti,P))
            if winding*cross(Ni,uin)<.999999 or not _clear_other(P,Ti,other,radius):continue
            def outgoing(No,To,end,main=None):
                uout=unit(sub(end,To));qo=math.atan2(No[1],No[0])
                arc=(winding*(qo-qi))%TAU
                if winding*cross(No,uout)<.999999 or arc>math.pi+1e-10 or not _clear_other(To,end,other,radius):return
                if main is None and wrapped and not _line_clear(To,E,R):return
                pieces=[{'kind':'arc','center':G,'radius':radius,'start':qi,'sweep':winding*arc},
                        {'kind':'line','a':To,'b':end}]
                length=norm(sub(Ti,P))+radius*arc+norm(sub(end,To))
                derivative=None
                if main:
                    mainN,main_winding=main;start=math.atan2(mainN[1],mainN[0]);sweep=(main_winding*(angle-start))%TAU
                    length+=R*sweep;derivative=main_winding*R
                    pieces.append({'kind':'arc','center':(0,0),'radius':R,'start':start,'sweep':main_winding*sweep})
                append(length,pieces,Ti,To,uin,uout,key,end if main else None,derivative)
            for qo in (bout-aout,bout+aout):
                No=polar(qo);To=add(G,mul(No,radius));outgoing(No,To,E)
            if wrapped:
                delta=mul(G,-1);distance=norm(delta);base=unit(delta);perp=(-base[1],base[0])
                for sign in (1,-1):
                    projection=(radius-sign*R)/distance
                    if abs(projection)>=1:continue
                    for branch in (-1,1):
                        No=add(mul(base,projection),mul(perp,branch*math.sqrt(1-projection**2)))
                        To=add(G,mul(No,radius));mainN=mul(No,sign);end=mul(mainN,R);uout=unit(sub(end,To))
                        main_winding=1 if cross(mainN,uout)>0 else -1
                        outgoing(No,To,end,(mainN,main_winding))
    if not candidates:raise ValueError('No valid central cable path; adjust roller spacing/placement or cap mount.')
    return min(candidates,key=lambda value:value['length'])

def route(phi,c,side,cap_x=None):
    if c.get('rope_routing','central_face')=='outer_rim':return _outer_route(phi,c,side)
    if cap_x is None:cap_x=-(c['length']-c['cap_reference_distance'])
    return _central_route(phi,c,side,cap_x)

def _cap_demand(phi,c,side,reference,arm):
    """Solve cable inventory at a moving cap; d(length)/dx = -lead cosine."""
    initial=route(phi,c,side,-arm)
    if initial['length']<=reference+1e-12:return 0.
    maximum=arm-c['routing_distance']-c['routing_radius']-.005
    x=(initial['length']-reference)/initial['cap_projection']
    for _ in range(12):
        if not 0<=x<=maximum:raise ValueError('Piston take-up exhausted the central feed span; move its mount toward J1.')
        current=route(phi,c,side,-arm+x);error=current['length']-reference
        if abs(error)<1e-12:return x
        x+=error/current['cap_projection']
    raise ValueError('Central cable cap-travel solve did not converge.')

def prepare(c):
    p={'arm':c['length']-(c['cap_reference_distance'] if c['preset']=='dual_rope' else c['femur_anchor_distance'])}
    if c['preset']=='dual_rope':
        if c['routing_offset']<=c['routing_radius']+.00001:
            raise ValueError('Red and blue routing pulley circles must be separated.')
        if c.get('rope_routing','central_face')=='outer_rim' and c['routing_offset']+c['routing_radius']<=c['pulley_radius']:
            raise ValueError('Parallel rope feeds must lie outside the knee drum: routing offset + radius > drum radius.')
        if c.get('rope_routing','central_face')!='outer_rim' and c['rope_eye_offset']>=c['routing_offset']-c['routing_radius']-.00001:
            raise ValueError('Both rope eyes must lie inside the central gap between the rollers.')
        if math.hypot(c['routing_distance'],c['routing_offset'])<=c['pulley_radius']+c['routing_radius']:
            raise ValueError('The two routing pulleys must clear the knee drum.')
        p['reference_phi']=0. if c.get('rope_neutral_pose','straight')=='folded' else math.pi
        p['reference']={colour:route(p['reference_phi'],c,colour)['length'] for colour in ('red','blue')}
    else:
        p['minimum']=abs(p['arm']-c['crank_radius'])
        if p['minimum']<.005:raise ValueError('Bellcrank tip must not coincide with femur anchor at straight knee.')
    return p

def state(theta,omega,c,p):
    phi=2*theta
    if c['preset']=='dual_rope':
        central=c.get('rope_routing','central_face')!='outer_rim'
        takeup={colour:(_cap_demand(phi,c,colour,p['reference'][colour],p['arm']) if central else route(phi,c,colour)['length']-p['reference'][colour]) for colour in ('red','blue')}
        active=max(takeup,key=takeup.get);x=max(0,takeup[active])
        if abs(takeup['red']-takeup['blue'])<1e-10 and abs(omega)>1e-10:
            ahead=phi+math.copysign(1e-7,omega)
            upcoming={colour:(_cap_demand(ahead,c,colour,p['reference'][colour],p['arm']) if central else route(ahead,c,colour)['length']-p['reference'][colour]) for colour in ('red','blue')}
            active=max(upcoming,key=upcoming.get)
        routes={colour:route(phi,c,colour,-p['arm']+x) for colour in ('red','blue')}
        projection=routes[active].get('cap_projection',1.)
        J=2*routes[active]['derivative']/projection if x>1e-12 else 0.
        if p['arm']-c['routing_distance']-x<.005:
            raise ValueError('Piston take-up exhausted the parallel rope span; move its mount toward J1 or routing pulleys toward the knee.')
        geometry={'routes':routes,'routing':c.get('rope_routing','central_face'),'active':active if x>1e-12 else 'none',
                  'slack':{key:max(0,p['reference'][key]-routes[key]['length']) if central else x-takeup[key] for key in takeup},'cap_x':-p['arm']+x,
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
    tensions={colour:force/(routes[colour].get('cap_projection',1.)) if geometry['active']==colour else 0. for colour in ('red','blue')}
    return {'compression':z,'takeup':x,'coil_length':coil,'cap_force':force,'elastic_force':elastic,
            'torque':-force*J,'jacobian':J,'energy':.5*c['stiffness']*z*z,
            'dissipation':max(0,(force-elastic)*speed),'red_tension':tensions['red'],'blue_tension':tensions['blue'],
            'geometry':geometry}

def samples(piece,count=20):
    if piece['kind']=='line':return [piece['a'],piece['b']]
    return [add(piece['center'],mul(polar(piece['start']+piece['sweep']*i/count),piece['radius'])) for i in range(count+1)]
