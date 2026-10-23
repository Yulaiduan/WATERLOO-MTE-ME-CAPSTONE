"""Independent reduced-coordinate rigid circle/rectangle contact integrator.

Run Python analytical_contact.py --request-stdin; input builder mm/deg/kg/N and
runConfig SI/s, contactConfig and optional caseConfig JSON. Output contact-v2
rows and world-mm frames. No Pymunk dependency. Massless straight linkage,
vertical chassis, uniform disc and rigid Coulomb contact only; no tire model.
"""
import argparse
import json
import math
import sys
from contact_cases import (validate_contact_request, resolve_case, initial_conditions,
    terrain_spec, CaseController, energy_fields, case_metrics, model_identity,
    stopping_demand, world, energy_estimate)
from dynamic_model import R, mul

# Contact complementarity: https://underactuated.csail.mit.edu/multibody.html
# Accumulated PGS: https://box2d.org/posts/2024/02/solver2d/


def simulate_contact(payload, *, stop_at_assessment=False):
    m=validate_contact_request(payload);p,c=m.p,m.c;cc=payload['contactConfig'];case=resolve_case(payload)
    ctl=CaseController(m,case);terrain=terrain_spec(m,case);boxes=terrain['boxes'];speed=terrain['speed']
    ax,az=m.axis;r=p['rw']/1000;mw=p['m6'];mt=p['m1']+mw;I=m.I['6']
    det=mt*mw-(mw*az)**2
    inv=((mw/det,-mw*az/det,0),(-mw*az/det,mt/det,0),(0,0,1/I))
    def product(a,b):return sum(x*y for x,y in zip(a,b))
    def inverse(v):return [product(row,v) for row in inv]
    def kinetic(v):return .5*(mt*v[0]**2+2*mw*az*v[0]*v[1]+mw*v[1]**2+I*v[2]**2)
    q,h,x,z=initial_conditions(m,case);u=[h,m.distance(q),(m.K*(q/R-p['te'])-p['alpha'])*R]
    qd=c['initialVelocityDegS']*R if case['kind']=='terrain-stability' else 0.
    v=[-az*m.jacobian(q)*qd,m.jacobian(q)*qd,0.]
    sl,sh=sorted((m.distance(m.lo),m.distance(m.hi)))
    t=0.;steps=0;rows=[];frames=[];events=[];next_sample=1/c['outputHz'];sample_t=0.
    sumJ=[0.,0.];sumN=sumT=0.;points=[];slips=[];work=stoploss=stabilization=dampingwork=terrainwork=contactloss=0.;maxpen=0.;contacted=False;previous_contact=False
    termination='duration';first_raised=None;maxnf=0.;maxtf=0.;tor=ctl.torques(q,qd)
    penetration_limit_mm=1.;prepen=postpen=maxpre=maxpost=0.;max_stop_position_error=0.
    def geometry(time):
        x=ax*u[1];z=u[0]+az*u[1];out=[]
        out.append((z-r,(0.,1.),(x,0.)))
        for b in boxes:
            left,right=b[0][0]+speed*time,b[1][0]+speed*time;top=b[2][1]
            cx=max(left,min(right,x));cz=max(0,min(top,z));dx=x-cx;dz=z-cz;d=math.hypot(dx,dz)
            if d>1e-14:n=(dx/d,dz/d);gap=d-r
            else:
                ds=[(x-left,(-1.,0.)),(right-x,(1.,0.)),(z,(0.,-1.)),(top-z,(0.,1.))]
                distance,n=min(ds,key=lambda a:a[0]);gap=-distance-r;cx=x-n[0]*distance;cz=z-n[1]*distance
            out.append((gap,n,(cx,cz)))
        return out
    def jac(n,spin=False):return (n[1],ax*n[0]+az*n[1],r if spin else 0.)
    def append():
        nonlocal sample_t,sumN,sumT,maxnf,maxtf
        q=m.inverse(u[1]);qd=v[1]/m.jacobian(q);spring=m.spring(q);e=energy_fields(m,q,u[0],v[0],v[1],v[2]);ke=e['chassisKineticJ']+e['wheelKineticJ'];pe=e['springEnergyJ']+e['gravityEnergyJ']
        gap=min(g[0] for g in geometry(t))*1000;elapsed=t-sample_t;nf=sumN/elapsed if elapsed else 0.;tf=sumT/elapsed if elapsed else 0.;maxnf=max(maxnf,nf);maxtf=max(maxtf,tf)
        A=world((0,u[0]));C=world((ax*u[1],u[0]+az*u[1]));translate=lambda a:world((a[0],a[1]+u[0]))
        theta6=u[2]/R+p['alpha'];theta4=m.dc*m.fe*(theta6-m.K*(q/R-p['te']));theta5=(1-1/m.dc)*(q/R-p['te'])+theta4/m.dc
        slip=max(slips,key=abs) if slips else None
        frame=dict(t=t,theta2=q/R,A=A,B=translate(m.sites(q)['5'][0]),C=C,actualA=A,actualC=C,chassisZMm=A[2],wheelZMm=C[2],wheelAngle=u[2]/R,theta4=theta4,theta5=theta5,theta6=theta6,
            bodyPositionsMm={'1':A,'6':C},bodyAnglesDeg={'1':0.,'6':u[2]/R},indexAnglesDeg={'a':0,'b':p['phi0']+(180-q/R)*(m.ab-1),'c':theta4,'d':theta5,'e':theta5,'f':theta6},terrainOffsetMm=world((speed*t,0)),terrainPolygonsMm=[[world((a+speed*t,b)) for a,b in box] for box in boxes],contactPointsMm=list(points),contactNormalForceN=nf,contactTangentialForceN=tf,slipMmS=slip,gapMm=gap,penetrationMm=max(0,-gap),guideResidualMm=0.,constraintPositionErrorMm=0.,constraintAngleErrorDeg=0.)
        if p['springEnabled']:frame.update(D=translate(mul(m.rotate(spring['D']),.001)),Q=translate(mul(m.rotate(spring['Q']),.001)))
        row=dict(t=t,theta2=q/R,velocityDegS=qd/R,accelerationDegS2=None,Fs=spring['force'],tauStatic=None,tauApplied=tor['motorTorqueNm']-c['dampingNms']*qd,kineticJ=ke,potentialJ=pe,energyJ=ke+pe,CxMm=C[0],CzMm=C[2],chassisZMm=A[2],chassisVelocityMmS=v[0]*1000,chassisAccelerationMmS2=None,wheelZMm=C[2],wheelVelocityXMmS=-ax*v[1]*1000,wheelVelocityZMmS=(v[0]+az*v[1])*1000,wheelAngle=u[2]/R,wheelAngularVelocityDegS=v[2]/R,theta4=theta4,theta5=theta5,theta6=theta6,requestedInputMm=None,appliedInputMm=None,inputVelocityMmS=None,inputAccelerationMmS2=None,inputReactionN=None,contactNormalForceN=nf,contactTangentialForceN=tf,contactForceXN=-sumJ[0]/elapsed if elapsed else 0.,contactForceZN=sumJ[1]/elapsed if elapsed else 0.,contactNormalImpulseNs=sumN,contactTangentialImpulseNs=sumT,contactCount=len(points),slipMmS=slip,gapMm=gap,penetrationMm=max(0,-gap),guideResidualMm=0.,guideForceN=(spring['torque']+tor['motorTorqueNm']-c['dampingNms']*qd)/m.jacobian(q),actuatorDampingWorkJ=work+dampingwork,motorWorkJ=work,dampingWorkJ=dampingwork,contactDissipationJ=contactloss,stopDissipationJ=stoploss,positionStabilizationJ=stabilization,terrainWorkJ=terrainwork,inputWorkJ=terrainwork,stoppingDemandTorqueNm=stopping_demand(m,q,qd,v[0],case),**e,**tor)
        ground_under_hip=max([0.]+[box[2][1] for box in boxes if box[0][0]+speed*t<=0<=box[1][0]+speed*t])
        clearance=(u[0]-ground_under_hip)*1000-case['undersideOffsetMm'] if case['undersideOffsetMm'] is not None else None
        phase='end-stop' if min(abs(u[1]-sl),abs(u[1]-sh))<1e-8 and abs(v[1])<1e-7 else 'contact' if previous_contact else 'free-flight'
        row.update(demandTorqueNm=row['stoppingDemandTorqueNm'],chassisClearanceMm=clearance,motionPhase=phase,
            preProjectionPenetrationMm=prepen,postProjectionPenetrationMm=postpen,
            energyBalanceResidualJ=ke+pe-(rows[0]['energyJ'] if rows else ke+pe)-work-dampingwork-terrainwork+stoploss+contactloss-stabilization)
        frame.update(chassisClearanceMm=clearance,motionPhase=phase,controllerPhase=tor['controllerPhase'])
        rows.append(row);frames.append(frame);sample_t=t;sumJ[:]=[0.,0.];sumN=sumT=0.;points.clear();slips.clear()
    append()
    if rows[0]['penetrationMm']>1e-7:
        raise ValueError('Initial wheel overlaps terrain; adjust initial pose/terrain delay.')
    if rows[0]['chassisClearanceMm'] is not None and rows[0]['chassisClearanceMm']<=0:
        raise ValueError('Initial chassis underside clearance is nonpositive; reduce the underside offset or change the initial case pose/drop.')
    while t<c['duration']-1e-12:
        q=m.inverse(u[1]);qd=v[1]/m.jacobian(q);tor=ctl.torques(q,qd,contacted);dt=min(c['dt'],c['duration']-t,next_sample-t)
        f=(m.spring(q)['torque']+tor['motorTorqueNm']-c['dampingNms']*qd)/m.jacobian(q);fx,fz=m.force
        acc=inverse((-mt*p['g']+fz,f-mw*p['g']*az+ax*fx+az*fz,m.Mw))
        # Split the drift exactly at the first guide endpoint under this step's
        # frozen force, so extension work ends at the actual angle, not a sample.
        predicted=u[1]+v[1]*dt+.5*acc[1]*dt*dt
        if predicted<sl or predicted>sh:
            endpoint=sl if predicted<sl else sh
            if abs(u[1]-endpoint)>1e-10:
                roots=[]
                if abs(acc[1])<1e-14:
                    if abs(v[1])>1e-14:roots=[(endpoint-u[1])/v[1]]
                else:
                    discriminant=v[1]*v[1]-2*acc[1]*(u[1]-endpoint)
                    if discriminant>=0:roots=[(-v[1]+sign*math.sqrt(discriminant))/acc[1] for sign in (-1,1)]
                positive=[root for root in roots if 1e-10<root<=dt]
                if positive:dt=min(positive)
        beforeq=q;beforevh=v[0]
        # Exact constant-force drift/kick; contacts use the physical velocity only.
        for k in range(3):u[k]+=v[k]*dt+.5*acc[k]*dt*dt;v[k]+=acc[k]*dt
        t+=dt;steps+=1
        # Unilateral guide-end impulse conserves chassis/wheel vertical momentum.
        if u[1]<=sl+1e-12 and v[1]<0 or u[1]>=sh-1e-12 and v[1]>0:
            endpoint=sl if u[1]<=sl+1e-12 else sh;atq=m.lo if abs(endpoint-m.distance(m.lo))<1e-12 else m.hi
            u[1]=endpoint
            if (endpoint==sl and v[1]<0) or (endpoint==sh and v[1]>0):
                before=kinetic(v);momentum_before=mt*v[0]+mw*az*v[1];j=-v[1]/inv[1][1];dv=inverse((0,j,0));v[:]=[a+b for a,b in zip(v,dv)];stoploss+=max(0,before-kinetic(v))
                typ='compression-stop' if atq==m.hi else 'extension-stop'
                if not any(e['type']==typ for e in events):events.append(dict(t=t,type=typ,verticalMomentumBeforeKgMS=momentum_before,verticalMomentumAfterKgMS=mt*v[0]+mw*az*v[1],dissipatedEnergyJ=max(0,before-kinetic(v))))
                if atq==m.lo:ctl.extended=True
        dampingwork-=c['dampingNms']*qd*qd*dt
        contacts=[]
        for gap,n,pt in geometry(t):
            jn=jac(n);normal_speed=product(jn,v)-n[0]*speed
            if (gap<=1e-8 or gap+normal_speed*dt<=0) and product(jn,inverse(jn))>1e-14:
                tangent=(n[1],-n[0]);jt=jac(tangent,True)
                contacts.append([gap,n,pt,jn,jt,0.,0.])
        contact_ke_before=kinetic(v);step_terrain_work=0.;stop_loss_before=stoploss
        stop_constraints=[]
        if u[1]<=sl+1e-9:stop_constraints.append([(0.,1.,0.),0.])
        if u[1]>=sh-1e-9:stop_constraints.append([(0.,-1.,0.),0.])
        for _ in range(max(10,int(c['iterations']))):
            for con in contacts:
                gap,n,pt,jn,jt,ln,lt=con;wn=product(jn,inverse(jn));target=max(0,gap/dt)
                new=max(0,ln-(product(jn,v)-n[0]*speed+target)/wn);dv=inverse([a*(new-ln) for a in jn]);v[:]=[a+b for a,b in zip(v,dv)];con[5]=new
                wt=product(jt,inverse(jt));trial=lt-(product(jt,v)-n[1]*speed)/wt;limit=cc['friction']*new;newt=max(-limit,min(limit,trial));dv=inverse([a*(newt-lt) for a in jt]);v[:]=[a+b for a,b in zip(v,dv)];con[6]=newt
            # End stops and terrain are one coupled velocity solve. A floor
            # impulse can otherwise reopen a previously resolved stop velocity.
            for con in stop_constraints:
                js,old=con;ws=product(js,inverse(js));new=max(0.,old-product(js,v)/ws)
                before=kinetic(v);dv=inverse([a*(new-old) for a in js]);v[:]=[a+b for a,b in zip(v,dv)]
                stoploss+=before-kinetic(v);con[1]=new
        active=False
        for gap,n,pt,jn,jt,ln,lt in contacts:
            if ln>1e-12:
                active=True;step_terrain_work+=speed*(n[0]*ln+n[1]*lt);sumN+=ln;sumT+=abs(lt);sumJ[0]+=n[0]*ln+n[1]*lt;sumJ[1]+=n[1]*ln-n[0]*lt;points.append(world(pt));slips.append((product(jt,v)-n[1]*speed)*1000)
                if first_raised is None and pt[1]>1e-7:first_raised=t;events.append(dict(t=t,type='first-raised-terrain-contact'))
        terrainwork+=step_terrain_work;contactloss+=contact_ke_before+step_terrain_work-kinetic(v)-(stoploss-stop_loss_before)
        if active and not contacted:contacted=True;events.append(dict(t=t,type='first-contact',chassisVelocityMmS=beforevh*1000))
        if previous_contact and not active and case['kind']=='jump' and not any(e['type']=='takeoff' for e in events):events.append(dict(t=t,type='takeoff'))
        previous_contact=active
        if case['kind']=='jump' and beforevh>0>=v[0] and any(e['type']=='takeoff' for e in events) and not any(e['type']=='apex' for e in events):events.append(dict(t=t,type='apex',chassisZMm=u[0]*1000))
        if contacted and beforevh<0<=v[0] and not any(e['type']=='chassis-arrest' for e in events):events.append(dict(t=t,type='chassis-arrest'))
        # Separate mass-weighted position projection; never changes velocity/KE.
        def potential():
            qq=m.inverse(max(sl,min(sh,u[1])));return m.spring(qq)['energy']+p['g']*(mt*u[0]+mw*az*u[1])
        potential_before=potential()
        prepen=max(0.,-min(g[0] for g in geometry(t)))*1000;maxpre=max(maxpre,prepen)
        if prepen>penetration_limit_mm:
            maxpen=max(maxpen,prepen);postpen=prepen;maxpost=max(maxpost,postpen);termination='contact-penetration-limit'
            events.append(dict(t=t,type=termination,penetrationMm=prepen,limitMm=penetration_limit_mm,stage='before-position-projection'))
            work+=tor['motorTorqueNm']*(m.inverse(u[1])-beforeq);append();break
        for _ in range(max(10,int(c['iterations']))):
            for gap,n,pt in geometry(t):
                maxpen=max(maxpen,max(0,-gap)*1000)
                if gap<0:
                    jn=jac(n);du=inverse(jn);denom=product(jn,du)
                    if denom>1e-14:
                        scale=-gap/denom;u[0]+=du[0]*scale;u[1]+=du[1]*scale
            if u[1]<sl or u[1]>sh:
                endpoint=sl if u[1]<sl else sh;correction=(endpoint-u[1])/inv[1][1]
                u[0]+=inv[0][1]*correction;u[1]=endpoint
            if min(g[0] for g in geometry(t))>=-1e-10:break
        postpen=max(0.,-min(g[0] for g in geometry(t)))*1000;maxpost=max(maxpost,postpen);maxpen=max(maxpen,prepen,postpen)
        max_stop_position_error=max(max_stop_position_error,max(0,sl-u[1],u[1]-sh)*1000)
        q=m.inverse(u[1]);stabilization+=potential()-potential_before
        work_q=m.lo if case['kind']=='jump' and ctl.extended and tor['motorTorqueNm']!=0 else q
        work+=tor['motorTorqueNm']*(work_q-beforeq)
        if postpen>penetration_limit_mm:
            termination='contact-penetration-limit';events.append(dict(t=t,type=termination,penetrationMm=postpen,limitMm=penetration_limit_mm,stage='after-coupled-position-projection'));append();break
        ground_under_hip=max([0.]+[box[2][1] for box in boxes if box[0][0]+speed*t<=0<=box[1][0]+speed*t])
        if case['undersideOffsetMm'] is not None and (u[0]-ground_under_hip)*1000<=case['undersideOffsetMm']:
            events.append(dict(t=t,type='underside-contact'));termination='underside-contact';append();break
        if not all(math.isfinite(a) for a in u+v):raise ValueError('Analytical contact diverged.')
        if stop_at_assessment and case['kind']=='landing' and any(e['type'] in ('chassis-arrest','compression-stop') for e in events):
            termination='assessment-outcome';append();break
        if t>=next_sample-1e-10 or t>=c['duration']-1e-10:append();next_sample+=1/c['outputHz']
    snapshot=dict(params=p,solverConfig=c,contactConfig=cc)
    if 'caseConfig' in payload:snapshot['caseConfig']=case
    result=dict(schema='kinefold/contact-v2',engine='analytical',params=p,runConfig=c,contactConfig=cc,caseConfig=case,snapshot=snapshot,designHash=model_identity(m,cc,case),rows=rows,frames=frames,events=events,caseMetrics=case_metrics(rows,events,m,case),terrain=terrain['terrain'],diagnostics=dict(termination=termination,elapsedSeconds=t,steps=steps,dt=c['dt'],iterations=c['iterations'],integrator='Independent reduced-mass constant-force drift with accumulated unilateral Coulomb PGS impulses',rigidBodies=2,chassisBodyMassKg=p['m1'],wheelBodyMassKg=mw,wheelMomentKgM2=I,chassisPitchLocked=True,wheelSpinFree=True,maxPenetrationMm=maxpen,maxGuideResidualMm=0.,maxConstraintPositionErrorMm=0.,maxConstraintAngleErrorDeg=0.,maxContactNormalForceN=maxnf,maxContactTangentialForceN=maxtf,firstRaisedContactTimeS=first_raised,effectiveFriction=cc['friction'],restitution=0,positionStabilization='Separate mass-weighted projection; no velocity/kinetic correction',stopDissipationJ=stoploss,resolvedInertiasKgM2=m.I,builderMassesKg={k:p['m'+k] for k in ('1','2','3','5','6')},modelRevision='straight-guide-contact-v2'),scope=dict(mode='terrain-contact',quarterModel=True,fixture='floating-chassis',coordinates='+x left / +z up / mm'),warnings=['Experimental rigid two-body quarter model; no tire, rigid chassis collision shape or hardware validation; entered underside point-clearance stops are assessed.','Position projection is separate from physical contact velocity and kinetic energy.','Sharp contact impulse peaks and travel-stop events require timestep refinement.'])

    result['energyEstimate']=energy_estimate(m,case) if case['energyMethod'] else None
    result['diagnostics'].update(energyBalanceResidualJ=rows[-1]['energyBalanceResidualJ'],maxPreProjectionPenetrationMm=maxpre,maxPostProjectionPenetrationMm=maxpost,penetrationTerminationLimitMm=penetration_limit_mm,maxTravelStopDriftMm=max_stop_position_error)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--request-stdin',action='store_true',required=True);parser.parse_args()
    try:print(json.dumps(simulate_contact(json.load(sys.stdin)),allow_nan=False))
    except (ValueError,KeyError,TypeError,ArithmeticError) as error:print(json.dumps(dict(error=str(error))));sys.exit(1)
