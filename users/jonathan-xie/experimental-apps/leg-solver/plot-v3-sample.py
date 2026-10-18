"""Render V3 hip-horn sample geometry and full-range support/torque figures.

Run: python plot-v3-sample.py (after node verify-spring.cjs --output).
Inputs: adjacent v3-full-range.csv and v3-verification.json; mm/deg/N/Nm.
Dependencies: NumPy and Matplotlib. Outputs adjacent PNG/SVG figures.
Limitations: prescribed 10 kg-equivalent wheel load, ideal tension spring,
zero moving mass; calculated fit, not a selected or tested physical shock.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle

out=Path(__file__).resolve().parent
data=np.genfromtxt(out/'v3-full-range.csv',delimiter=',',names=True)
verification=json.loads((out/'v3-verification.json').read_text())
navy,teal,pink,red,gray,blue='#193745','#087f82','#bb408b','#c43f55','#738694','#307cef'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'text.color':navy,'axes.labelcolor':navy,'axes.edgecolor':'#b8c8d1','svg.fonttype':'none'})
t=data['theta2'];ratio=data['supportRatio']
fig,axs=plt.subplots(3,1,figsize=(12,12),gridspec_kw={'height_ratios':[1.3,.8,1]})
fig.subplots_adjust(left=.10,right=.97,top=.90,bottom=.12,hspace=.48)
fig.suptitle('Hip tension horn: the fit over the full 90–270° travel',x=.10,ha='left',y=.969,fontsize=20,weight='bold')
fig.text(.10,.928,'Sample A · L₂ = L₃ = 300 mm · q_ab = 2 · α = 0° · F_z = 98.1 N · zero moving mass',color=gray)
ax=axs[0];ax.plot(t,ratio,color=teal,lw=2.4);ax.set_yscale('symlog',linthresh=.5,linscale=.8);ax.set(xlim=(90,270),ylim=(-300,300),ylabel=r'$F_{eq}/(mg)$  [symmetric-log scale]')
ax.axhline(1,color=gray,ls='--');ax.axhline(0,color=gray,lw=.8);ax.axvspan(100,165,color=teal,alpha=.08);ax.set_title('A. Signed equivalent support — poles at the vertical-motion dead centres',loc='left',fontsize=12)
for x,y,label in [(100,1.022,'100°: 1.022 mg'),(180,.9271,'180°: 0.927 mg'),(240,.2624,'240°: 0.262 mg'),(260,-1.4309,'260°: −1.431 mg')]:
 ax.scatter(x,y,color=teal,s=22);ax.annotate(label,(x,y),xytext=(7,17) if x!=260 else (-10,-25),ha='left' if x!=260 else 'right',textcoords='offset points',fontsize=10)
ax.set_yticks([-100,-10,-1,0,1,10,100],labels=['−100','−10','−1','0','1','10','100'])
ax.text(92,75,'90°+: +∞',color=teal);ax.text(268,-75,'270°−: −∞',ha='right',color=teal)
ax.text(246.874,6,'Spring torque changes sign\nat 246.874°',ha='center',fontsize=10,color=pink);ax.axvline(246.874,color=pink,ls=':',lw=1)
axs[1].plot(t,ratio,color=teal,lw=2.3);axs[1].set(xlim=(100,165),ylim=(.97,1.03),ylabel=r'$F_{eq}/(mg)$',title='B. Working-range detail: 0.977968 to 1.022031 mg (approximately ±2.20%)');axs[1].axhline(1,color=gray,ls='--')
ax=axs[2];ax.plot(t,data['tauG'],color=gray,lw=2,label=r'$\tau_G$ load demand');ax.plot(t,data['tauS'],color=teal,lw=2,label=r'$\tau_S$ spring assistance');ax.plot(t,data['tau2'],color=red,lw=2,label=r'$\tau_2=\tau_G-\tau_S$ residual');ax.axhline(0,color=gray,lw=.8);ax.set(xlim=(90,270),ylabel='Torque (Nm)',title='C. Finite torques, even where equivalent vertical support is undefined');ax.legend(ncol=3,frameon=False,fontsize=10)
for ax in axs:
 ax.grid(alpha=.22);ax.set_xlabel(r'$\theta_2$ (degrees)')
fig.text(.10,.035,'Positive support balances an upward wheel load: the spring acts downward on the wheel. Above 246.874° it acts upward instead.\nEndpoints are undefined ratios, not infinite spring forces. Full-range peak tension ≈1.60 kN. No travel, strength or shock rating is assumed.',fontsize=10,color=gray)
for ext in ['png','svg']:fig.savefig(out/f'v3-full-range.{ext}',dpi=170,facecolor='white')
plt.close(fig)

fig,(leg,detail)=plt.subplots(1,2,figsize=(14,8),gridspec_kw={'width_ratios':[.85,1.3]})
fig.subplots_adjust(left=.04,right=.98,top=.83,bottom=.22,wspace=.13)
fig.suptitle('One hip horn + one tension spring',x=.04,ha='left',y=.96,fontsize=24,weight='bold')
fig.text(.04,.905,'Geometry shown at θ₂ = 135°, α = 0°; fixed spring mount S is above and behind the hip.',fontsize=12,color=gray)
A=np.array([0.,0.]);theta=np.deg2rad(135);B=-300*np.array([np.cos(theta),np.sin(theta)]);C=B-300*np.array([np.cos(np.pi-theta),np.sin(np.pi-theta)])
S=np.array([94.62059092890653,61.04113690737084]);r=63.02554487767227;eta=-34.047265733959684;phi=np.deg2rad(135+eta);D=r*np.array([np.cos(phi),np.sin(phi)])
def seg(ax,u,v,**kw):ax.plot([u[0],v[0]],[u[1],v[1]],**kw)
def coil(ax,u,v):
 d=v-u;n=np.array([-d[1],d[0]])/np.linalg.norm(d);points=[u]
 for i in range(17):points.append(u+d*(.12+.76*i/16)+n*(0 if i in [0,16] else (3 if i%2 else -3)))
 points.append(v);points=np.array(points);ax.plot(points[:,0],points[:,1],color=pink,lw=2)
seg(leg,A,B,color=blue,lw=12,solid_capstyle='round');seg(leg,B,C,color='#d48739',lw=12,solid_capstyle='round');leg.add_patch(Circle(C,80,facecolor='#eff3f6',edgecolor=gray,lw=2));seg(leg,A,D,color=pink,lw=5);coil(leg,D,S)
for point,label,offset in [(A,'A · hip',(-8,-18)),(B,'B · knee',(10,5)),(C,'C · wheel',(10,-5)),(S,'S fixed',(10,8))]:
 leg.plot(*point,'o',color='white',mec=navy,ms=6);leg.annotate(label,point,xytext=offset,textcoords='offset points',fontsize=11)
leg.text(130,-95,'Link 2\nfemur',color=blue);leg.text(170,-325,'Link 3\ntibia',color='#b56d29');leg.annotate('Front / travel (−y)',xy=(-125,-80),xytext=(80,-80),arrowprops={'arrowstyle':'->','color':gray},color=gray,ha='right')
leg.set(xlim=(-145,320),ylim=(-530,130),aspect='equal');leg.axis('off')
detail.set(xlim=(-70,160),ylim=(-38,117),aspect='equal');detail.axis('off')
seg(detail,A,D,color=pink,lw=9,solid_capstyle='round');coil(detail,D,S)
seg(detail,A,[S[0],0],color=gray,ls='--',lw=1);seg(detail,[S[0],0],S,color=gray,ls='--',lw=1)
detail.annotate('',xy=(0,-15),xytext=(S[0],-15),arrowprops={'arrowstyle':'<->','color':gray});detail.text(S[0]/2,-22,r'$S_y=94.621$ mm',ha='center',color=gray)
detail.annotate('',xy=(119,0),xytext=(119,S[1]),arrowprops={'arrowstyle':'<->','color':gray});detail.text(124,S[1]/2,r'$S_z=61.041$ mm',rotation=90,va='center',color=gray)
for point,label,offset in [(A,'A = (0, 0)',(-8,-4)),(D,'D · moving pin',(-2,13)),(S,'S · chassis pin',(0,13))]:
 detail.plot(*point,'o',color='white',mec=navy,ms=7);detail.annotate(label,point,xytext=offset,textcoords='offset points',ha='right' if point is A else 'center',fontsize=11)
detail.text(7,31,r'$r_h=63.026$ mm',rotation=79,ha='center',va='center',color=pink)
detail.text(42,75,r'$\ell(135°)=106.599$ mm',ha='center',color=pink)
reverse=55*np.array([np.cos(theta),np.sin(theta)]);seg(detail,A,reverse,color=blue,ls='--',lw=1.3);detail.text(-50,48,'B→A direction',ha='center',color=blue,fontsize=10)
detail.add_patch(Arc(A,54,54,theta1=135+eta,theta2=135,color=pink,lw=1.5));detail.text(-42,17,r'$\eta=-34.047°$',color=pink,fontsize=11)
detail.annotate('+y',xy=(33,0),xytext=(3,0),arrowprops={'arrowstyle':'->','color':gray},va='center',color=gray)
detail.annotate('+z',xy=(0,95),xytext=(0,80),arrowprops={'arrowstyle':'->','color':gray},ha='center',color=gray)
fig.text(.45,.225,r'Horn angle from +y: $\phi_h=\theta_2+\eta-\alpha$; angle from A→B is $\eta+180°=145.953°$.',fontsize=11)
fig.text(.04,.145,r'$\tau_2=\tau_G-\tau_S$,     $\tau_G=-2mgL\cos\alpha\cos\theta_2$,     $\tau_S=F_s\,d\ell/d\theta_2$  (SI units)',fontsize=16)
fig.text(.04,.09,'Spring law: F_s = k max(0, ℓ − ℓ₀ + p), with k = 13.247873 N/mm, ℓ₀ = 54.992217 mm, added preload p = 0 mm.\nInstalled at 100°: ℓ = 69.026 mm, extension = 14.034 mm, tension = 185.923 N. At 135°: extension = 51.606 mm, tension = 683.676 N.',fontsize=11,color=gray)
fig.text(.04,.026,'S_y and S_z locate S globally relative to A. Horn radius r_h and fixed offset η locate D relative to the femur.\nPositive τ₂ is residual load demand; applied CCW motor couple = −τ₂. Pin span ℓ₀ is an effective zero-force length; no built-in initial tension is assumed.',fontsize=10,color=gray)
for ext in ['png','svg']:fig.savefig(out/f'v3-hip-horn-geometry.{ext}',dpi=170,facecolor='white')
print('Saved full-range plots and labeled geometry.')
