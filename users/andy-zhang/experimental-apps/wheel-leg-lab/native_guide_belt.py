"""Draw the visible ideal 2:1 guide over actual Pymunk bodies.

Invocation: capture_torque after Space.step, draw during native rendering.
Inputs: SI body state/config, previous velocities/spins, optional viewer-only
slack-span tension N. Outputs: moving material dots, pivot/rotation marks and
torque-derived force arrows. Requires pygame/Pymunk and guide_belt geometry.
No belt forces are applied. Engine pin loads exclude these inferred bearing
loads; unknown pretension stays unknown. Signed recovery covers floating mode.
"""
import math
import pygame
from pymunk import Vec2d
from guide_belt import build_loop, material_phase, material_dots, tension_state


def capture_torque(m,c,velocities,spins,dt):
    if c['fixture']!='floating':return None
    u,l,h,w=(m[key] for key in ('upper','lower','hip','wheel'))
    g=m['space'].gravity
    accelerations={key:(m[key].velocity-velocities[key])/dt for key in velocities}
    au,al,ah=(accelerations[key] for key in ('upper','lower','hip'))
    if m['manual_spring']:
        sf,sm=m['spring_loads'],m['spring_torques']
    else:
        force=m['cache']['n']*m['spring'].impulse/dt
        sf={'hip':-force,'upper':Vec2d(0,0),'lower':force}
        sm={'upper':0.,'lower':(l.local_to_world(m['spring'].anchor_b)-l.position).cross(force)}
    f1=sf['hip']-h.mass*(ah-g);f2=f1+sf['upper']-u.mass*(au-g);f3=f2+sf['lower']-l.mass*(al-g)
    Mu=(u.local_to_world(m['j1'].anchor_b)-u.position).cross(f1)+(u.local_to_world(m['j2'].anchor_a)-u.position).cross(-f2)+sm['upper']
    Ml=(l.local_to_world(m['j2'].anchor_b)-l.position).cross(f2)+(l.local_to_world(m['j3'].anchor_a)-l.position).cross(-f3)+sm['lower']
    wheel_reaction=-(w.moment*(w.angular_velocity-spins['wheel'])/dt-m['wheel_external_moment']) if m['wheel_drive'] else 0.
    actuator=m.get('live_actuator',0.)
    ru=u.moment*(u.angular_velocity-spins['upper'])/dt-Mu+actuator
    rl=l.moment*(l.angular_velocity-spins['lower'])/dt-Ml-actuator-wheel_reaction
    return (ru+rl)/2


def draw(screen,m,c,project,font,viewer=None):
    if not c.get('guide_pulleys_visible'):return
    viewer=viewer or {};rh=c['guide_hip_radius'];rk=rh/2
    A=m['hip'].local_to_world(m['j1'].anchor_a);B=m['lower'].local_to_world(m['j2'].anchor_b)
    loop=build_loop(A,B,rh,rk)
    gold=(226,191,112);white=(230,239,225);gray=(132,151,139)
    pygame.draw.lines(screen,gold,True,[project(p) for p in loop['points']],2)
    phase=material_phase(m['upper'].angle-m['hip'].angle,-math.radians(c['theta']),rh)
    for i,p in enumerate(material_dots(loop,phase)):
        pygame.draw.circle(screen,white if i%4 else (246,144,93),project(p),3 if i%4==0 else 2)
    for name,center,radius,body in [('J1 fixed',A,rh,m['hip']),('J2 / r2',B,rk,m['lower'])]:
        cp=project(center);end=project(center+Vec2d(math.cos(body.angle),math.sin(body.angle))*radius*.86)
        pygame.draw.line(screen,white,cp,end,2);pygame.draw.circle(screen,white,end,3)
        pygame.draw.line(screen,white,(cp[0]-5,cp[1]),(cp[0]+5,cp[1]),1)
        pygame.draw.line(screen,white,(cp[0],cp[1]-5),(cp[0],cp[1]+5),1)
        screen.blit(font.render(name,True,white),(cp[0]+10,cp[1]+15))
        if abs(body.angular_velocity)>1e-5:
            sign=1 if body.angular_velocity>0 else -1
            arc=[project(center+Vec2d(math.cos(body.angle+sign*i*.06),math.sin(body.angle+sign*i*.06))*radius*1.4) for i in range(15)]
            pygame.draw.lines(screen,white,False,arc,1)
            end,prev=arc[-1],arc[-3];angle=math.atan2(end[1]-prev[1],end[0]-prev[0])
            pygame.draw.polygon(screen,white,[end,(end[0]-6*math.cos(angle-.5),end[1]-6*math.sin(angle-.5)),(end[0]-6*math.cos(angle+.5),end[1]-6*math.sin(angle+.5))])
    torque=m.get('native_guide_torque');known_sign=torque is not None
    torque=torque if known_sign else m['guide'].impulse/c['dt']
    load=tension_state(loop,torque,viewer.get('pretension_N'))
    if viewer.get('show_force_vectors',True):
        for arrow in load['force_arrows']:
            p=project(arrow['point']);value=arrow['magnitude_N']
            direction=Vec2d(*loop['force_units'][arrow['span']])*(1 if arrow['body']=='hip' else -1)
            shade=(249,127,95) if value>1e-8 and known_sign else gray
            length=32 if value>1e-8 else 18
            tip=(p[0]+direction.x*length,p[1]-direction.y*length)
            pygame.draw.line(screen,shade,p,tip,2 if value>1e-8 else 1)
            angle=math.atan2(tip[1]-p[1],tip[0]-p[0])
            pygame.draw.polygon(screen,shade,[tip,(tip[0]-6*math.cos(angle-.5),tip[1]-6*math.sin(angle-.5)),(tip[0]-6*math.cos(angle+.5),tip[1]-6*math.sin(angle+.5))])
    prefix='Delta T' if known_sign else '|Delta T| (sign unavailable)'
    message=f'Guide 2:1 | radii {rh*1000:.0f}/{rk*1000:.0f} mm | {prefix} {load["differential_N"]:.1f} N'
    note=(f'Inferred spans {load["tension_plus_N"]:.1f}/{load["tension_minus_N"]:.1f} N; viewer baseline only.' if load['pretension_known'] else 'Torque-equivalent arrows; pretension and total span forces unknown.')
    screen.blit(font.render(message,True,gold),(24,293))
    screen.blit(font.render(note+' Engine pin loads omit belt bearing loads.',True,gray),(24,314))
