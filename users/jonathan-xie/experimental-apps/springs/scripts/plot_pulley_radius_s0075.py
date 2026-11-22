"""Render the quick S0075 comparison; run with python -B from springs root.
Reads .work/radius-s0075/results.json; mm/N/deg/Nm. Writes plots, CSV and JSON
under research/2026-11-22-s0075-pulley-radius. Static nominal comparison only.
"""
import pathlib,sys,json,csv,copy,hashlib
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=pathlib.Path.cwd();sys.path.insert(0,str(R.parent/'vsl-solver/v7'));import spring_lab as lab
D=R/'research/2026-11-22-s0075-pulley-radius';D.mkdir(parents=True,exist_ok=True);d=json.loads((R/'.work/radius-s0075/results.json').read_text());rows=[]
fig,axes=plt.subplots(1,2,figsize=(12,4.7),sharex=True);theta=np.linspace(120,180,601)
styles=[('baseline','Original 0.5 in','#244C70'),('free_position_1p5','1.5 in, move Su/Sv','#CA6B21'),('preload_refit_diagnostic','1.5 in, also reset preloads','#258369')]
for key,title,color in styles:
 rec=d[key] if key=='baseline' else d[key]['record'];p={**rec['parameters'],**rec['geometry']};z=lab.profile(p,601);ix=np.searchsorted(z['theta'],theta);k=np.array([s['k'] for s in rec['springs']]);p0=np.array([s['p0'] for s in rec['springs']]);peaks=[]
 for j,mask in enumerate(rec['masks']):
  mass=sum(p[x] for x in ['m1','m2','m3','m5','m6'])+rec['payloads'][j]/4;mask=np.array(mask);F=mask@p0+(mask@k)*z['delta'];tau=F*z['A']-mass*p['g']*z['J']+z['gravityOffset'];t=tau[ix];axes[j].plot(theta,t,label=title,color=color,lw=2);peaks.append(float(np.max(abs(t))));
  rows.extend({'variant':key,'payload_kg':rec['payloads'][j],'theta2_deg':float(a),'residual_Nm':float(b),'cable_force_N':float(f)} for a,b,f in zip(theta,t,F[ix]))
 print(key,'dense_peak', [x['maxAbs'] for x in rec['cases']],'force_minmax',[(min(x['cable_force_N'] for x in rows if x['variant']==key and x['payload_kg']==case),max(x['cable_force_N'] for x in rows if x['variant']==key and x['payload_kg']==case)) for case in rec['payloads']])
for j,ax in enumerate(axes):
 ax.set(title=('Unloaded' if j==0 else '+70 kg total payload'),xlabel='Knee angle theta2 (deg)',ylabel='Residual hip torque (N m)');ax.axhline(0,color='#81919D',lw=.7);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
axes[0].legend(loc='upper left',fontsize=8);fig.suptitle('S0075: increasing the spring pulley radius from 0.5 to 1.5 inches',fontsize=14);fig.text(.5,.025,'Horn radius 50 mm and both spring rates fixed. Curves use the saved S0075 mass model (alpha = 0 deg).',ha='center',fontsize=9);fig.tight_layout(rect=[0,.055,1,.95]);fig.savefig(D/'residual-comparison.png',dpi=160);fig.savefig(D/'residual-comparison.svg');plt.close(fig)
with (D/'residual-curves.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(D/'results.json').write_text(json.dumps(d,indent=2),encoding='utf8')
text='''# S0075 pulley-radius quick check — 2026-11-22

Source: saved S0075 in springs/v6-spring-solutions.xlsx, evaluated read-only with
vsl-solver/v7/spring_lab.py. Use the record geometry, not the older duplicate
spring fields inside parameters. Saved alpha=0 deg and working theta2=120–180 deg.
Both existing Swift springs, r_h=50 mm, nu=0 and payload swap masks remain fixed.
All original workbooks and solver files remain unchanged.

## Results (peak absolute residual hip torque, N m)

| Case | Su mm | Sv mm | unloaded | +70 kg |
|---|---:|---:|---:|---:|
| Original rs12.7 |12.601|75.4|0.0631|0.6817|
| rs38.1; only Su/Sv changed |70.886|126.2|4.0884|9.5300|
| rs38.1; also reset preloads (diagnostic) |78.431|126.2|1.5502|1.5502|

Original preload forces are 640.264 and 1365.461 N at theta2=90 deg. Diagnostic
forces are 581.520 and 1189.855 N. Spring rates remain21.89085 and48.15988 N/mm.
Normal working stroke remains about49.9–50.0 mm. All three variants pass the
backend's rated spring envelopes and unloaded -50 deg inversion check, including
its Sv-r_h>=2rs clearance condition. The larger radius forces Sv>=126.2 mm, 50.8 mm
above the original. Su also increases materially; packaging is an important cost.
The original Su bound +/-30 mm gives much worse17.20/37.94 Nm; moving beyond
that original bound is necessary for the reported useful fit.

The fit minimizes the worst absolute residual over both payload cases. Primary
fit uses12 deterministic starting points with Sv126.2–400 and Su+/-150 mm, fixed
preloads; preload diagnostic uses4 starts and the same position bounds. This is
a bounded quick search, not a proof of the global optimum. Selection used401
uniform angles; validation used6001 uniform angles plus exact profile critical
points. The initial attempt failed because the backend adds variable critical
points to the grid; optimization now selects a fixed grid from that profile.

This comparison holds the original spring rates and mass/angle assumptions.
Preload adjustment is explicitly a diagnostic beyond the requested Su/Sv-only
change. It shows that much of the error is installation bias rather than an
unmanageable increase in nonlinearity. Static spring-envelope checks do not
certify rope fatigue, sheave bearings, guides or physical collision geometry.
A1.5-inch radius is a cable-bending design input, not a verified4kN cable WLL.

Reproduce: python -B scripts/pulley_radius_s0075.py from springs root with numpy
and scipy. Numeric evidence is results.json; residual-curves.csv and the rendered
PNG/SVG compare the three useful variants. No saved S0075 overwrite, commit or
remote publication is part of this task.
'''
(D/'README.md').write_text(text,encoding='utf8');print('saved',D)