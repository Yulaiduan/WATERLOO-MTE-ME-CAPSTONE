"""Shared experimental contact geometry, scenario and controller laws.

Imported by independent analytical/Pymunk integrators; no engine is imported.
Inputs are complete builder mm/deg/kg/N, run SI/s, optional strict caseConfig.
Outputs are SI initial conditions/torques and JSON-safe scenario assessments.
Rigid quarter-model laws are illustrative, not hardware peak-torque certification.
"""
import math
import hashlib
import json
from dynamic_model import Model, R, mul, validate, finite

CASE_DEFAULTS = dict(kind='terrain-stability',jumpTorqueNm=20.,landingDropMm=100.,
    landingOpenFraction=2/3,landingBrakeTorqueNm=20.,landingBrakeLimitNm=200.,
    brakeStrategy='entered',undersideOffsetMm=50.,energyMethod=True)


def resolve_case(payload):
    raw=payload.get('caseConfig')
    if 'caseConfig' not in payload:return dict(CASE_DEFAULTS)
    if not isinstance(raw,dict) or set(raw)!=set(CASE_DEFAULTS):
        raise ValueError('caseConfig requires exactly '+', '.join(CASE_DEFAULTS))
    c=dict(raw)
    if c['kind'] not in ('terrain-stability','jump','landing'):raise ValueError('Unknown contact case kind.')
    if c['brakeStrategy'] not in ('entered','energy-sized'):raise ValueError('Unknown brakeStrategy.')
    for k in ('jumpTorqueNm','landingDropMm','landingBrakeTorqueNm','landingBrakeLimitNm'):
        if not finite(c[k]) or not 0<=c[k]<=(5000 if k=='landingDropMm' else 10000):raise ValueError(k+' exceeds the allowed finite case range.')
    if not finite(c['landingOpenFraction']) or not .01<=c['landingOpenFraction']<=.99:raise ValueError('landingOpenFraction must be within [.01,.99].')
    if c['undersideOffsetMm'] is not None and (not finite(c['undersideOffsetMm']) or not 0<=c['undersideOffsetMm']<=5000):raise ValueError('undersideOffsetMm must be null or nonnegative finite.')
    if type(c['energyMethod']) is not bool:raise ValueError('energyMethod must be boolean.')
    return c


class ContactGeometry(Model):
    """Reuse exact VSL geometry/spring helpers, never prescribed-input dynamics."""

    def __init__(self, params, config):
        validate(params, config)
        p, c = dict(params), dict(config)
        if p['m1'] <= 0 or p['m6'] <= 0:
            raise ValueError('Terrain contact requires positive explicit m1 and m6; no mass is substituted.')
        if any(p[k] != 0 for k in ('m2', 'm3', 'm5')):
            raise ValueError('Terrain contact supports massless links/idler only: m2=m3=m5=0.')
        if c['inertiaModel'] != 'uniform-rods-discs' or any(c[k] != 0 for k in ('I2', 'I3', 'I5', 'I6', 'hipRotorInertiaKgM2')):
            raise ValueError('Terrain contact requires uniform wheel-disc inertia and zero additional/custom/rotor inertia.')
        if abs(p['L2'] - p['L3']) > 1e-10 or abs(p['ra'] / p['rb'] - 2) > 1e-12:
            raise ValueError('Terrain contact requires certified straight travel: equal L2/L3 and ra/rb=2. Curved guide geometry is unsupported.')
        if c['inputRiseMm'] != 0:
            raise ValueError('Terrain contact uses sharp square polygons; inputRiseMm must be zero.')
        if p['loadMode'] == 'contact':
            raise ValueError('Prescribed contact loads are unsupported with actual contact. Use weight or explicit global additional loads.')
        if p['te'] == p['tc']:
            raise ValueError('Terrain contact requires a nonempty monotonic working range.')
        self.p, self.c = p, c
        self.q0, self.lo, self.hi = p['theta2'] * R, p['te'] * R, p['tc'] * R
        self.ab, self.dc, self.fe = p['ra'] / p['rb'], p['rd'] / p['rc'], p['rf'] / p['re']
        self.k3, self.k5 = 1-self.ab, 1-1/self.dc
        self.K = 1-self.ab+(self.ab-1/self.dc)/self.fe
        self.mean = (math.pi + p['phi0']*R)/2
        # C(q) = axis * 2L cos(q-mean), identically, including alpha/phi0.
        self.axis = self.rotate((-math.cos(self.mean), -math.sin(self.mean)))
        for n in range(-2, 4):
            if self.lo-1e-10 <= self.mean+n*math.pi <= self.hi+1e-10:
                raise ValueError('Straight-path Jacobian is singular or changes sign in the working range; move te/tc away from the turning point.')
        self.branch = 1 if self.q0-self.mean > 0 else -1
        self.jacobian_min = min(abs(self.jacobian(q)) for q in (self.lo,self.hi))
        if self.jacobian_min < 1e-7:
            raise ValueError('Straight guide Jacobian is too close to zero for this contact model.')
        self.route = self.exit_route() if p['springEnabled'] else dict(applied=0, shift=0)
        self.reference_payout = self.geometry(math.pi/2, reference=True)['payout'] if p['springEnabled'] else 0
        if p['springEnabled']:
            for q in self.candidates(self.lo,self.hi):
                self.geometry(q)
        self.force, self.Mw = self.loads()
        self.I = {'2':0., '3':0., '5':0., '6':.5*p['m6']*(p['rw']/1000)**2}

    def distance(self,q):
        return 2*self.p['L2']/1000*math.cos(q-self.mean)

    def jacobian(self,q):
        return -2*self.p['L2']/1000*math.sin(q-self.mean)

    def inverse(self,distance):
        u = distance/(2*self.p['L2']/1000)
        if abs(u) > 1+1e-12:
            raise ValueError('Actual wheel/chassis separation exceeds the exact VSL geometric domain.')
        return self.mean+self.branch*math.acos(max(-1,min(1,u)))

    def internal_force(self,q,qd):
        """Actual equal/opposite guide force, no gravity or contact duplication."""
        Q = self.spring(q)['torque']+self.c['hipTorqueNm']-self.c['dampingNms']*qd
        return Q/self.jacobian(q)


def validate_contact_request(payload):
    if not isinstance(payload,dict) or set(payload) not in ({'engine','params','runConfig','contactConfig'}, {'engine','params','runConfig','contactConfig','caseConfig'}):
        raise ValueError('Contact request requires exactly engine, params, runConfig and contactConfig.')
    if payload['engine'] not in ('pymunk','analytical'):
        raise ValueError('Contact engine must be analytical or pymunk.')
    cc = payload['contactConfig']
    if not isinstance(cc,dict) or set(cc) != {'mode','friction','restitution','drive'}:
        raise ValueError('contactConfig requires exactly mode, friction, restitution and drive.')
    if cc['mode'] != 'terrain-contact' or cc['drive'] != 'free':
        raise ValueError('Contact mode must be terrain-contact with freely backdrivable drive=free.')
    if not finite(cc['friction']) or not 0 <= cc['friction'] <= 2:
        raise ValueError('Contact friction must be finite within [0,2].')
    if not finite(cc['restitution']) or cc['restitution'] != 0:
        raise ValueError('This contact model requires zero restitution.')
    case=resolve_case(payload)
    model=ContactGeometry(payload['params'],payload['runConfig'])
    if case['kind'] in ('jump','landing') and model.axis[1]*model.jacobian((model.lo+model.hi)/2)<=0:
        raise ValueError('Jump/landing require tc to be the geometrically compressed endpoint; this straight-path branch reverses that convention.')
    if case['kind']=='landing' and case['brakeStrategy']=='energy-sized' and abs(model.axis[0])>1e-10:
        raise ValueError('energy-sized braking requires a vertical guide on a stationary flat floor; use entered torque and dynamic search for tilted guides.')
    return model


def initial_conditions(m,case):
    q=m.q0
    if case['kind']=='jump':q=m.hi
    elif case['kind']=='landing':q=m.hi+case['landingOpenFraction']*(m.lo-m.hi)
    C=m.sites(q)['6'][0];z=m.p['rw']/1000
    if case['kind']=='landing':z+=case['landingDropMm']/1000
    return q,z-C[1],C[0],z


def world(v):return [-v[0]*1000,0,v[1]*1000]


def terrain_spec(m,case):
    p,c=m.p,m.c;r=p['rw']/1000;q,h,x,z=initial_conditions(m,case)
    speed=c['inputSpeedMmS']/1000 if case['kind']=='terrain-stability' else 0.
    height=c['inputHeightMm']/1000 if case['kind']=='terrain-stability' else 0.
    width=c['inputPlateauMm']/1000;gap=c['inputGapMm']/1000
    corner=math.sqrt(max(0,2*r*height-height*height)) if height<=2*r else 0
    clearance=0 if height==0 else (r if height>=r else corner)
    front=x-clearance-speed*c['inputDelayS'];count=math.ceil((speed*c['duration']+4*r)/(width+gap))+3
    boxes=[]
    for i in range(count):
        if height==0:break
        right=front-i*(width+gap);left=right-width
        boxes.append([(left,0),(right,0),(right,height),(left,height)])
    extent=abs(x)+speed*c['duration']+count*(width+gap)+10;base=[(-extent,0),(extent,0)]
    public=dict(polygonsMm=[[world(v) for v in b] for b in boxes],baseSegmentMm=[world(v) for v in base],
        translationVelocityMmS=[-speed*1000,0,0],cornerRadiusMm=0,firstContactClearanceMm=clearance*1000,
        upperCornerClearanceMm=corner*1000,initialFrontEdgeXMm=-front*1000,
        initialPossibleContactTimeS=c['inputDelayS'] if height else None,heightMm=height*1000,
        plateauMm=width*1000,gapMm=gap*1000,wheelAngleZeroDirection='-x',coordinates='Kinefold +x left / +z up, mm')
    return dict(boxes=boxes,base=base,speed=speed,height=height,terrain=public)


def model_identity(m,contact,case):
    return hashlib.sha256(json.dumps(dict(params=m.p,runConfig=m.c,contactConfig=contact,caseConfig=case),sort_keys=True,separators=(',',':')).encode()).hexdigest()


def usable_compression(m,q,case):
    """Flat-floor compression endpoint before the entered underside threshold."""
    target=m.hi
    offset=case['undersideOffsetMm']
    if offset is None:return target
    clearance=lambda angle:m.p['rw']/1000-m.sites(angle)['6'][0][1]-offset/1000
    if clearance(q)<=0:return q
    if clearance(target)>0:return target
    lo,hi=q,target
    for _ in range(60):
        mid=(lo+hi)/2
        if clearance(mid)>0:lo=mid
        else:hi=mid
    return lo


def energy_estimate(m,case):
    q,h,x,z=initial_conditions(m,case);qc=m.hi
    if case['kind']=='jump':
        work=case['jumpTorqueNm']*(m.hi-m.lo)
        spring=m.spring(m.hi)['energy']-m.spring(m.lo)['energy']
        return dict(averageTorqueNm=None,motorWorkToExtensionJ=work,springReleaseToExtensionJ=spring,
            idealGrossCOMRiseMm=max(0,work+spring)/((m.p['m1']+m.p['m6'])*m.p['g'])*1000 if m.p['g']>0 else None,
            meaning='Available motor and spring work divided by total weight; includes stance rise, excludes stop/contact losses, not guaranteed jump apex.')
    if case['kind']=='terrain-stability':return dict(averageTorqueNm=None,meaning='No single energy-sized torque for moving terrain.')
    if abs(m.axis[0])>1e-10:return dict(averageTorqueNm=None,applicable=False,meaning='Chassis-only energy estimate requires a vertical guide and fixed wheel centre after impact; use dynamic search for tilted geometry.')
    # Conservative energy-to-constant-angle-work estimate, wheel held at floor.
    qc=usable_compression(m,q,case)
    travel=qc-q
    delta_h=m.sites(qc)['6'][0][1]-m.sites(q)['6'][0][1]
    energy=m.p['m1']*m.p['g']*case['landingDropMm']/1000
    energy+=m.p['m1']*m.p['g']*delta_h+m.spring(q)['energy']-m.spring(qc)['energy']
    return dict(energyToAbsorbJ=max(0,energy),availableCompressionRad=max(0,travel),usableCompressionEndDeg=qc/R,
        averageTorqueNm=max(0,energy)/travel if travel>0 else None,
        meaning='Post-wheel-impact chassis energy/work average over usable compression before stop/underside threshold; vertical flat-floor estimate excludes wheel impact loss, redistribution and is not a guaranteed dynamic peak or successful arrest.')


class CaseController:
    def __init__(self,m,case):
        self.m,self.case=m,case;self.contacted=False;self.extended=False
        self.energy=energy_estimate(m,case)
        if case['kind']=='landing' and case['brakeStrategy']=='energy-sized' and self.energy.get('averageTorqueNm') is None:
            raise ValueError('Energy-sized braking has no usable compression stroke before the entered underside threshold; adjust the case or use an entered torque.')
    def torques(self,q,qd,contacted=False):
        self.contacted=self.contacted or contacted;m,c=self.m,self.case
        hold=brake=0.;motor=m.c['hipTorqueNm'];phase='terrain'
        if c['kind']=='jump':
            if q<=m.lo+1e-7:self.extended=True
            motor=0. if self.extended else -c['jumpTorqueNm'];phase='jump-coast' if self.extended else 'jump-extension'
        elif c['kind']=='landing':
            if not self.contacted:
                # Relative acceleration zero under free fall, even on tilted guides:
                # wheel extra load projected through inverse reduced mass matrix.
                ax,az=m.axis;M=m.p['m1']+m.p['m6'];mw=m.p['m6']
                fx,fz=m.force
                fhold=-(ax*fx+az*fz-mw*az*fz/M)
                hold=fhold*m.jacobian(q)-m.spring(q)['torque']+m.c['dampingNms']*qd
                motor=hold;phase='landing-hold'
            else:
                requested=c['landingBrakeTorqueNm'] if c['brakeStrategy']=='entered' else self.energy['averageTorqueNm']
                brake=-min(requested,c['landingBrakeLimitNm']) if qd>0 else 0.
                motor=brake;phase='landing-brake' if qd>0 else 'landing-release'
        return dict(motorTorqueNm=motor,holdTorqueNm=hold,brakeTorqueNm=brake,controllerPhase=phase)


def energy_fields(m,q,h,vh,sd,omega):
    ax,az=m.axis;s=m.distance(q);p=m.p
    chassis=.5*p['m1']*vh*vh
    wheel=.5*p['m6']*((ax*sd)**2+(vh+az*sd)**2)+.5*m.I['6']*omega*omega
    return dict(chassisKineticJ=chassis,wheelKineticJ=wheel,springEnergyJ=m.spring(q)['energy'],
        gravityEnergyJ=p['g']*(p['m1']*h+p['m6']*(h+az*s)))


def case_metrics(rows,events,m,case):
    impact=next((e for e in events if e['type']=='first-contact'),None)
    takeoff=next((e for e in events if e['type']=='takeoff'),None)
    apex=next((e for e in events if e['type']=='apex'),None)
    arrest=next((e for e in events if e['type']=='chassis-arrest'),None)
    bottom=next((e for e in events if e['type']=='compression-stop'),None)
    under=next((e for e in events if e['type']=='underside-contact'),None)
    failed=case['kind']=='landing' and (under is not None or (bottom is not None and (arrest is None or bottom['t']<=arrest['t'])))
    return dict(kind=case['kind'],takeoffTimeS=takeoff['t'] if takeoff else None,
        apexTimeS=apex['t'] if apex else None,apexChassisZMm=apex['chassisZMm'] if apex else max(r['chassisZMm'] for r in rows),impactTimeS=impact['t'] if impact else None,
        impactChassisVelocityMmS=impact.get('chassisVelocityMmS') if impact else None,
        firstArrestTimeS=arrest['t'] if arrest else None,maxCompressionDeg=max(r['theta2'] for r in rows),
        minimumUndersideClearanceMm=min(r.get('chassisClearanceMm',r['chassisZMm']-case['undersideOffsetMm']) for r in rows) if case['undersideOffsetMm'] is not None else None,
        landingSuccess=(bool(arrest) and not failed) if case['kind']=='landing' else None,
        outcome=('bottom-out-before-arrest' if failed and bottom else 'underside-contact' if under else 'arrested' if arrest else 'partial-no-arrest') if case['kind']=='landing' else 'completed-observation',
        energyEstimate=energy_estimate(m,case) if case['energyMethod'] else None,
        demandTorqueMeaning='Kinetic energy divided by remaining angular stroke plus gravity/spring work estimate; not a certified impact peak.')


def stopping_demand(m,q,qd,vh,case=None):
    if abs(m.axis[0])>1e-10:return None
    target=usable_compression(m,q,case or CASE_DEFAULTS)
    remain=target-q
    if remain<=1e-9 or vh>=0:return None
    delta_h=m.sites(target)['6'][0][1]-m.sites(q)['6'][0][1]
    energy=.5*m.p['m1']*vh*vh+m.p['m1']*m.p['g']*delta_h+m.spring(q)['energy']-m.spring(target)['energy']
    return max(0,energy/remain)


def minimum_required_torque(payload,simulate,iterations=5):
    """Coarse bounded scan plus local bracket refinement, never a global proof."""
    import copy
    case=resolve_case(payload)
    if case['kind']!='landing':raise ValueError('Torque search requires landing case.')
    trials=[];limit=case['landingBrakeLimitNm']
    def trial(torque):
        request=copy.deepcopy(payload);request['caseConfig']={**case,'brakeStrategy':'entered','landingBrakeTorqueNm':torque}
        result=simulate(request);metrics=result.get('caseMetrics',{})
        success=bool(metrics.get('landingSuccess'))
        trials.append(dict(torqueNm=torque,success=success,outcome=metrics.get('outcome'),
            firstArrestTimeS=metrics.get('firstArrestTimeS'),termination=result.get('diagnostics',{}).get('termination')))
        return success
    for torque in sorted(set(limit*i/4 for i in range(5))):trial(torque)
    passes=[r['torqueNm'] for r in trials if r['success']]
    limitation='Lowest passing tested torque and local bracket only; nonmonotone feasibility, timestep and observation duration prevent a global minimum claim.'
    if not passes:return dict(feasible=False,status='no-passing-tested-torque',torqueNm=None,limitNm=limit,
        reason='No passing tested torque in the bounded coarse scan.',evaluations=len(trials),trials=trials,limitation=limitation)
    hi=min(passes)
    if hi==0:return dict(feasible=True,status='passing-tested-torque',torqueNm=0.,lowerBoundNm=0.,limitNm=limit,
        evaluations=len(trials),trials=trials,limitation=limitation)
    lo=max(r['torqueNm'] for r in trials if r['torqueNm']<hi and not r['success'])
    for _ in range(min(7,max(0,iterations))):
        mid=(lo+hi)/2
        if trial(mid):hi=mid
        else:lo=mid
    return dict(feasible=True,status='passing-tested-bracket',torqueNm=hi,lowerBoundNm=lo,limitNm=limit,
        evaluations=len(trials),trials=trials,limitation=limitation)


def floor_under_hip(spec,t):
    """Highest exact terrain surface under the x-fixed hip, in source metres."""
    offset=spec['speed']*t
    return max([0.]+[spec['height'] for b in spec['boxes'] if b[0][0]+offset<=0<=b[1][0]+offset])
