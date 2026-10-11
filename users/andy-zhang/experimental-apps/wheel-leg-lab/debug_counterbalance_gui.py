"""Show the actual live Pymunk constant-lift lever in a desktop window.

Run: python debug_counterbalance_gui.py --config FILE --run --loop, or
--headless-check. Inputs: counterbalance SI profile, pause/step/reset controls.
Outputs: live solving, owned JSON status and optional ignored PNG snapshot.
Requires pygame/Pymunk/SciPy. Official engine drawing plus schematic finite
coil/rope overlay; no contact, hardware packaging or structure verification.
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
import counterbalance as study


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',type=Path);parser.add_argument('--run',action='store_true')
    parser.add_argument('--loop',action='store_true');parser.add_argument('--headless-check',action='store_true')
    parser.add_argument('--state-file',type=Path);parser.add_argument('--snapshot-file',type=Path)
    parser.add_argument('--screenshot',type=Path,default=Path(__file__).parent/'artifacts/native-counterbalance.png')
    args=parser.parse_args();values=json.loads(args.config.read_text()) if args.config else {}
    c=study.config(values.get('config',values));model=study.build(c)
    pygame.init();screen=pygame.display.set_mode((1180,860),pygame.RESIZABLE)
    pygame.display.set_caption('Pymunk LIVE - constant-lift lever')
    font=pygame.font.SysFont('Segoe UI',16);small=pygame.font.SysFont('Segoe UI',14);title=pygame.font.SysFont('Segoe UI',23)
    clock=pygame.time.Clock();paused=not args.run;t=0.;steps=0;loops=0;accumulator=0.;row=None;buttons={};snapshot=False
    def reset():
        nonlocal model,t,row,accumulator
        model=study.build(c);t=0.;row=None;accumulator=0.
    def step():
        nonlocal t,steps,row
        body=model['lever'];velocity=body.velocity;spin=body.angular_velocity
        study.drive(model,c,t,c['dt']);model['space'].step(c['dt']);t+=c['dt'];steps+=1
        row=study.telemetry(model,c,t,velocity,spin,c['dt'])
    def report(status='running'):
        if args.state_file:
            args.state_file.parent.mkdir(parents=True,exist_ok=True)
            args.state_file.write_text(json.dumps({'status':status,'mode':'native-live','model':'counterbalance','pid':os.getpid(),'window_id':pygame.display.get_wm_info().get('window'),'t':t,'solver_steps':steps,'loops':loops,'paused':paused,'shape_count':len(model['space'].shapes),'constraint_count':len(model['space'].constraints)}),encoding='utf-8')
    def text(value,x,y,f=font,color=(220,236,225)):screen.blit(f.render(str(value),True,color),(x,y))
    def paint():
        nonlocal buttons
        W,H=screen.get_size();side=W-320;screen.fill((23,30,27));pygame.draw.rect(screen,(31,42,36),(side,0,320,H))
        text('Actual Pymunk Space - constant-lift lever',24,18,title)
        text('LIVE Space.step | '+('PAUSED' if paused else 'RUNNING')+' | '+c['mode']+' dynamics',24,49,small,(164,190,173))
        buttons={name:pygame.Rect(24+i*102,80,94,34) for i,name in enumerate(['Run' if paused else 'Pause','Step','Reset'])}
        for name,rect in buttons.items():pygame.draw.rect(screen,(56,87,66),rect,border_radius=4);text(name,rect.x+15,rect.y+5)
        text('Space: pause/run   . : one solver step   R: reset   Esc: close',24,125,small)
        text('Zero-effective spring: coil force varies; elastic vertical lift is constant.' if c['law']=='zero_effective' else 'Ordinary finite-free-length spring: elastic lift varies with angle.',24,152,small)
        text('k H R = g (payload m L + lever mass L/2) at exact balance.',24,176,small)
        L=c['length'];height=max(L,c['anchor_height']);scale=min((side-100)/(2.2*L),(H-300)/(2*height+.08))
        ox=side*.42;oy=270+height*scale
        project=lambda p:(round(ox+p[0]*scale),round(oy-p[1]*scale))
        options=pymunk.pygame_util.DrawOptions(screen);options.transform=pymunk.Transform(a=scale,d=-scale,tx=ox,ty=oy)
        model['space'].debug_draw(options)
        pose=study.frame(model,c,t);a,b=project(pose['anchor']),project(pose['attach'])
        colour=(239,135,199)
        pygame.draw.line(screen,colour,a,b,2)
        for key,label in [('pivot','O'),('anchor','A / H'),('attach','B / R'),('tip','Payload / L')]:
            p=project(pose[key]);pygame.draw.circle(screen,colour,p,4);text(label,p[0]+10,p[1]-20,small)
        if row and row['end_force_N']:
            start=project(pose['tip']);sign=1 if row['end_force_N']>0 else -1;end=(start[0],start[1]-sign*60)
            pygame.draw.line(screen,(243,111,101),start,end,3)
            pygame.draw.lines(screen,(243,111,101),False,[(end[0]-6,end[1]+sign*10),end,(end[0]+6,end[1]+sign*10)],3)
            text(f'End C: {row["end_force_N"]:.2f} N',end[0]+12,end[1],small)
        pygame.draw.line(screen,(120,145,131),project([0,-height]),project([0,height]),1)
        state=model.get('spring_state') or study.forces(model['lever'].angle,model['lever'].angular_velocity,c)
        # Physical finite coil is shown as a separate routed inset, not a zero-size coil.
        coil_length=state['coil_length_m'];length=max(35,min(240,coil_length*500));x,y=24,224
        points=[(x,y)]
        for i in range(1,24):points.append((x+length*i/24,y+(0 if i in (1,23) else (7 if i%2 else -7))))
        points.append((x+length,y));pygame.draw.lines(screen,colour,False,points,2)
        text(f'Routed coil: {coil_length*1000:.1f} mm | {state["spring_force_N"]:.2f} N | {c["law"]}',x,243,small)
        x=side+17;y=22;text('Live engine inspector',x,y,title);y+=40
        body=model['lever'];text('One body: uniform lever + point payload',x,y,small);y+=31
        for value in [f'Mass {body.mass:.3f} kg',f'COM inertia {body.moment:.5f} kg m2',f'Angle {math.degrees(body.angle):.2f} deg',f'Angular speed {body.angular_velocity:.3f} rad/s',f'COM speed ({body.velocity.x:.3f}, {body.velocity.y:.3f}) m/s',f'Rate k {c["stiffness"]:.3f} N/m',f'L / R / H {L*1000:.0f} / {c["spring_radius"]*1000:.0f} / {c["anchor_height"]*1000:.0f} mm']:
            text(value,x,y,small);y+=25
        y+=15;text('Actual constraints',x,y);y+=29
        text('PivotJoint at O',x,y,small);y+=25
        text('SimpleMotor: prescribed angle' if model['motor'] else 'No holding motor / controller',x,y,small);y+=40
        if row:
            for value in [f'Pin force {row["joint_force_N"]:.2f} N',f'Pin Fx / Fy {row["joint_fx"]:.2f} / {row["joint_fy"]:.2f} N',f'End force {row["end_force_N"]:.2f} N / {row["end_force_kgf"]:.3f} kgf',f'End moment {row["end_force_moment_Nm"]:.3f} N m',f'End velocity {row["tip_velocity_y"]:.4f} m/s',f'Driver torque {row["driver_torque_Nm"]:.3f} N m',f'Spring moment {row["spring_moment_Nm"]:.3f} N m',f'Angular accel {row["angular_acceleration_rad_s2"]:.3f} rad/s2',f'Equivalent lift {row["equivalent_support_N"]:.3f} N',f'Energy {row["mechanical_energy_J"]:.3f} J']:
                text(value,x,y,small);y+=25
        text(f't {t:.3f} s | {steps} live steps | {loops} loops',24,H-48,small)
        text('Engine shapes are sensors; coil routing is schematic and massless.',24,H-26,small)
    if args.headless_check:
        for _ in range(min(1200,int(c['duration']/c['dt']))):step()
        paint();args.screenshot.parent.mkdir(parents=True,exist_ok=True);pygame.image.save(screen,str(args.screenshot))
        assert len(model['space'].shapes)==3 and len(model['space'].constraints)==1+int(c['mode']=='prescribed')
        assert math.isfinite(model['lever'].angle)
        print(f'PASS: actual live lever stepped/rendered, {steps} steps, 3 shapes, {len(model["space"].constraints)} constraints.');pygame.quit();return
    running=True;last_report=0;report('ready')
    while running:
        elapsed=min(clock.tick(60)/1000,.1);paint()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:running=False
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:running=False
                elif event.key==pygame.K_SPACE:paused=not paused;accumulator=0.
                elif event.key==pygame.K_PERIOD:paused=True;step()
                elif event.key==pygame.K_r:reset();paused=True
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                clicked=next((name for name,rect in buttons.items() if rect.collidepoint(event.pos)),None)
                if clicked in ('Run','Pause'):paused=not paused;accumulator=0.
                elif clicked=='Step':paused=True;step()
                elif clicked=='Reset':reset();paused=True
        if not paused:
            accumulator+=elapsed
            while accumulator>=c['dt']:
                step();accumulator-=c['dt']
                bound=not math.radians(c['theta_min_deg'])<model['lever'].angle<math.radians(c['theta_max_deg'])
                if t>=c['duration'] or bound:
                    if args.loop:reset();loops+=1
                    else:paused=True;accumulator=0.;break
        pygame.display.flip()
        if args.snapshot_file and not snapshot and steps>=min(600,int(c['duration']/c['dt'])):
            args.snapshot_file.parent.mkdir(parents=True,exist_ok=True);pygame.image.save(screen,str(args.snapshot_file));snapshot=True
        if pygame.time.get_ticks()-last_report>=200:report();last_report=pygame.time.get_ticks()
    report('closed');pygame.quit()

if __name__=='__main__':main()
