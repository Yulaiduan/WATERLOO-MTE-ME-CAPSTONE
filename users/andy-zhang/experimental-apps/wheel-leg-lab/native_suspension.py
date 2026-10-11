"""Draw suspension force sites and coil travel over the live engine debug view.

Invocation: draw(screen, model, SI_config, world_to_pixel, font). Output: Pygame
overlay of ideal massless mechanisms, separate from actual engine shapes.
Uses actual body poses; coil inset shows physical length (metres).
Requires pygame/Pymunk; routing is schematic, not a collision or CAD model.
"""
import math
import pygame
from spring_mechanisms import CATALOG, geometry_from_bodies, spring_law


def draw(screen, model, c, project, font):
    if not model['manual_spring']:return
    g=geometry_from_bodies({key:model[key] for key in ('hip','upper','lower')},c)
    law=model.get('spring_state') or spring_law(g['input_length'],g['input_speed'],dict(c,rest_length=model['rest']),model['spring_input_reference'])
    colour=(238,139,199) if not law['slack'] else (123,144,132)
    a,b=(project(g['anchors'][key]['world']) for key in ('a','b'))
    def segment(p,q,width=2,color=colour):pygame.draw.line(screen,color,p,q,width)
    def coil(p,q,shade=colour):
        dx,dy=q[0]-p[0],q[1]-p[1];length=max(1.,math.hypot(dx,dy));nx,ny=-dy/length,dx/length
        points=[p]
        for i in range(1,20):
            t=i/20;offset=0 if i in (1,19) else (7 if i%2 else -7)
            points.append((p[0]+dx*t+nx*offset,p[1]+dy*t+ny*offset))
        points.append(q);pygame.draw.lines(screen,shade,False,points,2)
    L=c['length'];hip=model['upper'].local_to_world((-L/2,0));knee=model['upper'].local_to_world((L/2,0))
    if c['spring_topology']=='gravity_balance':
        cp=project(model['hip'].position);segment(cp,a,3,(155,170,157))
        if c['aux_spring_enabled'] or c['chassis_shape_enabled']:screen.blit(font.render(f'Chassis / J1 mass: {c["chassis_mass"]:.1f} kg',True,(195,214,200)),(cp[0]-70,cp[1]-48))
        screen.blit(font.render(f'H {-c["spring_chassis_y"]*1000:.0f} mm',True,(170,188,175)),(cp[0]-78,(cp[1]+a[1])//2))
        screen.blit(font.render(f'R {c["spring_upper_fraction"]*L*1000:.0f} mm',True,(170,188,175)),(b[0]+12,b[1]-19))
    if g['kind']=='pulley':
        centre=hip if c['spring_topology']=='hip_pulley' else knee
        cp=project(centre);edge=project((centre.x+c['spring_pulley_radius'],centre.y))
        radius=max(5,abs(edge[0]-cp[0]));pygame.draw.circle(screen,colour,cp,radius,2)
        segment(cp,a);segment(a,b,2,(229,203,103))
    elif c['spring_topology'].endswith('bellcrank'):
        pivot=project(hip if c['spring_topology']=='hip_bellcrank' else knee)
        segment(pivot,b,5);coil(a,b)
    elif c.get('spring_force_law')=='zero_effective':segment(a,b,2,(229,203,103))
    else:coil(a,b)
    for site in g['force_sites']:
        p=project(site['world']);pygame.draw.circle(screen,colour,p,4)
        magnitude=law['tension'];direction=site['direction'];sign=1 if magnitude>=0 else -1
        tip=(p[0]+sign*direction[0]*28,p[1]-sign*direction[1]*28)
        segment(p,tip,2,(247,213,103))
    screen.blit(font.render(CATALOG[c['spring_topology']]['label'],True,colour),(24,153))
    x,y=32,197;draw_length=max(25,min(210,law['coil_length']*650))
    if c['spring_transmission']!='direct':
        pygame.draw.rect(screen,(148,164,153),(x-8,y-17,240,35),1)
        segment((x-20,y),(x+draw_length+42,y),2,(229,203,103))
        segment((x+draw_length,y-17),(x+draw_length,y+17),3)
    coil((x,y),(x+draw_length,y))
    text=f"Coil {law['coil_length']*1000:.1f} mm | {law['coil_load']:.1f} N | input {g['input_length']*1000:.1f} mm | {'SLACK' if law['slack'] else 'engaged'}"
    screen.blit(font.render(text,True,(195,214,200)),(24,224))
    screen.blit(font.render('Spring / routing overlay: ideal massless mechanism',True,(148,170,155)),(24,246))
    if model.get('auxiliary',{}).get('enabled'):
        ag=geometry_from_bodies({key:model[key] for key in ('hip','upper','lower')},model['auxiliary']['config'])
        alaw=model.get('auxiliary_state') or spring_law(ag['input_length'],ag['input_speed'],model['auxiliary']['config'],model['auxiliary']['input_ref'])
        aa,ab=(project(ag['anchors'][key]['world']) for key in ('a','b'))
        purple=(183,154,237);coil(aa,ab,purple)
        for point in (aa,ab):pygame.draw.circle(screen,purple,point,5,2)
        screen.blit(font.render(f'Ride spring + damper: {alaw["tension"]:.1f} N | k {c["aux_stiffness"]:.0f} N/m | c {c["aux_damping"]:.0f} N s/m',True,purple),(24,269))
        screen.blit(font.render('Ride strut',True,purple),((aa[0]+ab[0])//2+28,(aa[1]+ab[1])//2-38))
