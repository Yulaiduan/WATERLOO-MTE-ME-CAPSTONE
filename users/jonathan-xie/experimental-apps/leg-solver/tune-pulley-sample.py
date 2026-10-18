"""Fit the user's 13kg V4 idler sample and plot residuals independently.

Run python tune-pulley-sample.py. Inputs mm,N,kg,deg: k8,Sv100,rs0.1,
equal300mm links,qab2,alpha=nu=0,m13kg,Fz=mg,theta100..165.
Outputs compact fit evidence and PNG; SciPy/NumPy/Matplotlib required.
Minimax support-error fit within declared bounds, not a global mechanism proof.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import least_squares, minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out=Path(__file__).parent
K,H,R,M,G,L=8.,100.,.1,13.,9.81,300.
nominal=2*M*G*L/(K*H)
t=np.linspace(100,165,1301)
def calc(x,t=t,rs=R):
    su,rh,p0=x
    th=np.deg2rad(np.r_[90,t]);D=np.array([rh*np.cos(th),rh*np.sin(th)]).T
    v=D-[su,H];d=np.linalg.norm(v,axis=1)
    if np.min(d)<=rs:return None
    psi=np.unwrap(np.arctan2(v[:,1],v[:,0]))-np.arccos(rs/d)
    wrap=psi-np.pi/2+2*np.pi*np.ceil((np.pi/2-psi[0]-1e-12)/(2*np.pi))
    if min(wrap)<0 or max(wrap)>2*np.pi:return None
    Q=np.array([su+rs*np.cos(psi),H+rs*np.sin(psi)]).T
    tangent=np.sqrt(d*d-rs*rs);u=(Q-D)/tangent[:,None]
    payout=tangent+rs*wrap
    fs=np.maximum(0,p0+K*(payout-payout[0]))
    derivative=D[:,1]*u[:,0]-D[:,0]*u[:,1]
    tauS=-fs*derivative/1000
    tauG=2*M*G*L*np.cos(th)/1000
    motor=tauG-tauS
    pct=motor[1:]/np.abs(tauG[1:])*100
    return dict(motor=motor[1:],pct=pct,fs=fs[1:],support=1+pct/100,tauG=tauG[1:],tauS=tauS[1:])

initial=np.array([0,nominal,K*abs(H-nominal)])
fit=least_squares(lambda x:calc(x)['pct'],initial,bounds=([-5,85,0],[5,105,200]),xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=1000)
x0=np.r_[fit.x,max(abs(calc(fit.x)['pct']))]
def constraints(y):
    z=calc(y[:3]);v=z['pct'] if z else np.full(len(t),1e6)
    return np.r_[y[3]-v,y[3]+v]
mn=minimize(lambda y:y[3],x0,method='SLSQP',bounds=[(-5,5),(85,105),(0,200),(0,1)],constraints=[dict(type='ineq',fun=constraints)],options=dict(ftol=1e-13,maxiter=2000))
assert mn.success,mn.message
fitx=mn.x[:3]
cases=[('Product rule, p₀ = 0',[0,nominal,0],R),('Product + point-matching p₀',initial,R),('Finite-radius fit',fitx,R),('Point pulley, matched preload',initial,0)]
dense=np.linspace(100,165,65001)
data=[]
for label,x,rs in cases:
    z=calc(x,dense,rs)
    data.append(dict(label=label,Su_mm=float(x[0]),rh_mm=float(x[1]),p0_N=float(x[2]),rs_mm=rs,maxAbsMotor_Nm=float(max(abs(z['motor']))),maxAbsPercent=float(max(abs(z['pct']))),supportMin=float(min(z['support'])),supportMax=float(max(z['support'])),pe_N=float(z['fs'][0]),maxFs_N=float(max(z['fs']))))
summary=dict(assumptions=dict(k_N_per_mm=K,Sv_mm=H,rs_mm=R,m_kg=M,g=G,L_mm=L,alpha_deg=0,nu_deg=0,theta_deg=[100,165],movingMasses=0,load='Fz=mg,Fy=0'),fitBounds=dict(Su_mm=[-5,5],rh_mm=[85,105],p0_N=[0,200]),objective='minimax abs motor / abs gravity torque, sampled 1301; verified 65001',cases=data)
(out/'v4-tuning.json').write_text(json.dumps(summary,indent=2)+'\n')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(12.5,8),sharex=True)
colors=['#c64e46','#d68a18','#087f82','#65758a']
for i,(label,x,rs) in enumerate(cases):
    z=calc(x,dense,rs)
    axes[0,0].plot(dense,z['motor'],label=label,color=colors[i],ls='--' if i==3 else '-')
    axes[0,1].plot(dense,z['pct'],color=colors[i],ls='--' if i==3 else '-')
    if i in [1,2,3]:
        axes[1,0].plot(dense,z['motor'],color=colors[i],ls='--' if i==3 else '-')
        axes[1,1].plot(dense,z['pct'],color=colors[i],ls='--' if i==3 else '-')
for ax in axes.flat:ax.axhline(0,color='#9baab2',lw=.7);ax.grid(alpha=.2);ax.set_xlim(100,165)
axes[0,0].set_ylabel('Applied CCW motor τ₂ (Nm)');axes[0,1].set_ylabel('τ₂ / |τG| (%)')
axes[1,0].set_ylabel('Applied CCW motor τ₂ (Nm)');axes[1,1].set_ylabel('τ₂ / |τG| (%)')
axes[0,0].set_title('Preload mismatch dominates');axes[0,1].set_title('Signed residual as % of gravity requirement')
axes[1,0].set_title('Zoom: matched preload vs finite-radius fit');axes[1,1].set_title('Zoom: support error')
axes[1,0].set_xlabel('θ₂ (degrees)');axes[1,1].set_xlabel('θ₂ (degrees)')
fig.suptitle('13 kg · 300/300 mm · k = 8 N/mm · Sv = 100 mm · rs = 0.1 mm\nFinite idler is a small correction once preload is matched',fontsize=14)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=2,bbox_to_anchor=(.5,.005))
fig.tight_layout(rect=[0,.085,1,.92]);fig.savefig(out/'v4-tuning.png',dpi=160)
print(json.dumps(summary,indent=2))
