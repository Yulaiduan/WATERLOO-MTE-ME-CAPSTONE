"""View the live fixture using the official Pymunk/Pygame renderer.

Run: python debug_gui.py [--config FILE] or --headless-check.
Inputs: saved config in SI, native pause/step/reset and body-selection controls.
Outputs: live desktop inspection, or ignored artifacts/native-debug.png in check mode.
Requires Pymunk and pygame-ce; prescribed-height fixture, not a CAD or tire-contact editor.
"""
import argparse
import json
import math
import os
from pathlib import Path
import sys

if '--headless-check' in sys.argv:
    os.environ['SDL_VIDEODRIVER']='dummy'
    os.environ['SDL_AUDIODRIVER']='dummy'

import pygame
import pymunk
import pymunk.pygame_util
from physics import config, build, drive
from native_suspension import draw as draw_suspension
from native_guide_belt import draw as draw_guide, capture_torque

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',type=Path)
    parser.add_argument('--headless-check',action='store_true')
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--loop',action='store_true')
    parser.add_argument('--state-file',type=Path)
    parser.add_argument('--snapshot-file',type=Path)
    parser.add_argument('--screenshot',type=Path,default=Path(__file__).parent/'artifacts/native-debug.png')
    args=parser.parse_args()
    values=json.loads(args.config.read_text()) if args.config else None
    c=config(values.get('config',values) if values else None)
    viewer=values.get('guide_visualization',{}) if values else {}
    pygame.init();screen=pygame.display.set_mode((1180,1020 if c['aux_spring_enabled'] or c['chassis_shape_enabled'] or c['guide_pulleys_visible'] else 940),pygame.RESIZABLE)
    pygame.display.set_caption('Pymunk live model - Capstone suspension')
    font=pygame.font.SysFont('Segoe UI',16);small=pygame.font.SysFont('Segoe UI',14);title=pygame.font.SysFont('Segoe UI',23)
    clock=pygame.time.Clock();model=build(c);t=0.;paused=not args.run;accumulator=0.;selected='lower';command=0.;steps=0;loops=0
    def reset():
        nonlocal model,t,paused,accumulator,command
        model=build(c);t=0.;paused=True;accumulator=0.;command=0.
    def step():
        nonlocal t,command,steps
        previous={key:model[key].velocity for key in ('upper','lower','hip','wheel')}
        spins={key:model[key].angular_velocity for key in ('upper','lower','wheel')}
        command,actuator,*_=drive(model,c,t,c['dt']);model['live_actuator']=actuator;model['space'].step(c['dt']);t+=c['dt'];steps+=1
        model['native_guide_torque']=capture_torque(model,c,previous,spins,c['dt'])
        model['live_acceleration']={key:(model[key].velocity-value)/c['dt'] for key,value in previous.items()}
    def report(status='running'):
        if args.state_file:
            args.state_file.parent.mkdir(parents=True,exist_ok=True)
            args.state_file.write_text(json.dumps({'status':status,'pid':os.getpid(),'mode':'native-live','window_id':pygame.display.get_wm_info().get('window'),'t':t,'solver_steps':steps,'loops':loops,'paused':paused,'shape_count':len(model['space'].shapes),'constraint_count':len(model['space'].constraints),'spring_topology':c['spring_topology']}),encoding='utf-8')
    def text(value,x,y,f=font,color=(225,235,229)):
        screen.blit(f.render(str(value),True,color),(x,y))
    buttons={}
    def paint():
        nonlocal buttons
        W,H=screen.get_size();side=W-310;screen.fill((23,30,27));pygame.draw.rect(screen,(31,42,36),(side,0,310,H))
        text('Actual Pymunk Space',24,18,title);text('LIVE Space.step solver · '+('PAUSED' if paused else 'RUNNING'),24,49,small,(166,190,173))
        buttons={name:pygame.Rect(24+i*102,82,94,34) for i,name in enumerate(['Run' if paused else 'Pause','Step','Reset'])}
        for name,rect in buttons.items():pygame.draw.rect(screen,(56,87,66),rect,border_radius=4);text(name,rect.x+15,rect.y+5)
        text('Space: pause/run    . : one solver step    R: reset    Click body: inspect',24,128,small,(166,190,173))
        L=c['length'];max_height=2*L*math.sin(math.radians(c['theta_max']))+c['radius']
        min_y=-max_height if c['fixture']=='hip' else -c['radius']
        max_y=.10 if c['fixture']=='hip' else 2*L+.08
        scale=min((side-100)/(L+c['radius']+.15),(H-(380 if c['guide_pulleys_visible'] else 330))/(max_y-min_y))
        ox=side*.38;oy=(335 if c['guide_pulleys_visible'] else 285)+max_y*scale
        options=pymunk.pygame_util.DrawOptions(screen)
        options.transform=pymunk.Transform(a=scale,d=-scale,tx=ox,ty=oy)
        model['space'].debug_draw(options)
        draw_suspension(screen,model,c,lambda p:(round(ox+p[0]*scale),round(oy-p[1]*scale)),small)
        draw_guide(screen,model,c,lambda p:(round(ox+p[0]*scale),round(oy-p[1]*scale)),small,viewer)
        for name in ['upper','lower', 'moving']+(['hip'] if c['aux_spring_enabled'] or c['chassis_shape_enabled'] else []):
            b=model[name];p=(round(ox+b.position.x*scale),round(oy-b.position.y*scale))
            pygame.draw.line(screen,(220,105,168),(p[0]-4,p[1]),(p[0]+4,p[1]),1)
            pygame.draw.line(screen,(220,105,168),(p[0],p[1]-4),(p[0],p[1]+4),1)
        text(f'{c["radius"]*1000:.0f} mm wheel radius | {c["extension"]*1000:.0f} mm extension | pink crosses: centres',24,H-45,small,(166,190,173))
        text(f't = {t:.3f} s | '+(f'height command = {command*1000:.1f} mm' if c['target']=='position' else f'diagnostic input = {command:.2f}'),24,H-23,small)
        x=side+18;y=22;text('Engine object inspector',x,y,title);y+=42
        for key in ['upper','lower','wheel','hip']:
            b=model[key];text(f'{key}: {"static" if b.body_type==pymunk.Body.STATIC else "dynamic"}',x,y);y+=25
        y+=14;text('Selected: '+selected,x,y);y+=28;b=model[selected]
        acceleration=model.get('live_acceleration',{}).get(selected,pymunk.Vec2d(0,0))
        for value in [f'Mass: {b.mass:.3g} kg',f'Inertia: {b.moment:.5g} kg m2',f'Angle: {math.degrees(b.angle):.2f} deg',f'Velocity: ({b.velocity.x:.3f}, {b.velocity.y:.3f}) m/s',f'Acceleration: ({acceleration.x:.2f}, {acceleration.y:.2f}) m/s2',f'Angular speed: {b.angular_velocity:.3f} rad/s']:
            text(value,x,y,small);y+=23
        y+=14;text('Actual constraints',x,y);y+=29
        for key in ['j1','j2','j3','guide','spring','stop']+(['wheel_drive'] if model.get('wheel_drive') else [])+(['driver'] if model.get('driver') else []):
            if model[key] is None:continue
            text(f'{key}: {type(model[key]).__name__}',x,y,small);y+=23
        y+=10;text('Physical guide: 2:1 carrier',x,y,small);y+=23
        text('Absolute GearJoint ratio: -1',x,y,small);y+=23
        text(f'Spring k: {c["stiffness"]:.0f} N/m',x,y,small);y+=23
        text(f'Free length: {model["rest"]*1000:.1f} mm',x,y,small);y+=30
        text('Solver joint resultants',x,y);y+=26
        for key in ['j1','j2','j3']:
            text(f'{key}: {model[key].impulse/c["dt"]:.2f} N',x,y,small);y+=22
        text(f'Guide torque magnitude: {model["guide"].impulse/c["dt"]:.2f} N m',x,y,small);y+=22
        lower=model['lower'];knee=model['upper'].local_to_world((c['length']/2,0))
        if model['manual_spring']:
            moment=model.get('spring_torques',{}).get('lower',0.)+(lower.position-knee).cross(model.get('spring_loads',{}).get('lower',pymunk.Vec2d(0,0)))
        elif model['cache'].get('n') is not None:
            moment=(lower.local_to_world(model['spring'].anchor_b)-knee).cross(model['cache']['n']*model['spring'].impulse/c['dt'])
        else:moment=0.
        text(f'Spring about knee: {moment:.2f} N m',x,y,small);y+=22
        text(f'Knee actuator: {model.get("live_actuator",0.):.2f} N m',x,y,small);y+=22
        if model.get('auxiliary',{}).get('enabled'):
            state=model.get('auxiliary_state',{})
            text(f'Ride strut force: {state.get("tension",0.):.2f} N',x,y,small);y+=22
            text(f'Ride k / c: {c["aux_stiffness"]:.0f} / {c["aux_damping"]:.0f}',x,y,small);y+=22
            text(f'Ride free length: {model["auxiliary"]["config"]["rest_length"]*1000:.1f} mm',x,y,small);y+=22
        text('Geometry shapes are sensors.',x,H-53,small,(166,190,173))
        text('No tire / terrain contact in this bench.',x,H-31,small,(166,190,173))
        return ox,oy,scale,side
    if args.headless_check:
        for _ in range(1200):step()
        paint();args.screenshot.parent.mkdir(parents=True,exist_ok=True);pygame.image.save(screen,str(args.screenshot))
        assert len(model['space'].shapes)==3+int(c['aux_spring_enabled'] or c['chassis_shape_enabled'])+2*int(c['guide_pulleys_visible']) and len(model['space'].constraints)==6-int(model['manual_spring'])+int(c['wheel_drive_locked'])+int(c['target']=='position')
        assert math.isfinite(model['lower'].angle)
        print(f"PASS: live Pymunk stepped, official pygame debug_draw rendered {len(model['space'].shapes)} shapes and {len(model['space'].constraints)} constraints.")
        pygame.quit();return
    running=True;last_report=0.;snapshot_taken=False;report('ready')
    while running:
        elapsed=min(clock.tick(60)/1000,.1);ox,oy,scale,side=paint()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:running=False
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE:paused=not paused;accumulator=0.
                elif event.key==pygame.K_r:reset()
                elif event.key==pygame.K_PERIOD:paused=True;step()
                elif event.key==pygame.K_ESCAPE:running=False
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                clicked=next((name for name,rect in buttons.items() if rect.collidepoint(event.pos)),None)
                if clicked in ['Run','Pause']:paused=not paused;accumulator=0.
                elif clicked=='Step':paused=True;step()
                elif clicked=='Reset':reset()
                elif event.pos[0]<side:
                    point=((event.pos[0]-ox)/scale,(oy-event.pos[1])/scale)
                    hit=model['space'].point_query_nearest(point,.03,pymunk.ShapeFilter())
                    if hit:
                        selected=next((key for key in ['upper','lower','wheel','hip'] if model[key] is hit.shape.body),selected)
        if not paused:
            accumulator+=elapsed
            while accumulator>=c['dt']:
                step();accumulator-=c['dt']
                if t>=c['duration']:
                    if args.loop:model=build(c);t=0.;loops+=1
                    else:paused=True;accumulator=0.;break
        pygame.display.flip()
        if args.snapshot_file and not snapshot_taken and steps>=min(600,int(c['duration']/c['dt'])):
            args.snapshot_file.parent.mkdir(parents=True,exist_ok=True);pygame.image.save(screen,str(args.snapshot_file));snapshot_taken=True
        if pygame.time.get_ticks()-last_report>=200:report();last_report=pygame.time.get_ticks()
    report('closed')
    pygame.quit()

if __name__=='__main__':main()
