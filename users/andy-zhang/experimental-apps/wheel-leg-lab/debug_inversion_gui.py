"""Live native Pygame/Pymunk inversion viewer, owned by Motion Lab.

Run python debug_inversion_gui.py [--config JSON] [--run] [--loop] or
--headless-check. SI profile; output live desktop Space.step and optional ignored
state/screenshot files. Fixed-pitch, ideal-routing/contact study, not hardware.
"""
import argparse
import json
import math
import os
from pathlib import Path
import sys
if '--headless-check' in sys.argv:
    os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
import pygame
import pymunk
import pymunk.pygame_util
import inversion
import invertible_spring as springs

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path);parser.add_argument('--run',action='store_true');parser.add_argument('--loop',action='store_true');parser.add_argument('--headless-check',action='store_true');parser.add_argument('--state-file',type=Path);parser.add_argument('--snapshot-file',type=Path)
    parser.add_argument('--quit-at-end',action='store_true')
    args=parser.parse_args();value=json.loads(args.config.read_text()) if args.config else {};c=inversion.config(value.get('config',value));m=inversion.build(c)
    pygame.init();screen=pygame.display.set_mode((1150,900),pygame.RESIZABLE);pygame.display.set_caption('IMPOSSIBLE pulley - historical ideal Pymunk study' if c['preset']=='dual_rope' else 'Live Pymunk - symmetric knee bellcrank')
    font=pygame.font.SysFont('Segoe UI',17);clock=pygame.time.Clock();paused=not args.run;running=True;accumulator=0.;steps=0;loops=0;last_report=0.;snapped=False
    initial_q,_,initial_A,initial_B,_=inversion.coordinates(m,c);minimum_angle=maximum_angle=math.degrees(initial_q);minimum_knee_right=initial_B.x-initial_A.x
    def advance():
        nonlocal steps,minimum_angle,maximum_angle,minimum_knee_right
        inversion.step(m,c);steps+=1
        q,_,A,B,_=inversion.coordinates(m,c);minimum_angle=min(minimum_angle,math.degrees(q));maximum_angle=max(maximum_angle,math.degrees(q));minimum_knee_right=min(minimum_knee_right,B.x-A.x)
    def report(status):
        if args.state_file:
            args.state_file.parent.mkdir(parents=True,exist_ok=True);args.state_file.write_text(json.dumps({'status':status,'pid':os.getpid(),'window_id':pygame.display.get_wm_info().get('window'),'t':m['t'],'solver_steps':steps,'loops':loops,'paused':paused,'mode':'native-live','model':'inversion','preset':c['preset'],'shape_count':len(m['space'].shapes),'constraint_count':len(m['space'].constraints),'minimum_angle_deg':minimum_angle,'maximum_angle_deg':maximum_angle,'minimum_knee_right_m':minimum_knee_right}),encoding='utf-8')
    def text(s,x,y):screen.blit(font.render(s,True,(231,234,222)),(x,y))
    def paint():
        W,H=screen.get_size();screen.fill((28,32,27));q,w,A,B,C=inversion.coordinates(m,c);s=springs.state(q,w,c,m['prepared'])
        text('Live Pymunk inversion | Space: run/pause  .: step  R: reset  Esc: close',20,20)
        text(f'{"IMPOSSIBLE pulley / historical" if c["preset"]=="dual_rope" else c["preset"]} | {c["fixture"]} | fixed pitch / ideal model',20,49)
        text(f't={m["t"]:.3f}s  theta={math.degrees(q):.1f}deg  motor={inversion.torque(m["t"],c):.2f}Nm  omega={w:.2f}rad/s',20,78)
        text(f'Cap compression={s["compression"]*1000:.1f}mm  red={s["red_tension"]:.1f}N  blue={s["blue_tension"]:.1f}N',20,107)
        if c['angle_limit_enabled']:text(f'Knee-right limits: {c["angle_min_deg"]:.0f} to {c["angle_max_deg"]:.0f}deg',20,134)
        max_y=A.y+2*c['length']+c['radius'];min_y=0 if c['fixture']=='ground' else A.y-2*c['length']-c['radius']
        scale=min((W-180)/(2*c['length']+2*c['radius']+.3),(H-190)/(max_y-min_y+.1));ox=W*.48-A.x*scale;oy=150+max_y*scale
        point=lambda p:(round(ox+p[0]*scale),round(oy-p[1]*scale))
        options=pymunk.pygame_util.DrawOptions(screen);options.transform=pymunk.Transform(a=scale,d=-scale,tx=ox,ty=oy);m['space'].debug_draw(options)
        g=s['geometry'];world=lambda p:tuple(B+pymunk.Vec2d(*springs.rot(p,m['upper'].angle)))
        if c['preset']=='dual_rope':
            for colour,rgb in [('red',(235,90,100)),('blue',(80,155,245))]:
                route=g['routes'][colour];active=g['active']==colour
                pieces=[{'kind':'line','a':route.get('eye',(g['cap_x'],route['feed'][1])),'b':route['feed']},*route['pieces']]
                for piece in pieces:pygame.draw.lines(screen,rgb,False,[point(world(p)) for p in springs.samples(piece)],3 if active else 1)
                pygame.draw.circle(screen,rgb,point(world(route['anchor'])),3)
            cap,seat=g['piston_cap_x'],g['fixed_seat_x'];ref=cap-s['takeup']
            pygame.draw.lines(screen,(185,190,175),True,[point(world(p)) for p in [(ref,-.015),(seat,-.015),(seat,.015),(ref,.015)]],2)
            pygame.draw.line(screen,(230,175,75),point(world((cap,0))),point(world((seat,0))),4)
            pygame.draw.line(screen,(175,215,125),point(world((cap,-.013))),point(world((cap,.013))),3)
            pygame.draw.line(screen,(185,190,175),point(world((cap,0))),point(world((g['cap_x'],0))),2)
            eye=c['rope_eye_offset'] if g.get('routing') in ('central_wrap','central_face') else c['routing_offset']+c['routing_radius']
            pygame.draw.line(screen,(185,190,175),point(world((g['cap_x'],-eye))),point(world((g['cap_x'],eye))),2)
        else:
            pygame.draw.line(screen,(210,145,235),point(B),point(world(g['crank_tip'])),5);pygame.draw.line(screen,(235,185,90),point(world(g['femur_anchor'])),point(world(g['crank_tip'])),3)
        text(('Actual floor contacts' if c['fixture']=='ground' else 'Fixed J1 / no floor')+('; three pins + guide + angle stops' if c['angle_limit_enabled'] else '; three pins + guide')+'; no commanded wheel height.',20,H-30)
    if args.headless_check:
        for _ in range(min(4000,round(c['duration']/c['dt']))):advance()
        paint();output=args.snapshot_file or Path(__file__).parent/'artifacts/inversion-native.png';output.parent.mkdir(parents=True,exist_ok=True);pygame.image.save(screen,str(output));assert math.isfinite(m['lower'].angle);report('closed');pygame.quit();print('PASS: live inversion Space stepped and official debug renderer drew',len(m['space'].shapes),'shapes /',len(m['space'].constraints),'constraints');return
    report('ready')
    try:
        while running:
            elapsed=min(clock.tick(60)/1000,.05)
            for e in pygame.event.get():
                if e.type==pygame.QUIT:running=False
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE:running=False
                    elif e.key==pygame.K_SPACE:paused=not paused;accumulator=0
                    elif e.key==pygame.K_PERIOD:paused=True;advance()
                    elif e.key==pygame.K_r:m=inversion.build(c);paused=True;accumulator=0
            if not paused:
                accumulator+=elapsed
                while accumulator>=c['dt']:
                    advance();accumulator-=c['dt']
                    if m['t']>=c['duration']:
                        if args.loop:m=inversion.build(c);loops+=1
                        else:paused=True;accumulator=0;running=not args.quit_at_end;break
            paint();pygame.display.flip()
            if args.snapshot_file and not snapped and steps>=min(1200,round(c['duration']/c['dt'])):
                args.snapshot_file.parent.mkdir(parents=True,exist_ok=True);pygame.image.save(screen,str(args.snapshot_file));snapped=True
            if pygame.time.get_ticks()-last_report>250:report('running' if not paused else 'ready');last_report=pygame.time.get_ticks()
    finally:report('closed');pygame.quit()

if __name__=='__main__':main()
