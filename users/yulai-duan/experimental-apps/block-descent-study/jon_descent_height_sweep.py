"""Reproduce matched October 18 100/150/250/300 mm passive block exits.

Run: python jon_single_leg_descent.py, then python jon_descent_height_sweep.py.
Inputs: pinned inputs/, previous run, SI kg/m/s parameters with assumed masses.
Outputs: ignored results/ models, trajectories, summaries and plots.
Limits: hip height held; no prescribed vertical motion, motor or full vehicle.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jon_single_leg_descent as b
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = b.ROOT
BASE_RAW = b.RAW
RAW = ROOT/'results/2026-10-18-jon-descent-heights'
OUT = RAW/'plots'
BENCH = RAW/'record'
HEIGHTS = [100, 150, 250, 300]
AVAILABLE = .6*(math.sin(math.radians(100))-math.sin(math.radians(135)))

def name(height): return f'height-{height}mm'

def extra(r):
    h=b.history(r['case']['name']); edge=r['metrics']['edge_time_s']
    active=h['time_s']>=edge
    stop=np.flatnonzero(active & (h['theta2_deg']<=100))
    landed=r['metrics']['floor_recontact_s']
    r['height_metrics']=dict(
        additional_geometric_travel_mm=1000*AVAILABLE,
        geometric_floor_reachable=r['case']['height']<=AVAILABLE,
        nominal_floor_gap_at_extension_limit_mm=1000*max(0,r['case']['height']-AVAILABLE),
        floor_arrival_after_edge_ms=None if landed is None else 1000*(landed-edge),
        first_extension_stop_after_edge_ms=None if not len(stop) else 1000*(h['time_s'][stop[0]]-edge),
        max_descent_mm=float(1000*max(h['wheel_z_m'][0]-h['wheel_z_m'])),
        final_floor_clearance_mm=float(1000*(h['wheel_z_m'][-1]-r['case']['radius'])),
        minimum_hip_angle_deg=float(min(h['theta2_deg'])),
        max_carriage_position_error_m=float(max(abs(h['x_m']-(r['case']['x0']+r['case']['speed']*h['time_s'])))))
    return r

def plot(results):
    colors=['#007d8a','#d67519','#7050a1','#bd3b59']
    fig,axs=b.plt.subplots(2,2,figsize=(13,8))
    for height,col in zip(HEIGHTS,colors):
        h=b.history(name(height));t=1000*(h['time_s']-h['edge_time_s'])
        series=[1000*(h['wheel_z_m'][0]-h['wheel_z_m']),h['extension_speed_mps'],h['theta2_deg'],h['joint_speed_radps']]
        for ax,y in zip(axs.flat,series):ax.plot(t,y,label=f'{height} mm block',color=col,lw=1.8)
    labels=['Wheel descent from starting height (mm)','Downward extension speed (m/s)','Hip angle (degrees)','Hip angular velocity (rad/s)']
    for ax,label in zip(axs.flat,labels):
        ax.set_ylabel(label);ax.set_xlabel('Time after wheel centre passes edge (ms)');ax.set_xlim(-10,500);ax.grid(alpha=.2)
    axs[0,0].axhline(1000*AVAILABLE,color='black',ls='--',lw=1,label='166.6 mm geometric travel limit')
    axs[0,0].axhline(100,color=colors[0],ls=':',lw=1)
    axs[0,0].axhline(150,color=colors[1],ls=':',lw=1)
    axs[0,0].legend(fontsize=9)
    axs[1,0].axhline(100,color='black',ls='--',lw=1)
    fig.suptitle('Jon V4 spring | matched 0.5 m/s single-leg block exits\nSame initial 135° hip pose; hip height held; no added damper or suspension motor')
    fig.tight_layout()
    for folder in [OUT,BENCH]:fig.savefig(folder/'height-profiles.png',dpi=170)
    b.plt.close(fig)

def main():
    for p in [RAW,OUT,BENCH]:p.mkdir(parents=True,exist_ok=True)
    checks=b.verify()
    (RAW/'source').mkdir(exist_ok=True)
    for p in b.INPUTS.iterdir():
        if p.is_file():shutil.copy2(p,RAW/'source'/p.name)
    b.RAW=RAW
    cases=[b.Case(name=name(h),height=h/1000) for h in HEIGHTS]
    cases += [b.Case(name=name(h)+'-half-dt',height=h/1000,dt=.0000625) for h in HEIGHTS]
    cases += [b.Case(name=name(h)+'-half-contact',height=h/1000,contact_time=.002) for h in [150,300]]
    results=[extra(b.run(c)) for c in cases]
    # Exact reproduction of the retained 100 mm baseline, plus reachability.
    old=json.loads((BASE_RAW/'fixed-v05-b0/results.json').read_text())
    for key in ['floor_recontact_s','peak_extension_speed_mps','peak_abs_joint_speed_radps']:
        assert results[0]['metrics'][key]==old['metrics'][key],key
    for r in results:
        assert (r['metrics']['floor_recontact_s'] is not None)==r['height_metrics']['geometric_floor_reachable']
        assert r['metrics']['max_coupling_error_rad']<.0001
        assert r['metrics']['max_path_error_m']<.0001
        # MuJoCo's soft stop allows a small transient overrun. Bound its wheel
        # displacement explicitly; it cannot bridge either unreachable gap.
        if not r['height_metrics']['geometric_floor_reachable']:
            assert r['height_metrics']['max_descent_mm']-1000*AVAILABLE<2.5
    sensitivity=[]
    for r in results[4:]:
        base=next(x for x in results[:4] if x['case']['height']==r['case']['height'])
        speed_delta=100*(r['metrics']['peak_extension_speed_mps']/base['metrics']['peak_extension_speed_mps']-1)
        arr=r['height_metrics']['floor_arrival_after_edge_ms'];orig=base['height_metrics']['floor_arrival_after_edge_ms']
        sensitivity.append(dict(case=r['case']['name'],peak_extension_speed_change_pct=speed_delta,
            arrival_change_ms=None if arr is None else arr-orig,
            stop_angle_change_deg=r['height_metrics']['minimum_hip_angle_deg']-base['height_metrics']['minimum_hip_angle_deg']))
        assert abs(speed_delta)<2,sensitivity[-1]
    checks['baseline_reproduced_exactly']=True
    checks['reachability_matches_all_integrations']=True
    source_hashes={}
    for p in [Path(__file__),Path(b.__file__),ROOT/'encode_jon_descent_video.swift']:
        shutil.copy2(p,RAW/'source'/p.name);source_hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    study=dict(source_commit=b.COMMIT,source_preset='v4-textbook-10mm.json',python=sys.version,mujoco=mujoco.__version__,numpy=np.__version__,
        checks=checks,source_sha256=source_hashes,cases=results,sensitivity=sensitivity,
        assumptions=['Held hip height and pitch; horizontal 0.5 m/s velocity fixture.',
        '135 degree initial hip angle in every case; 100-165 degree allowed range.',
        'Moving masses 0.6/0.65/1.5 kg are assumptions, not measurements.',
        'Jon V4 exact finite-idler spring; zero added damping; no suspension motor/inertia.',
        '250/300 mm lower floors exceed remaining travel; chassis motion is excluded.',
        'Soft joint stops and tire contact are numerical models, not calibrated hardware.'])
    for folder in [RAW,BENCH]:b.dump(folder/('study.json' if folder==RAW else 'results.json'),study)
    plot(results)
    print('SUMMARY',json.dumps([dict(height_mm=r['case']['height']*1000,**r['height_metrics'],peak_speed_mps=r['metrics']['peak_extension_speed_mps']) for r in results[:4]]),flush=True)
    print('SENSITIVITY',json.dumps(sensitivity),flush=True)

def spring_overlay(ren,d):
    s=b.Spring();q=float(d.joint('hip').qpos[0]);_,_,D,Q,psi,wrap=s.geometry(q);hip=d.body('chassis').xpos
    def pt(xz):return hip+np.array([xz[0],-.055,xz[1]])
    def line(a,bb,width=.002):
        scene=ren.scene;g=scene.geoms[scene.ngeom]
        mujoco.mjv_initGeom(g,mujoco.mjtGeom.mjGEOM_CAPSULE,np.zeros(3),np.zeros(3),np.eye(3).flatten(),np.array([.9,.4,.8,1.]))
        mujoco.mjv_connector(g,mujoco.mjtGeom.mjGEOM_CAPSULE,width,np.array(a),np.array(bb));scene.ngeom+=1
    line(pt((0,0)),pt(D),.004);line(pt(D),pt(Q))
    pts=[pt((s.su+s.rho*math.cos(a),s.sv+s.rho*math.sin(a))) for a in np.linspace(psi,psi-wrap,24)]
    for a,bb in zip(pts,pts[1:]):line(a,bb)
    line(pts[-1],pt((s.su+.09,s.sv+s.rho)))
    for j in range(16):line(pt((s.su+.09+j*.005,s.sv+s.rho+(.008 if j%2 else -.008))),pt((s.su+.09+(j+1)*.005,s.sv+s.rho+(.008 if (j+1)%2 else -.008))))

def render():
    b.RAW=RAW;frames=RAW/'frames-1x';frames.mkdir(exist_ok=True)
    cases=[]
    for height in HEIGHTS:
        m=mujoco.MjModel.from_xml_path(str(RAW/name(height)/'model.xml'))
        cases.append(dict(height=height,m=m,d=mujoco.MjData(m),p=np.load(RAW/name(height)/'poses.npz'),h=b.history(name(height)),ren=mujoco.Renderer(m,height=340,width=960)))
    fonts={n:ImageFont.truetype(str(Path(b.matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'),n) for n in [20,24,28,34]}
    errors=[];fps=60;nframes=120
    for frame in range(nframes):
        t=frame/fps;canvas=Image.new('RGB',(1920,1080),'#10252d');draw=ImageDraw.Draw(canvas)
        draw.text((24,16),'100 / 150 / 250 / 300 mm block exits | Jon V4 spring',font=fonts[34],fill='white')
        draw.text((24,62),'ACTUAL SPEED 1x | 0.5 m/s | same initial pose, spring and moving masses | all views same scale',font=fonts[24],fill='#bddde4')
        for i,item in enumerate(cases):
            x=(i%2)*960;y=110+(i//2)*430
            p=item['p'];k=int(np.argmin(abs(p['time_s']-t)));d=item['d'];m=item['m']
            d.qpos[:]=p['qpos'][k];d.qvel[:]=p['qvel'][k];mujoco.mj_forward(m,d);errors.append(abs(p['time_s'][k]-t))
            cam=mujoco.MjvCamera();cam.lookat[:]=[d.body('chassis').xpos[0]-.1,0,.45];cam.distance=1.35;cam.azimuth=90;cam.elevation=-5
            ren=item['ren'];ren.update_scene(d,camera=cam);spring_overlay(ren,d)
            canvas.paste(Image.fromarray(ren.render()),(x,y+36))
            h=item['h'];j=int(np.argmin(abs(h['time_s']-t)))
            floor=h['floor_load_N'][j]>1;block=h['block_load_N'][j]>1
            status='FLOOR CONTACT' if floor else 'ON BLOCK' if block else 'EXTENSION STOP' if h['theta2_deg'][j]<=100.05 else 'DESCENDING'
            draw.text((x+24,y),f'{item["height"]} mm | {status}',font=fonts[28],fill='#ffcf82')
            draw.text((x+24,y+377),f'Descent {1000*(h["wheel_z_m"][0]-h["wheel_z_m"][j]):.0f} mm | speed {h["extension_speed_mps"][j]:+.2f} m/s | hip {h["theta2_deg"][j]:.1f} deg',font=fonts[24],fill='white')
            if item['height']>1000*AVAILABLE:
                draw.text((x+24,y+407),f'Lower floor beyond travel; nominal gap {item["height"]-1000*AVAILABLE:.0f} mm at stop',font=fonts[20],fill='#ffcf82')
        draw.text((24,994),f't = {t:.3f} s | hip height held; available extra downward travel 166.6 mm',font=fonts[24],fill='#bddde4')
        draw.text((24,1034),'Computed fixture behavior; assumed masses and contact. No suspension motor or added damper. Spring drawing schematic.',font=fonts[20],fill='#bddde4')
        canvas.save(frames/f'{frame:05d}.png')
        if frame in [30,45,60,118]:canvas.save(OUT/f'preview-{frame}.png')
    for item in cases:item['ren'].close()
    b.dump(OUT/'render-provenance.json',dict(fps=fps,frames=nframes,duration_s=nframes/fps,playback_rate=1,frame_time_rule='t = frame / 60 seconds',max_pose_time_error_s=float(max(errors)),source_commit=b.COMMIT))
    print('Rendered',nframes,'actual-speed frames',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');args=ap.parse_args()
    render() if args.render else main()
