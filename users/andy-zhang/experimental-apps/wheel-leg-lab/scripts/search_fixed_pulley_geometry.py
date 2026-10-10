"""Search fixed-ratio near-linear leg strokes with a deterministic SciPy fit.

Run: python scripts/search_fixed_pulley_geometry.py from the app root.
Inputs: normalized lengths, radians, 12 degree left rays; seed 21 and explicit fit bounds.
Outputs: ignored artifacts/fixed-pulley-search/search-results.json and diagnostics.
Requires NumPy and SciPy; exploratory local fits are not global optima or collision checks.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import least_squares

OUTPUT=Path(__file__).resolve().parents[1]/"artifacts/fixed-pulley-search"
OUTPUT.mkdir(parents=True,exist_ok=True)
TILT=np.tan(np.deg2rad(12))
fractions=np.linspace(0,1,9)

def points(lam,k,t):
    return np.sin(t)-lam*np.sin(k*t),np.cos(t)+lam*np.cos(k*t)

def residual(v):
    lam,k,d0,d1,u0,u1=v
    scale=1+lam
    down=d0+(d1-d0)*fractions
    up=u0+(u1-u0)*fractions
    xd,yd=points(lam,k,down)
    xu,yu=points(lam,k,up)
    # Approximate the exact rays drawn by the user; no phase change or extra actuator.
    ray=np.concatenate([(xd+TILT*yd)/scale,(xu-TILT*yu)/scale])
    heights=np.array([yd[0]/scale-.55,yd[-1]/scale-.80,yu[0]/scale+.55,yu[-1]/scale+.80])*3
    sign=np.concatenate([np.minimum(yd/scale,0),np.maximum(yu/scale,0)])*3
    span=np.array([max(abs(d1-d0)-np.pi/2,0),max(abs(u1-u0)-np.pi/2,0)])
    return np.concatenate([ray,heights,sign,span])

rng=np.random.default_rng(21)
best=[]
for index in range(150):
    lam=rng.uniform(.5,2.5)
    k=rng.uniform(.3,2.5)
    d=rng.uniform(-np.pi,np.pi)
    u=d+rng.choice([-1,1])*np.pi
    v=[lam,k,d-.2,d+.2,np.clip(u-.2,-6,6),np.clip(u+.2,-6,6)]
    fit=least_squares(residual,v,bounds=([.3,.2,-6.2,-6.2,-6.2,-6.2],[3,3,6.2,6.2,6.2,6.2]),max_nfev=300,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    best.append((float(np.linalg.norm(fit.fun)),fit.x))
best.sort(key=lambda p:p[0])
answer=[]
for score,v in best[:8]:
    lam,k,d0,d1,u0,u1=v
    down=d0+(d1-d0)*fractions
    up=u0+(u1-u0)*fractions
    x,y=points(lam,k,np.concatenate([down,up]))
    theta=np.concatenate([down,up])
    xd=np.cos(theta)-lam*k*np.cos(k*theta)
    yd=-np.sin(theta)-lam*k*np.sin(k*theta)
    answer.append(dict(score=score,lower_over_upper=float(lam),hip_over_knee_pulley=float(k+1),down_angles=np.rad2deg([d0,d1]).tolist(),up_angles=np.rad2deg([u0,u1]).tolist(),max_ray_error_percent=float(100*np.max(np.abs(x+TILT*np.abs(y)))/(1+lam)),tangent_angles=np.rad2deg(np.arctan2(xd,yd)).tolist(),height_fractions=(y/(1+lam)).tolist()))
(OUTPUT/'search-results.json').write_text(json.dumps(answer,indent=2))
print(json.dumps(answer[:2],indent=2))
