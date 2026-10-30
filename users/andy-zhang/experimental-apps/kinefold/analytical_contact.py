"""Independent reduced-coordinate rigid circle/rectangle contact integrator.

Run Python analytical_contact.py --request-stdin; input builder mm/deg/kg/N and
runConfig SI/s, contactConfig and optional caseConfig JSON. Output contact-v2
rows and world-mm frames. No Pymunk dependency. Straight ideal linkage with
massless bars or two finite uniform rods, vertical chassis, free uniform disc
and rigid Coulomb contact only; no tire or whole-vehicle model.
"""
import argparse
import json
import math
import sys
from contact_cases import (validate_contact_request, resolve_case, initial_conditions,
    terrain_spec, CaseController, energy_fields, case_metrics, model_identity,
    stopping_demand, world, energy_estimate, annotate_contact_work)
from torque_targets import TargetObservation
from contact_cases import check_motor_step
from dynamic_model import R, mul
from terrain_profiles import circle_contacts, surface_height, raised_contact
from contact_cases import initial_motion,COMObservation
from finite_contact_model import kinetic as finite_kinetic, gravity as finite_gravity

# Contact complementarity: https://underactuated.csail.mit.edu/multibody.html
# Accumulated PGS: https://box2d.org/posts/2024/02/solver2d/


def simulate_contact(payload, *, stop_at_assessment=False):
    m=validate_contact_request(payload);p,c=m.p,m.c;cc=payload['contactConfig'];case=resolve_case(payload)
    observation=TargetObservation(case,c['dt'])
    com_observation=COMObservation()
    ctl=CaseController(m,case);terrain=terrain_spec(m,case);boxes=terrain['boxes'];speed=terrain['speed']
    ax,az=m.axis;r=p['rw']/1000;mw=p['m6'];mt=p['m1']+mw;I=m.I['6']
    def product(a,b):return sum(x*y for x,y in zip(a,b))
    def mass_at(q):
        if m.finite_links:return m.mass_terms(q)['inverse']
        ms=mw+m.Jref/m.jacobian(q)**2;det=mt*ms-(mw*az)**2
        return ((ms/det,-mw*az/det,0),(-mw*az/det,mt/det,0),(0,0,1/I))
    inv=mass_at(m.q0)
    def inverse(v):return [product(row,v) for row in inv]
    def kinetic(v):
        q=m.inverse(u[1]);ms=mw+m.Jref/m.jacobian(q)**2
        if m.finite_links:return finite_kinetic(m,q,v)
        return .5*(mt*v[0]**2+2*mw*az*v[0]*v[1]+ms*v[1]**2+I*v[2]**2)
    q,h,x,z=initial_conditions(m,case);u=[h,m.distance(q),(m.K*(q/R-p['te'])-p['alpha'])*R]
    qd=c['initialVelocityDegS']*R if case['kind']=='terrain-stability' else 0.
    motion=initial_motion(m,case,q)
    v=[motion['chassisVelocity'],motion['guideVelocity'],0.] if m.terrain_config and m.terrain_config['schema']=='kinefold/terrain-v2' and case['kind']=='terrain-stability' else [-az*m.jacobian(q)*qd,m.jacobian(q)*qd,0.]
    sl,sh=sorted((m.distance(m.lo),m.distance(m.hi)))
    t=0.;steps=0;rows=[];frames=[];events=[];next_sample=1/c['outputHz'];sample_t=0.
    sumJ=[0.,0.];sumN=sumT=0.;points=[];slips=[];work=stoploss=stabilization=dampingwork=terrainwork=contactloss=motorloss=externalwork=0.;maxpen=0.;contacted=False;previous_contact=False
    termination='duration';first_raised=None;maxnf=0.;maxtf=0.;tor=ctl.torques(q,qd,time=0.,state=dict(h=h,vh=v[0],contacted=False))
    penetration_limit_mm=1.;prepen=postpen=maxpre=maxpost=0.;max_stop_position_error=0.
    def geometry(time):
        x=ax*u[1];z=u[0]+az*u[1];out=[]
        if 'segments' in terrain:return circle_contacts(terrain,time,x,z,r)
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
        q=m.inverse(u[1]);qd=v[1]/m.jacobian(q);spring=m.spring(q);e=energy_fields(m,q,u[0],v[0],v[1],v[2]);ke=e['chassisKineticJ']+e['wheelKineticJ']+e['rotorKineticJ']+e['legacyJointRotorKineticJ']+e['linkKineticJ'];pe=e['springEnergyJ']+e['gravityEnergyJ']+e['coggingPotentialJ']
        gap=min(g[0] for g in geometry(t))*1000;elapsed=t-sample_t;nf=sumN/elapsed if elapsed else 0.;tf=sumT/elapsed if elapsed else 0.;maxnf=max(maxnf,nf);maxtf=max(maxtf,tf)
        A=world((0,u[0]));C=world((ax*u[1],u[0]+az*u[1]));translate=lambda a:world((a[0],a[1]+u[0]))
        theta6=u[2]/R+p['alpha'];theta4=m.dc*m.fe*(theta6-m.K*(q/R-p['te']));theta5=(1-1/m.dc)*(q/R-p['te'])+theta4/m.dc
        slip=max(slips,key=abs) if slips else None
        frame=dict(t=t,theta2=q/R,A=A,B=translate(m.sites(q)['5'][0]),C=C,actualA=A,actualC=C,chassisZMm=A[2],wheelZMm=C[2],wheelAngle=u[2]/R,theta4=theta4,theta5=theta5,theta6=theta6,
            bodyPositionsMm={'1':A,'6':C},bodyAnglesDeg={'1':0.,'6':u[2]/R},indexAnglesDeg={'a':0,'b':p['phi0']+(180-q/R)*(m.ab-1),'c':theta4,'d':theta5,'e':theta5,'f':theta6},terrainOffsetMm=world((speed*t,0)),terrainPolygonsMm=[[world((a+speed*t,b)) for a,b in box] for box in boxes],contactPointsMm=list(points),contactNormalForceN=nf,contactTangentialForceN=tf,slipMmS=slip,gapMm=gap,penetrationMm=max(0,-gap),guideResidualMm=0.,constraintPositionErrorMm=0.,constraintAngleErrorDeg=0.)
        if p['springEnabled']:frame.update(D=translate(mul(m.rotate(spring['D']),.001)),Q=translate(mul(m.rotate(spring['Q']),.001)))
        row=dict(t=t,theta2=q/R,velocityDegS=qd/R,accelerationDegS2=None,Fs=spring['force'],tauStatic=None,tauApplied=tor['motorTorqueNm']+tor['jointFrictionNm']-c['dampingNms']*qd,kineticJ=ke,potentialJ=pe,energyJ=ke+pe,CxMm=C[0],CzMm=C[2],chassisZMm=A[2],chassisVelocityMmS=v[0]*1000,chassisAccelerationMmS2=None,wheelZMm=C[2],wheelVelocityXMmS=-ax*v[1]*1000,wheelVelocityZMmS=(v[0]+az*v[1])*1000,wheelAngle=u[2]/R,wheelAngularVelocityDegS=v[2]/R,theta4=theta4,theta5=theta5,theta6=theta6,requestedInputMm=None,appliedInputMm=None,inputVelocityMmS=None,inputAccelerationMmS2=None,inputReactionN=None,contactNormalForceN=nf,contactTangentialForceN=tf,contactForceXN=-sumJ[0]/elapsed if elapsed else 0.,contactForceZN=sumJ[1]/elapsed if elapsed else 0.,contactNormalImpulseNs=sumN,contactTangentialImpulseNs=sumT,contactCount=len(points),slipMmS=slip,gapMm=gap,penetrationMm=max(0,-gap),guideResidualMm=0.,guideForceN=(spring['torque']+tor['motorTorqueNm']+tor['jointPassiveNm']-c['dampingNms']*qd)/m.jacobian(q),actuatorDampingWorkJ=work+dampingwork,motorWorkJ=work,dampingWorkJ=dampingwork,motorDissipatedJ=motorloss,motorDissipationJ=motorloss,motorFrictionLossJ=motorloss,contactDissipationJ=contactloss,stopDissipationJ=stoploss,positionStabilizationJ=stabilization,terrainWorkJ=terrainwork,inputWorkJ=terrainwork,externalWorkJ=externalwork,stoppingDemandTorqueNm=stopping_demand(m,q,qd,v[0],case),**e,**tor)
        if not ctl.actuator:row.update(m.motor.motor_state(q,qd,tor['motorTorqueNm']))
        row.update(comZMm=(u[0]+sum(p['m'+k]*m.sites(q)[k][0][1] for k in ('2','3','6'))/m.total_mass)*1000,
            comVelocityZMmS=(v[0]+m.mass_terms(q)['B']/m.total_mass*qd)*1000)
        ground_under_hip=surface_height(terrain,t)
        clearance=(u[0]-ground_under_hip)*1000-case['undersideOffsetMm'] if case['undersideOffsetMm'] is not None else None
        phase='end-stop' if min(abs(u[1]-sl),abs(u[1]-sh))<1e-8 and abs(v[1])<1e-7 else 'contact' if previous_contact else 'free-flight'
        row.update(demandTorqueNm=row['stoppingDemandTorqueNm'],chassisClearanceMm=clearance,motionPhase=phase,
            preProjectionPenetrationMm=prepen,postProjectionPenetrationMm=postpen,
            energyBalanceResidualJ=ke+pe-(rows[0]['energyJ'] if rows else ke+pe)-work-dampingwork-terrainwork-externalwork+motorloss+stoploss+contactloss-stabilization)
        frame.update(chassisClearanceMm=clearance,motionPhase=phase,controllerPhase=tor['controllerPhase'])
        rows.append(row);frames.append(frame);sample_t=t;sumJ[:]=[0.,0.];sumN=sumT=0.;points.clear();slips.clear()
    append()
    if rows[0]['penetrationMm']>1e-7:
        raise ValueError('Initial wheel overlaps terrain; adjust initial pose/terrain delay.')
    if rows[0]['chassisClearanceMm'] is not None and rows[0]['chassisClearanceMm']<=0:
        raise ValueError('Initial chassis underside clearance is nonpositive; reduce the underside offset or change the initial case pose/drop.')
    while t<c['duration']-1e-12:
        q=m.inverse(u[1]);qd=v[1]/m.jacobian(q);tor=ctl.torques(q,qd,previous_contact if ctl.actuator else contacted,time=t,state=dict(h=u[0],vh=v[0],contacted=previous_contact));inv=mass_at(q);dt=min(c['dt'],c['duration']-t,next_sample-t)
        f=(m.spring(q)['torque']+tor['motorTorqueNm']+tor['jointPassiveNm']-c['dampingNms']*qd)/m.jacobian(q);fx,fz=m.force
        curve=m.Jref*(-m.distance(q))/m.jacobian(q)**4*v[1]**2
        acc=inverse((-mt*p['g']+fz,f+curve-mw*p['g']*az+ax*fx+az*fz,m.Mw))
        if m.finite_links:
            terms=m.mass_terms(q)
            acc=inverse((-terms['A']*p['g']+fz-terms['Hprime']*v[1]**2,
                f-p['g']*terms['H']+ax*fx+az*fz-.5*terms['Dprime']*v[1]**2,m.Mw))
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
        check_motor_step(m,qd,dt)
        beforeq=q;beforevh=v[0];beforewheelvh=v[0]+az*v[1];before_position=(ax*u[1],u[0]+az*u[1],u[2]);event_start=len(events)
        vertical_momentum=(terms['A']*v[0]+terms['H']*v[1]) if m.finite_links else None
        # Exact constant-force drift/kick; contacts use the physical velocity only.
        for k in range(3):u[k]+=v[k]*dt+.5*acc[k]*dt*dt;v[k]+=acc[k]*dt
        if m.finite_links:
            # h is cyclic apart from external gravity/load: integrate its
            # canonical momentum exactly through the changing finite geometry.
            # This prevents internal leg motion creating vertical COM impulse.
            drift_terms=m.mass_terms(m.inverse(max(sl,min(sh,u[1]))))
            v[0]=(vertical_momentum+(-drift_terms['A']*p['g']+fz)*dt-drift_terms['H']*v[1])/drift_terms['A']
        t+=dt;steps+=1
        # Keep the same canonical output clock as the native contact engine.
        if abs(t-c['duration'])<1e-10:t=c['duration']
        elif abs(t-next_sample)<1e-10:t=next_sample
        inv=mass_at(m.inverse(max(sl,min(sh,u[1]))))
        # Unilateral guide-end impulse conserves chassis/wheel vertical momentum.
        if u[1]<=sl+1e-12 and v[1]<0 or u[1]>=sh-1e-12 and v[1]>0:
            endpoint=sl if u[1]<=sl+1e-12 else sh;atq=m.lo if abs(endpoint-m.distance(m.lo))<1e-12 else m.hi
            u[1]=endpoint
            if (endpoint==sl and v[1]<0) or (endpoint==sh and v[1]>0):
                before=kinetic(v);momentum=lambda: m.mass_terms(atq)['A']*v[0]+m.mass_terms(atq)['H']*v[1] if m.finite_links else mt*v[0]+mw*az*v[1];momentum_before=momentum();j=-v[1]/inv[1][1];dv=inverse((0,j,0));v[:]=[a+b for a,b in zip(v,dv)];stoploss+=max(0,before-kinetic(v))
                typ='compression-stop' if atq==m.hi else 'extension-stop'
                if not any(e['type']==typ for e in events):events.append(dict(t=t,type=typ,verticalMomentumBeforeKgMS=momentum_before,verticalMomentumAfterKgMS=momentum(),dissipatedEnergyJ=max(0,before-kinetic(v))))
                if atq==m.lo:ctl.extended=True
        dampingwork-=c['dampingNms']*qd*qd*dt
        motorloss+=tor['motorLossPowerW']*dt
        contacts=[]
        for gap,n,pt in geometry(t):
            jn=jac(n);normal_speed=product(jn,v)-n[0]*speed
            if (gap<=1e-8 or gap+normal_speed*dt<=0) and product(jn,inverse(jn))>1e-14:
                tangent=(n[1],-n[0]);jt=jac(tangent,True)
                contacts.append([gap,n,pt,jn,jt,0.,0.])
        contact_ke_before=kinetic(v);pre_contact_vh=v[0];pre_contact_wheel_vh=v[0]+az*v[1];step_terrain_work=0.;stop_loss_before=stoploss
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
                if first_raised is None and raised_contact(terrain,t,pt):first_raised=t;events.append(dict(t=t,type='first-raised-terrain-contact'))
        terrainwork+=step_terrain_work;contactloss+=contact_ke_before+step_terrain_work-kinetic(v)-(stoploss-stop_loss_before)
        if active and not contacted:contacted=True;events.append(dict(t=t,type='first-contact',chassisVelocityMmS=beforevh*1000,preImpulseChassisVelocityMmS=pre_contact_vh*1000,preImpulseWheelVelocityZMmS=pre_contact_wheel_vh*1000,postImpulseChassisVelocityMmS=v[0]*1000,postImpulseWheelVelocityZMmS=(v[0]+az*v[1])*1000,contactGapMm=min(g[0] for g in geometry(t))*1000,contactDetection='First unilateral impulse; positive gap uses speculative gap/step contact'))
        if previous_contact and not active and case['kind']=='jump' and not any(e['type']=='takeoff' for e in events):events.append(dict(t=t,type='takeoff'))
        previous_contact=active
        if not m.finite_links and case['kind']=='jump' and beforevh>0>=v[0] and any(e['type']=='takeoff' for e in events) and not any(e['type']=='apex' for e in events):events.append(dict(t=t,type='apex',chassisZMm=u[0]*1000))
        if contacted and beforevh<0<=v[0] and not any(e['type']=='chassis-arrest' for e in events):events.append(dict(t=t,type='chassis-arrest',beforeStepChassisVelocityMmS=beforevh*1000,afterStepChassisVelocityMmS=v[0]*1000))
        externalwork+=fx*(ax*u[1]-before_position[0])+fz*(u[0]+az*u[1]-before_position[1])+m.Mw*(u[2]-before_position[2])
        # Additional-load work excludes the numerical position projection.
        # Separate mass-weighted position projection; never changes velocity/KE.
        def potential():
            qq=m.inverse(max(sl,min(sh,u[1])));return m.motor.motor_state(qq,0,0)['coggingPotentialJ']+m.spring(qq)['energy']+(finite_gravity(m,qq,u[0]) if m.finite_links else p['g']*(mt*u[0]+mw*az*u[1]))
        potential_before=potential()+kinetic(v)
        prepen=max(0.,-min(g[0] for g in geometry(t)))*1000;maxpre=max(maxpre,prepen)
        if prepen>penetration_limit_mm:
            maxpen=max(maxpen,prepen);postpen=prepen;maxpost=max(maxpost,postpen);termination='contact-penetration-limit'
            events.append(dict(t=t,type=termination,penetrationMm=prepen,limitMm=penetration_limit_mm,stage='before-position-projection'))
            work+=tor['motorTorqueNm']*(m.inverse(u[1])-beforeq);append();break
        for _ in range(max(10,int(c['iterations']))):
            inv=mass_at(m.inverse(max(sl,min(sh,u[1]))))
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
        q=m.inverse(u[1]);stabilization+=potential()+kinetic(v)-potential_before
        work_q=m.lo if case['kind']=='jump' and ctl.extended and tor['motorTorqueNm']!=0 else q
        work+=tor['motorTorqueNm']*(work_q-beforeq)
        for event in events[event_start:]:
            if event['type'] in ('first-contact','chassis-arrest','compression-stop','extension-stop'):
                ee=energy_fields(m,q,u[0],v[0],v[1],v[2])
                event['state']=dict(t=t,theta2=q/R,chassisVelocityMmS=v[0]*1000,wheelVelocityZMmS=(v[0]+az*v[1])*1000,
                    kineticJ=sum(ee[k] for k in ('chassisKineticJ','wheelKineticJ','rotorKineticJ','legacyJointRotorKineticJ','linkKineticJ')),motorTorqueNm=tor['motorTorqueNm'],
                    motorWorkJ=work,dampingWorkJ=dampingwork,motorDissipatedJ=motorloss,terrainWorkJ=terrainwork,externalWorkJ=externalwork,
                    contactDissipationJ=contactloss,stopDissipationJ=stoploss,positionStabilizationJ=stabilization,**ee)
                event['state']['energyBalanceResidualJ']=event['state']['kineticJ']+sum(ee[k] for k in ('springEnergyJ','gravityEnergyJ','coggingPotentialJ'))-rows[0]['energyJ']-work-dampingwork-terrainwork-externalwork+motorloss+stoploss+contactloss-stabilization

        if postpen>penetration_limit_mm:
            termination='contact-penetration-limit';events.append(dict(t=t,type=termination,penetrationMm=postpen,limitMm=penetration_limit_mm,stage='after-coupled-position-projection'));append();break
        ground_under_hip=surface_height(terrain,t)
        if case['undersideOffsetMm'] is not None and (u[0]-ground_under_hip)*1000<=case['undersideOffsetMm']:
            events.append(dict(t=t,type='underside-contact'));termination='underside-contact';append();break
        comvz=v[0]+m.mass_terms(q)['B']/m.total_mass*v[1]/m.jacobian(q) if m.finite_links else v[0]
        observation.step(t,u[0],comvz if m.finite_links and case['kind']=='jump' else v[0],u[0]+az*u[1],v[0]+az*v[1],r,active,events)
        if case['kind']=='jump':
            comz=u[0]+sum(p['m'+k]*m.sites(q)[k][0][1] for k in ('2','3','6'))/m.total_mass
            comvz=v[0]+m.mass_terms(q)['B']/m.total_mass*v[1]/m.jacobian(q)
            if observation.takeoff is not None:com_observation.capture_takeoff(t,comz,comvz)
            com_observation.step(t,comz,comvz,active)
            if m.finite_links and com_observation.apex and not any(e['type']=='apex' for e in events):events.append(dict(t=t,type='apex',chassisZMm=u[0]*1000,comZMm=comz*1000,criterion='whole-body COM vertical velocity'))
        if not all(math.isfinite(a) for a in u+v):raise ValueError('Analytical contact diverged.')
        if stop_at_assessment and ((case['kind']=='landing' and any(e['type'] in ('chassis-arrest','compression-stop') for e in events)) or (case['kind']=='jump' and observation.jump_finished())):
            termination='assessment-outcome';append();break
        if t>=next_sample-1e-10 or t>=c['duration']-1e-10:append();next_sample+=1/c['outputHz']
    snapshot=dict(params=p,solverConfig=c,contactConfig=cc)
    if 'terrainConfig' in payload:snapshot['terrainConfig']=m.terrain_config
    if 'caseConfig' in payload:snapshot['caseConfig']=case
    if 'motorConfig' in payload:snapshot['motorConfig']=m.motor.config
    result=dict(schema='kinefold/contact-v2',engine='analytical',params=p,runConfig=c,contactConfig=cc,caseConfig=case,snapshot=snapshot,designHash=model_identity(m,cc,case),rows=rows,frames=frames,events=events,caseMetrics=case_metrics(rows,events,m,case),terrain=terrain['terrain'],diagnostics=dict(termination=termination,elapsedSeconds=t,steps=steps,dt=c['dt'],iterations=c['iterations'],integrator='Independent reduced-mass constant-force drift with accumulated unilateral Coulomb PGS impulses',rigidBodies=2,chassisBodyMassKg=p['m1'],wheelBodyMassKg=mw,wheelMomentKgM2=I,chassisPitchLocked=True,wheelSpinFree=True,maxPenetrationMm=maxpen,maxGuideResidualMm=0.,maxConstraintPositionErrorMm=0.,maxConstraintAngleErrorDeg=0.,maxContactNormalForceN=maxnf,maxContactTangentialForceN=maxtf,firstRaisedContactTimeS=first_raised,effectiveFriction=cc['friction'],restitution=0,positionStabilization='Separate configuration-dependent mass-weighted projection; no velocity kick; kinetic/potential change ledgered',stopDissipationJ=stoploss,resolvedInertiasKgM2=m.I,builderMassesKg={k:p['m'+k] for k in ('1','2','3','5','6')},modelRevision='straight-guide-contact-v2'),scope=dict(mode='terrain-contact',quarterModel=True,fixture='floating-chassis',coordinates='+x left / +z up / mm'),warnings=['Experimental rigid two-body quarter model; no tire, rigid chassis collision shape or hardware validation; entered underside point-clearance stops are assessed.','Position projection applies no physical velocity kick; its geometry-induced rotor kinetic and potential energy change is recorded separately.','Sharp contact impulse peaks and travel-stop events require timestep refinement.'])

    if 'terrainConfig' in payload:result['terrainConfig']=m.terrain_config
    if m.terrain_config and case['kind']=='terrain-stability':result['warnings'].append('Source terrain is a synthesized design envelope represented by a rigid periodic 2D profile. Longitudinal grade is simulated only for terrain-v2. Cross-slope, corridor, soil/snow/water behavior and surface-specific friction are not simulated. The chassis follows a vertical slide, not free vehicle translation; guide reactions alter ordinary incline normal-load formulas.')
    if 'motorConfig' in payload:result['motorConfig']=m.motor.config
    if 'actuatorConfig' in payload:
        result['actuatorConfig']=m.actuator_config;result['snapshot']['actuatorConfig']=m.actuator_config
    if m.finite_links:
        result['diagnostics'].update(rigidBodies=4,finiteLinkDynamics=True,modelRevision='finite-link-contact-v1',linkMomentsKgM2={k:m.I[k] for k in ('2','3')},totalBodyMassKg=m.total_mass)
        result['warnings'][0]='Experimental finite uniform-link quarter model with exact analytical mass matrix; no tire, chassis collision shape or hardware validation.'
    result['energyEstimate']=energy_estimate(m,case) if case['energyMethod'] else None
    result['diagnostics'].update(reflectedHipInertiaKgM2=m.Jref,energyBalanceResidualJ=rows[-1]['energyBalanceResidualJ'],maxPreProjectionPenetrationMm=maxpre,maxPostProjectionPenetrationMm=maxpost,penetrationTerminationLimitMm=penetration_limit_mm,maxTravelStopDriftMm=max_stop_position_error)
    result['targetObservations']=observation.result()
    result['targetObservations'].update(com_observation.result())
    result['caseMetrics'].update(com_observation.result())
    if m.finite_links and case['kind']=='jump':result['targetObservations'].update(flightRiseMm=com_observation.result()['jumpComRiseMm'],apexCriterion='whole-body COM vertical velocity')
    return annotate_contact_work(result,m)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--request-stdin',action='store_true',required=True);parser.parse_args()
    try:print(json.dumps(simulate_contact(json.load(sys.stdin)),allow_nan=False))
    except (ValueError,KeyError,TypeError,ArithmeticError) as error:print(json.dumps(dict(error=str(error))));sys.exit(1)
