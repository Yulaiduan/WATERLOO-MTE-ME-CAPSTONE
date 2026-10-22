"""Fit 10mm V4 pulley for the confirmed 13kg example. Run python tune-pulley-textbook.py.
Inputs mm/deg/N/Nm; NumPy/SciPy. Outputs compact provisional tuning data.
Numerical bounded fits, no exact-balance or global optimum proof.
"""
from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares,minimize
k,h,r,m,g,L=8.,100.,10.,13.,9.81,300.
t=np.linspace(100,165,1001)
def calc(x,t=t):
 su,rh,p0=x;th=np.deg2rad(np.r_[90,t]);D=np.array([rh*np.cos(th),rh*np.sin(th)]).T;v=D-[su,h];d=np.linalg.norm(v,axis=1)
 if min(d)<=r+.001:return None
 psi=np.unwrap(np.arctan2(v[:,1],v[:,0]))-np.arccos(r/d);wrap=psi-np.pi/2+2*np.pi*np.ceil((np.pi/2-psi[0]-1e-12)/(2*np.pi))
 if min(wrap)<0 or max(wrap)>2*np.pi:return None
 Q=np.array([su+r*np.cos(psi),h+r*np.sin(psi)]).T;span=np.sqrt(d*d-r*r);u=(Q-D)/span[:,None];c=span+r*wrap;fs=np.maximum(0,p0+k*(c-c[0]));cp=D[:,1]*u[:,0]-D[:,0]*u[:,1];G=2*m*g*L*np.cos(th)/1000;motor=G+fs*cp/1000;pct=motor[1:]/abs(G[1:])*100
 return dict(pct=pct,motor=motor[1:],Fs=fs[1:],d90=d[0],wrap=wrap[1:])
best=None
for start in [[5,85,180],[0,80,200],[10,90,160],[20,95,200],[-20,80,200],[30,120,300],[0,120,200]]:
 def fun(x):
  z=calc(x)
  return z['pct'] if z else np.full(len(t),1e4+np.linalg.norm(x))
 ls=least_squares(fun,start,bounds=([-60,20,0],[60,180,3000]),max_nfev=1000,ftol=1e-12,xtol=1e-12,gtol=1e-12)
 if calc(ls.x) is None:continue
 if best is None or max(abs(calc(ls.x)['pct']))<best[0]:best=(max(abs(calc(ls.x)['pct'])),ls.x)
 print('start',start,'result',ls.x,'error',max(abs(calc(ls.x)['pct'])))
def con(y):
 z=calc(y[:3]);v=z['pct'] if z else np.full(len(t),1e6)
 return np.r_[y[3]-v,y[3]+v]
mn=minimize(lambda y:y[3],np.r_[best[1],best[0]],bounds=[(-60,60),(20,180),(0,3000),(0,100)],constraints=[dict(type='ineq',fun=con)],method='SLSQP',options=dict(ftol=1e-12,maxiter=1500))
assert mn.success,mn.message
z=calc(mn.x[:3],np.linspace(100,165,65001));result=dict(Su_mm=mn.x[0],rh_mm=mn.x[1],p0_N=mn.x[2],maxPercent=max(abs(z['pct'])),maxMotor_Nm=max(abs(z['motor'])),pe_N=z['Fs'][0],maxFs_N=max(z['Fs']),d90_mm=z['d90'])
print(json.dumps(result,indent=2));(Path(__file__).parent/'v4-textbook-verification.json').write_text(json.dumps(result,indent=2)+'\n')

# Plot the actual matched torques and separate motor/compensation signals.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
tt=np.linspace(100,165,65001);zz=calc(mn.x[:3],tt)
gravity=2*m*g*L*np.cos(np.deg2rad(tt))/1000
spring=gravity-zz['motor']
fig,axes=plt.subplots(2,2,figsize=(11.5,7.6),sharex=True)
axes[0,0].plot(tt,gravity,label='τG: no-spring motor',color='#8595a4')
axes[0,0].plot(tt,spring,label='τS: spring couple',color='#087f82',ls='--')
axes[0,0].set_ylabel('Signed torque (Nm)');axes[0,0].legend(fontsize=9)
axes[0,0].set_title('Spring tracks the gravity requirement')
axes[0,1].plot(tt,zz['motor'],color='#d34155');axes[0,1].set_ylabel('Applied CCW motor τ₂ (Nm)')
axes[0,1].set_title('Remaining actuator torque · linear scale')
axes[1,0].plot(tt,zz['pct'],color='#087f82');axes[1,0].set_ylabel('Compensation error (%)')
axes[1,0].set_title('100 × [effective support / mg − 1] · zoomed')
axes[1,1].plot(tt,zz['Fs'],color='#bd408d');axes[1,1].set_ylabel('Spring force (N)')
axes[1,1].set_title('Spring force and extension-stop preload')
for ax in axes.flat:ax.grid(alpha=.2);ax.set_xlim(100,165);ax.spines[['top','right']].set_visible(False)
for ax in [axes[0,1],axes[1,0]]:ax.axhline(0,color='#a8b6bf',lw=.8)
for ax in axes[1]:ax.set_xlabel('θ₂ (degrees)')
fig.suptitle('V4 textbook: 13 kg · 300/300 mm · rs = 10 mm · k = 8 N/mm · Sv = 100 mm',fontsize=13)
fig.text(.5,.015,f'Su = {mn.x[0]:.6f} mm   rh = {mn.x[1]:.6f} mm   p₀ = {mn.x[2]:.6f} N   |   max compensation error ≈ 0.0621%',ha='center',fontsize=10)
fig.tight_layout(rect=[0,.05,1,.95]);fig.savefig(Path(__file__).parent/'v4-textbook-10mm.png',dpi=160)
