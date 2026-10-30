"""Exact finite-link mass terms for the experimental straight VSL contact model.

Import mass_terms(model,q) with q radians, geometry metres, masses kg and inertia
kg m². Returns the [hip height, wheel-guide distance, free wheel spin] matrix,
its analytic distance derivatives and inverse. Uniform rods, massless compound
idler, fixed chassis pitch and ideal 2:1 straight-travel belt only; no hardware
or full-vehicle claim. No integration or external engine is used here.
"""
def mass_terms(m,q):
    p=m.p;sites=m.sites(q);j=m.jacobian(q);jp=-m.distance(q)
    A=p['m1']+p['m2']+p['m3']+p['m6']
    B=Bp=Cp=0.;C=m.I['2']+m.I['3']*m.k3*m.k3+m.Jref
    for key in ('2','3','6'):
        mass=p['m'+key];_,v,a=sites[key]
        B+=mass*v[1];Bp+=mass*a[1]
        C+=mass*(v[0]*v[0]+v[1]*v[1]);Cp+=2*mass*(v[0]*a[0]+v[1]*a[1])
    H=B/j;D=C/(j*j);det=A*D-H*H
    if det<=0:raise ValueError('Finite contact mass matrix is not positive definite.')
    return dict(A=A,B=B,C=C,H=H,D=D,Bprime=Bp,Cprime=Cp,
        Hprime=(Bp*j-B*jp)/j**3,Dprime=(Cp*j-2*C*jp)/j**4,
        inverse=((D/det,-H/det,0.),(-H/det,A/det,0.),(0.,0.,1/m.I['6'])))


def kinetic(m,q,v):
    a=m.mass_terms(q);vh,vd,w=v
    return .5*(a['A']*vh*vh+2*a['H']*vh*vd+a['D']*vd*vd+m.I['6']*w*w)


def gravity(m,q,h):
    return m.p['g']*(m.p['m1']*h+sum(m.p['m'+k]*(h+m.sites(q)[k][0][1]) for k in ('2','3','6')))
