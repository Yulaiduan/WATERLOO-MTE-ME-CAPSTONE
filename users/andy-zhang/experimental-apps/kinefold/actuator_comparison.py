"""Automatic catalog screening and bounded independent dynamic refinement.

Run: .venv/Scripts/python.exe actuator_comparison.py --request FILE --output DIR.
Input JSON captures project-v3, editable SI/mm assumptions and finite budgets;
outputs atomic progress/results/details JSON in the explicitly supplied local
job directory. All exact catalog motor/SKU pairs receive fast necessary/energy
screens; only selected rows receive actual independent finite-link rollouts.
Experimental quarter model and assumed motor envelope: no verified hardware
winner, whole-robot stability, thermal certification or global optimization.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import time

from actuation_limits import ACTUATOR_DEFAULTS, torque_limit

ROOT=Path(__file__).resolve().parent
ASSUMPTIONS=dict(hipBeltRatio=1.,dropHeightMm=2000.,jumpHeightMm=2000.,minClearanceMm=50.,undersideOffsetMm=50.,
    stopReserveDeg=1.,landingOpenFraction=2/3,dcBusV=48.,peakPhaseCurrentA=None,
    continuousPhaseCurrentA=None,noLoadRpm=6000.,baseSpeedFraction=.5,
    peakDurationS=2.,motoringPowerW=5000.,brakingPowerW=5000.,regenPowerW=5000.,
    regenEnergyJ=5000.,regenAcceptance=True,unknownEfficiency=.9,reverseEfficiency=.9,
    unknownGearboxInputInertiaKgM2=0.,additionalOutputInertiaKgM2=0.,
    rotorInertiaScenario='nominal',lossScenario='medium',lossLowFraction=.01,
    lossMediumFraction=.03,lossHighFraction=.08,lossReferenceRadS=10.,
    frictionSmoothingRadS=10.,rideKpNPerM=5000.,rideKdNsPerM=350.,rideTargetStepMm=0.,rideTargetStepTimeS=.1,
    recoveryKpNPerM=3000.,recoveryKdNsPerM=300.,holdKpNmPerRad=120.,holdKdNms=15.,
    dynamicDt=.000125,dynamicDurationS=3.,dynamicOutputHz=50.,
    terrainMaxRmsErrorMm=100.,terrainMaxBodyAccelMS2=100.,terrainMinContactFraction=.5,
    terrainMinTravelReserveDeg=0.,postArrestHoldS=.5,assumeKtCurrentCompatible=False)
BUDGET=dict(analyticalCandidates=6,pymunkCandidates=2,maxSeconds=480)
CASES=('landing','jump','terrain')


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()


def validate_assumptions(raw=None):
    if raw is None:return dict(ASSUMPTIONS)
    if not isinstance(raw,dict) or set(raw)-set(ASSUMPTIONS):raise ValueError('Unknown comparison assumption fields.')
    a={**ASSUMPTIONS,**raw}
    for key,value in a.items():
        if key in ('rotorInertiaScenario','lossScenario'):
            if value not in (('low','nominal','high') if key=='rotorInertiaScenario' else ('low','medium','high')):raise ValueError('Invalid '+key)
        elif key in ('regenAcceptance','assumeKtCurrentCompatible'):
            if type(value) is not bool:raise ValueError(key+' must be boolean.')
        elif key in ('peakPhaseCurrentA','continuousPhaseCurrentA') and value is None:continue
        elif isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=1e7:
            raise ValueError(key+' must be a bounded nonnegative finite number.')
    for k in ('dropHeightMm','jumpHeightMm','minClearanceMm','undersideOffsetMm'):
        if a[k]>5000:raise ValueError(k+' exceeds 5000 mm.')
    if not .01<=a['landingOpenFraction']<=.99 or not .01<=a['baseSpeedFraction']<1:raise ValueError('Invalid opening/base-speed fraction.')
    if not .01<=a['unknownEfficiency']<=1 or not .01<=a['reverseEfficiency']<=1:raise ValueError('Efficiency must be in [.01,1].')
    if not .0001<=a['dynamicDt']<=.002 or not .05<=a['dynamicDurationS']<=8 or not 5<=a['dynamicOutputHz']<=100:raise ValueError('Dynamic timing outside bounded range.')
    if a['dynamicDurationS']/a['dynamicDt']>80000:raise ValueError('Dynamic request exceeds step budget.')
    if not 0<=a['stopReserveDeg']<=10 or a['noLoadRpm']<=0 or a['lossReferenceRadS']<=0 or a['frictionSmoothingRadS']<=0:raise ValueError('Invalid reserve/speed assumption.')
    if not 1<=a['hipBeltRatio']<=3:raise ValueError('hipBeltRatio must be within [1,3].')
    if a['rideTargetStepMm']>500 or a['rideTargetStepTimeS']>30:raise ValueError('Ride target step requires 0..500 mm and 0..30 seconds.')
    if a['terrainMinContactFraction']>1:raise ValueError('Contact fraction must be within [0,1].')
    return a


def validate_budget(raw=None):
    if raw is None:return dict(BUDGET)
    if not isinstance(raw,dict) or set(raw)-set(BUDGET):raise ValueError('Unknown comparison budget fields.')
    b={**BUDGET,**raw}
    for k,lo,hi in (('analyticalCandidates',0,12),('pymunkCandidates',0,4),('maxSeconds',5,600)):
        if isinstance(b[k],bool) or not isinstance(b[k],(int,float)) or int(b[k])!=b[k] or not lo<=b[k]<=hi:raise ValueError('Invalid '+k)
    if b['pymunkCandidates']>b['analyticalCandidates']:raise ValueError('Pymunk shortlist cannot exceed analytical shortlist.')
    return b


def load_catalog():return json.loads((ROOT/'motor-gearbox-catalog.json').read_text(encoding='utf-8'))


def missing_metrics(catalog):
    motors=catalog['motors'];gears=catalog['gearboxes']
    return dict(motorCount=len(motors),gearboxCount=len(gears),
        allMotorSpeedCurvesMissing=all(m.get('noLoadRpm') is None for m in motors),
        motorSpeedMissing=sum(m.get('noLoadRpm') is None for m in motors),
        continuousTorqueMissing=sum(m.get('continuousTorqueNm') is None for m in motors),
        torqueConstantMissing=sum(m.get('torqueConstantNmPerA') is None for m in motors),
        gearboxEfficiencyMissing=sum(g.get('efficiency') is None for g in gears),
        gearboxInputInertiaMissing=sum(g.get('inputInertiaKgM2') is None for g in gears),
        additionalOutputHardwareInertiaUnmodeled=True,
        requiredBeforeHardwareSelection=[
            'Measured torque-speed curves at the chosen bus voltage and controller phase-current limit',
            'Kt and current convention (phase peak/RMS), winding resistance and inductance',
            'Continuous torque/current, peak duration, temperature and cooling/duty-cycle model',
            'Measured rotor inertia; gearbox input-equivalent inertia and forward/backdrive efficiency maps',
            'Regenerative braking limits and battery/brake-resistor power/energy acceptance',
            'Measured Coulomb/cogging torque, viscous drag, backlash/compliance and gearbox service factors',
            'Mechanical motor-to-gearbox shaft/mount compatibility and exact-SKU speed/load ratings'])


def candidate_hardware(m,g,a):
    flags=[]
    peak=m.get('peakTorqueNm')
    if peak is None or peak<=0:raise ValueError('Missing positive source peak torque.')
    base_n=g['ratio'];belt=a.get('hipBeltRatio',1.);n=base_n*belt;eta=g.get('efficiency')
    if eta is None:eta=a['unknownEfficiency'];flags.append('Forward efficiency assumed')
    key={'low':'rotorInertiaLowKgM2','nominal':'rotorInertiaKgM2','high':'rotorInertiaHighKgM2'}[a['rotorInertiaScenario']]
    jm=m.get(key)
    if jm is None:raise ValueError('Missing selected rotor-inertia scenario.')
    flags.append('Rotor inertia is Rev2 estimated geometry, not measured')
    jg=g.get('inputInertiaKgM2');jo=a['additionalOutputInertiaKgM2']
    if jg is None:jg=a['unknownGearboxInputInertiaKgM2'];flags.append('Missing gearbox input inertia explicitly substituted')
    flags.append('Additional external hip-side hardware inertia explicitly entered; gearbox input-equivalent J already covers its train')
    if belt!=1:flags.append('Extra hip belt assumed ideal rigid/lossless with no added mass or inertia')
    rpm=m.get('noLoadRpm')
    if rpm is None:rpm=a['noLoadRpm'];flags.append('No-load speed assumed at entered DC bus voltage')
    kt=m.get('torqueConstantNmPerA') or m.get('convertedKtNmPerA')
    if not a['assumeKtCurrentCompatible']:
        kt=None;flags.append('Kt/current convention unverified; current clipping and current result unavailable')
    else:flags.append('Kt/current convention explicitly assumed compatible')
    if m.get('continuousTorqueNm') is None:flags.append('Continuous motor torque unknown; thermal pass unavailable')
    flags.extend(['Reverse efficiency assumed','Power/regen/peak-duration limits are editable assumptions',
                  'Torque-speed plateau/linear rolloff is an approximation','Mechanical mounting compatibility unverified'])
    cfg={**ACTUATOR_DEFAULTS,'ratio':base_n,'hipBeltRatio':belt,'peakShaftNm':peak,'continuousShaftNm':m.get('continuousTorqueNm'),
        'noLoadRpm':rpm,'forwardEfficiency':eta,'reverseEfficiency':a['reverseEfficiency'],
        'gearboxPeakNm':g.get('peakOutputNm') or g.get('continuousOutputNm') or 10000.,
        'gearboxContinuousNm':g.get('continuousOutputNm'),
        'maxInputRpm':g.get('maxInputRpm') or g.get('ratedInputRpm'),
        'maxOutputRpm':None,'torqueConstantNmPerA':kt}
    for k in ('peakPhaseCurrentA','continuousPhaseCurrentA','dcBusV','baseSpeedFraction','peakDurationS',
              'motoringPowerW','brakingPowerW','regenPowerW','regenEnergyJ','regenAcceptance',
              'minClearanceMm','undersideOffsetMm','rideKpNPerM','rideKdNsPerM','rideTargetStepMm','rideTargetStepTimeS',
              'recoveryKpNPerM','recoveryKdNsPerM','holdKpNmPerRad','holdKdNms'):cfg[k]=a[k]
    if g.get('peakOutputNm') is None and g.get('continuousOutputNm') is None:flags.append('Gearbox torque rating missing; no hardware pass')
    usable=min(peak*n*eta,cfg['gearboxPeakNm']*belt)
    fraction=a[{'low':'lossLowFraction','medium':'lossMediumFraction','high':'lossHighFraction'}[a['lossScenario']]]
    fc=fraction*usable;b=fc/a['lossReferenceRadS']
    return dict(actuatorConfig=cfg,rotorInertiaKgM2=jm,gearboxInputInertiaKgM2=jg,
        gearboxOutputInertiaKgM2=jo,reflectedInertiaKgM2=n*n*(jm+jg)+jo,
        outputCoulombNm=fc,outputViscousNms=b,assumptionFlags=flags,
        ratingsKnown=g.get('peakOutputNm') is not None,
        motorMassKg=m.get('massKg'),gearboxMassKg=g.get('massKg'),
        continuousRatingKnown=m.get('continuousTorqueNm') is not None and g.get('continuousOutputNm') is not None)


def profile_model(project):
    from dynamic_model import Model
    if not isinstance(project,dict) or project.get('schema')!='kinefold/project-v3':raise ValueError('Capture a project-v3 design.')
    p=copy.deepcopy(project['params']);c=copy.deepcopy(project['solverConfig'])
    # This model is only a grounded smooth geometry/energy screen. Contact
    # refinement separately uses inputRise=0 and actual unilateral collisions.
    c['inputRiseMm']=min(10.,c['inputPlateauMm']/2)
    return Model(p,c)


def prepare_geometry(project,a):
    m=profile_model(project);p=m.p;count=100
    if abs(p['L2']-p['L3'])>1e-9 or abs(p['ra']/p['rb']-2)>1e-9:raise ValueError('Comparison requires equal-link 2:1 straight geometry.')
    qs=[m.lo+(m.hi-m.lo)*i/count for i in range(count+1)]
    M=m.total_mass;data=[]
    for q in qs:
        sites=m.floating_sites(q);cz=m.sites(q)['6'][0][1]
        h=p['rw']/1000-cz
        ug=p['g']*sum(p['m'+k]*(p['rw']/1000+v[0][1]) for k,v in sites.items())
        # Grounded screen assumes ideal rolling. Replace the source's locked
        # drive spin term with circle no-slip spin; actual contact may slip.
        J=m.coefficients(q)[0]-m.I['6']*m.K*m.K+m.I['6']*(m.sites(q)['6'][1][0]/(p['rw']/1000))**2
        Cprime=m.sites(q)['6'][1][1]
        comprime=sum(p['m'+k]*v[1][1] for k,v in sites.items())/M
        grav=p['g']*sum(p['m'+k]*v[1][1] for k,v in sites.items())
        spring=m.spring(q)
        data.append(dict(q=q,h=h,clearance=h-a['undersideOffsetMm']/1000,ug=ug,
            us=spring['energy'],spring=spring['torque'],J=J,comprime=comprime,
            Cprime=Cprime,gravity=grav))
    qstart=m.hi+a['landingOpenFraction']*(m.lo-m.hi)
    start=min(data,key=lambda d:abs(d['q']-qstart))
    # Use first physical bound, never grant stroke beyond the mechanical stop.
    qmax=m.hi-a['stopReserveDeg']*math.pi/180
    valid=[d for d in data if d['q']>=start['q'] and d['q']<=qmax and d['clearance']>=a['minClearanceMm']/1000]
    end=valid[-1] if valid else None
    return dict(model=m,totalMassKg=M,samples=data,landingStart=start,landingEnd=end,
        compressionStopClearanceMm=data[-1]['clearance']*1000,
        landingLimit='mechanical-stop-reserve' if end and end['q']>=qmax-(m.hi-m.lo)/count else 'minimum-clearance',
        alphaDeg=p['alpha'])


def fast_screen(geometry,hardware,a):
    c=hardware['actuatorConfig'];data=geometry['samples'];M=geometry['totalMassKg'];g=geometry['model'].p['g'];Jref=hardware['reflectedInertiaKgM2']
    fc=hardware['outputCoulombNm'];b=hardware['outputViscousNms'];end=geometry['landingEnd'];start=geometry['landingStart']
    if end and end['q']>start['q']:
        delta=end['q']-start['q'];drop=M*g*a['dropHeightMm']/1000
        energy=max(0.,drop+start['ug']-end['ug']+start['us']-end['us'])
        demand=energy/delta
        qd=math.sqrt(max(0.,2*drop/(start['J']+Jref)))
        cap=torque_limit(c,qd,-1e8)['actuatorAvailableNm']
        # Dissipative friction helps arrest in this necessary endpoint screen;
        # work varies with speed, so no full transient absorption claim follows.
        loss=(fc+b*qd)*delta
        capacity=cap*delta+loss
        landing=dict(status='screen-pass' if capacity>=energy else 'screen-fail',
            reason='Endpoint work/speed estimate; actual contact/arrest/hold must be refined.',
            metrics=dict(requiredJointNm=demand,availableJointNm=cap,energyRequiredJ=energy,
                estimatedAbsorptionJ=capacity,estimatedImpactHipRadS=qd,
                angularStrokeRad=delta,endClearanceMm=end['clearance']*1000,
                compressionStopClearanceMm=geometry['compressionStopClearanceMm'],
                physicalLimit=geometry['landingLimit'],allBodyDropEnergyJ=drop))
    else:landing=dict(status='screen-fail',reason='No compression stroke before requested clearance or physical stop.',metrics={})
    # Grounded energy-domain extension, including finite links and N² rotor.
    E=0.;elapsed=0.;stalled=False;maxspeed=0.;motorwork=0.;losswork=0.
    rev=list(reversed(data))
    for left,right in zip(rev,rev[1:]):
        dq=left['q']-right['q'];J=left['J']+Jref;speed=math.sqrt(max(0.,2*E/max(J,1e-12)))
        cap=torque_limit(c,-speed,-1e8,peak_elapsed_s=elapsed)['actuatorAvailableNm']
        drag=fc*math.tanh(speed/max(a['frictionSmoothingRadS']/(c['ratio']*c.get('hipBeltRatio',1)),1e-9))+b*speed
        Enew=E+cap*dq-(right['ug']-left['ug'])-(right['us']-left['us'])-drag*dq
        if Enew<=0:stalled=True;E=0.;break
        vs=math.sqrt(2*Enew/max(right['J']+Jref,1e-12));elapsed+=2*dq/max(speed+vs,1e-12)
        motorwork+=cap*dq;losswork+=drag*dq;E=Enew;maxspeed=max(maxspeed,vs)
    velocity=abs(data[0]['comprime'])*math.sqrt(2*E/(data[0]['J']+Jref)) if not stalled else 0.
    jumpheight=velocity*velocity/(2*g)*1000 if g else 0.
    jump=dict(status='screen-pass' if not stalled and jumpheight>=a['jumpHeightMm'] else 'screen-fail',
        reason='Grounded ideal-rolling full-stroke COM-energy estimate; unilateral takeoff, slip and internal flight dynamics require refinement.',
        metrics=dict(estimatedJumpHeightMm=jumpheight,targetHeightMm=a['jumpHeightMm'],strokeTimeS=elapsed,
            maxHipRadS=maxspeed,finalTotalKineticJ=E,motorWorkJ=motorwork,lossWorkJ=losswork,
            reflectedInertiaKgM2=Jref,stalled=stalled))
    holds=[abs(d['gravity']-d['spring']) for d in data]
    static=max(holds);available=torque_limit(c,0.,static)['actuatorAvailableNm']
    terrain=dict(status='screen-pass' if available>=static else 'screen-fail',
        reason='Necessary static support through travel only; sharp terrain peaks and tracking are assessed dynamically.',
        metrics=dict(maxStaticHoldNm=static,availableAtRestNm=available,marginNm=available-static))
    return dict(landing=landing,jump=jump,terrain=terrain)


def enumerate_candidates(catalog,geometry,a,selection=None):
    selection=selection or {};mids=selection.get('motorIds',[]);gids=selection.get('gearboxIds',[])
    for ids,key in ((mids,'motors'),(gids,'gearboxes')):
        if not isinstance(ids,list) or len(ids)>200 or any(not isinstance(x,str) for x in ids):raise ValueError('Invalid catalog selection.')
        if set(ids)-{v['id'] for v in catalog[key]}:raise ValueError('Unknown exact catalog ID.')
    rows=[]
    for m in catalog['motors']:
        if mids and m['id'] not in mids:continue
        for g in catalog['gearboxes']:
            if gids and g['id'] not in gids:continue
            row=dict(id=m['id']+'__'+g['id'],motorId=m['id'],gearboxId=g['id'],motorName=m['name'],
                gearboxName=g['name'],ratio=g['ratio'],massKg=None,rank=None,
                analytical={k:dict(status='not-run',reason='Outside completed finite shortlist.',metrics={}) for k in CASES},
                pymunk={k:dict(status='not-run',reason='Outside completed Pymunk cross-check.',metrics={}) for k in CASES})
            try:
                hw=candidate_hardware(m,g,a);row['hardware']=hw;row['screen']=fast_screen(geometry,hw,a)
                if hw['motorMassKg'] is not None and hw['gearboxMassKg'] is not None:row['massKg']=hw['motorMassKg']+hw['gearboxMassKg']
                row['status']='screen-only';row['assumptionFlags']=hw['assumptionFlags']
            except (ValueError,TypeError,ArithmeticError) as e:
                row['screen']={k:dict(status='unknown',reason=str(e),metrics={}) for k in CASES};row['status']='unknown'
            rows.append(row)
    rank_candidates(rows)
    return rows


def rank_candidates(rows):
    def hard_group(row):
        actual=[v for engine in ('analytical','pymunk') for v in row[engine].values() if v['status']!='not-run']
        if any(v['status']=='fail' for v in actual):return 5
        if any(v['status']=='numeric-failure' for v in actual):return 6
        if any(v['status']=='unknown' for v in actual):return 4
        if len(actual)==6 and all(v['status']=='pass' for v in actual):return 0
        if len(actual)==3 and all(v['status']=='pass' for v in actual):return 1
        if all(v['status']=='screen-pass' for v in row['screen'].values()):return 2
        if any(v['status']=='unknown' for v in row['screen'].values()):return 7
        return 3
    # A true nondominated set among the best available hard-feasibility class:
    # known lower mass, lower reflected inertia and larger usable torque.
    # Missing mass cannot be represented by a fictitious zero.
    for row in rows:row['paretoFront']=None if row.get('massKg') is None else False
    if rows:
        best=min(hard_group(r) for r in rows)
        comparable=[r for r in rows if hard_group(r)==best and r.get('massKg') is not None and 'hardware' in r]
        def objective(r):
            hw=r['hardware'];c=hw['actuatorConfig']
            return (r['massKg'],hw['reflectedInertiaKgM2'],-torque_limit(c,0.,1e8)['actuatorAvailableNm'])
        objectives=[objective(r) for r in comparable]
        for i,row in enumerate(comparable):
            this=objectives[i]
            row['paretoFront']=not any(all(x<=y for x,y in zip(other,this)) and any(x<y for x,y in zip(other,this)) for j,other in enumerate(objectives) if j!=i)
    def quality(row):
        # Failures precede mass ranking. Unknown is never counted as passing.
        screens=row['screen'];fails=sum(v['status']=='screen-fail' for v in screens.values())
        unknown=sum(v['status']=='unknown' for v in screens.values())
        actual=[v for engine in ('analytical','pymunk') for v in row[engine].values() if v['status']!='not-run']
        dfail=sum(v['status']=='fail' for v in actual);dunknown=sum(v['status'] in ('unknown','numeric-failure') for v in actual)
        landing=screens['landing'].get('metrics',{});jump=screens['jump'].get('metrics',{})
        lmargin=landing.get('estimatedAbsorptionJ',0)/max(landing.get('energyRequiredJ',1),1e-6)
        jmargin=jump.get('estimatedJumpHeightMm',0)/max(jump.get('targetHeightMm',1),1e-6)
        return (hard_group(row),fails,unknown,-min(lmargin,jmargin),
            0 if row.get('paretoFront') is True else 1,
            row['massKg'] if row['massKg'] is not None else 1e9,row['id'])
    ordered=sorted(rows,key=quality)
    for rank,row in enumerate(ordered,1):row['rank']=rank
    return ordered


def contact_payload(project,hardware,a,kind,engine):
    from contact_cases import CASE_DEFAULTS
    from motor_model import DEFAULTS
    c=copy.deepcopy(project['solverConfig']);c.update(inputRiseMm=0.,dt=a['dynamicDt'],
        duration=a['dynamicDurationS'],outputHz=a['dynamicOutputHz'],initialVelocityDegS=0.,hipTorqueNm=0.)
    c['hipRotorInertiaKgM2']+=hardware['gearboxOutputInertiaKgM2']
    base_n=hardware['actuatorConfig']['ratio'];belt=hardware['actuatorConfig'].get('hipBeltRatio',1);n=base_n*belt
    motor={**DEFAULTS,'enabled':True,'gearRatio':base_n,'hipBeltRatio':belt,'rotorInertiaKgM2':hardware['rotorInertiaKgM2'],
        'gearboxInputInertiaKgM2':hardware['gearboxInputInertiaKgM2'],
        'coulombFrictionNm':hardware['outputCoulombNm']/n,
        'viscousFrictionNms':hardware['outputViscousNms']/n**2,
        'frictionVelocityScaleRadS':a['frictionSmoothingRadS']}
    case={**CASE_DEFAULTS,'kind':'terrain-stability' if kind=='terrain' else kind,
        'landingDropMm':a['dropHeightMm'],'landingOpenFraction':a['landingOpenFraction'],
        'undersideOffsetMm':a['undersideOffsetMm'],'energyMethod':False}
    payload=dict(engine=engine,params=copy.deepcopy(project['params']),runConfig=c,
        motorConfig=motor,contactConfig={**project.get('contactConfig',{}),'mode':'terrain-contact',
            'friction':project.get('contactConfig',{}).get('friction',.8),'restitution':0,'drive':'free'},
        caseConfig=case,actuatorConfig=copy.deepcopy(hardware['actuatorConfig']))
    if project.get('terrainConfig'):payload['terrainConfig']=copy.deepcopy(project['terrainConfig'])
    return payload


def dynamic_metrics(result,a,kind):
    rows=result['rows'];events=result.get('events',[]);metrics=dict(result.get('caseMetrics',{}));diag=result.get('diagnostics',{})
    if not rows:raise ValueError('Empty dynamic result.')
    first=rows[0];duration=rows[-1]['t']-first['t']
    def rms(key):
        samples=[(r['t'],r.get(key)) for r in rows]
        pairs=[(t,v) for t,v in samples if isinstance(v,(float,int)) and math.isfinite(v)]
        if len(pairs)<2 or duration<=0:return None
        return math.sqrt(sum((t1-t0)*(v0*v0+v1*v1)/2 for (t0,v0),(t1,v1) in zip(pairs,pairs[1:]))/duration)
    contact=sum(max(0,r1['t']-r0['t'])*(1 if r0.get('contactCount',0)>0 else 0) for r0,r1 in zip(rows,rows[1:]))/max(duration,1e-12)
    def peak(key):return max((abs(r[key]) for r in rows if isinstance(r.get(key),(int,float)) and math.isfinite(r[key])),default=None)
    accel_rms=rms('chassisAccelerationMmS2')
    accel_peak=peak('chassisAccelerationMmS2')
    accel_basis='returned chassis acceleration samples'
    if accel_rms is None:
        intervals=[]
        for left,right in zip(rows,rows[1:]):
            dt=right['t']-left['t'];a0=left.get('chassisVelocityMmS');a1=right.get('chassisVelocityMmS')
            if dt>1e-10 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in (a0,a1)):
                intervals.append((dt,(a1-a0)/dt))
        if intervals:
            accel_rms=math.sqrt(sum(dt*a*a for dt,a in intervals)/sum(dt for dt,a in intervals))
            accel_peak=max(abs(a) for _,a in intervals)
            accel_basis='output-interval finite difference of actual chassis velocity; impulsive peaks unresolved'
    target=first['chassisZMm']
    terrain=result.get('terrainConfig') or result.get('snapshot',{}).get('terrainConfig') or {}
    grade=terrain.get('gradePercent',0)/100 if kind=='terrain' else 0.
    speed=result.get('runConfig',{}).get('inputSpeedMmS',0)
    metrics.update(rmsShaftTorqueNm=rms('shaftCommandNm'),
        peakShaftTorqueNm=max(abs(r.get('shaftCommandNm',0)) for r in rows),
        rmsPhaseCurrentA=rms('phaseCurrentA'),peakPhaseCurrentA=max((abs(r['phaseCurrentA']) for r in rows if isinstance(r.get('phaseCurrentA'),(int,float))),default=None),
        peakJointTorqueNm=max(abs(r.get('motorTorqueNm',0)) for r in rows),
        rmsJointTorqueNm=rms('motorTorqueNm'),peakShaftPowerW=peak('shaftMechanicalPowerW'),
        peakBodyAccelerationMS2=accel_peak/1000 if accel_peak is not None else None,
        rmsHeightErrorMm=math.sqrt(sum((r['chassisZMm']-r.get('rideTargetHeightMm',target+grade*speed*r['t']))**2 for r in rows)/len(rows)),
        rmsBodyAccelerationMS2=accel_rms/1000 if accel_rms is not None else None,
        accelerationBasis=accel_basis if accel_rms is not None else 'unavailable',
        contactFraction=contact,durationS=duration,
        maxEnergyResidualJ=max(abs(r.get('energyBalanceResidualJ',0)) for r in rows),
        termination=diag.get('termination'),maxPenetrationMm=diag.get('maxPenetrationMm'))
    qlo=result['params']['te'];qhi=result['params']['tc']
    metrics['minTravelReserveDeg']=min(min(r['theta2']-qlo,qhi-r['theta2']) for r in rows)
    cfg=result.get('actuatorConfig') or result.get('snapshot',{}).get('actuatorConfig',{})
    metrics['maxSampledShaftRpm']=peak('shaftRpm')
    metrics['maxSampledOutputRpm']=peak('shaftRpm')/cfg['ratio'] if peak('shaftRpm') is not None and cfg.get('ratio') else None
    metrics['sourceSpeedLimitExceeded']=bool(
        cfg.get('maxInputRpm') is not None and metrics['maxSampledShaftRpm'] is not None and metrics['maxSampledShaftRpm']>cfg['maxInputRpm']+1e-6 or
        cfg.get('maxOutputRpm') is not None and metrics['maxSampledOutputRpm'] is not None and metrics['maxSampledOutputRpm']>cfg['maxOutputRpm']+1e-6)
    cont=cfg.get('continuousShaftNm')
    metrics['thermalTorqueRatio']=metrics['rmsShaftTorqueNm']/cont if cont and metrics['rmsShaftTorqueNm'] is not None else None
    termination=diag.get('termination','')
    numeric=any(x in termination for x in ('penetration','diverge','numeric'))
    if numeric:return dict(status='numeric-failure',reason='Numerical contact/constraint guard reached; refine dt.',metrics=metrics)
    if metrics['sourceSpeedLimitExceeded']:
        return dict(status='fail',reason='Observed shaft/output speed exceeded a known exact-SKU limit; zero drive torque cannot prevent external backdrive overspeed.',metrics=metrics)
    if kind=='landing':
        arrest=next((e for e in events if e['type']=='chassis-arrest'),None)
        stop=next((e for e in events if e['type']=='compression-stop'),None)
        clearance=metrics.get('minimumUndersideClearanceMm')
        held=bool(arrest) and rows[-1]['t']-arrest['t']>=a['postArrestHoldS']
        metrics['postArrestObservedS']=rows[-1]['t']-arrest['t'] if arrest else None
        passed=bool(arrest) and held and stop is None and clearance is not None and clearance>=a['minClearanceMm'] and termination=='duration'
        status='pass' if passed else 'fail' if stop or termination=='underside-contact' or clearance is not None and clearance<a['minClearanceMm'] else 'unknown'
        reason='Arrest, full observed post-arrest hold, clearance and physical-stop order assessed.' if status!='unknown' else 'Observation ended before a decisive arrest/failure.'
    elif kind=='jump':
        obs=result.get('targetObservations',{});height=metrics.get('jumpComRiseMm')
        if height is None:height=obs.get('jumpComRiseMm')
        metrics['jumpComRiseMm']=height
        status='pass' if height is not None and height>=a['jumpHeightMm'] else 'fail' if height is not None else 'unknown'
        reason='Actual all-body COM apex above first takeoff; rotor/internal KE excluded from flight height.' if height is not None else 'No completed first-flight COM apex in observation.'
    else:
        clearance=metrics.get('minimumUndersideClearanceMm')
        done=termination=='duration'
        assessed=metrics['rmsBodyAccelerationMS2'] is not None and clearance is not None
        passed=done and assessed and metrics['rmsHeightErrorMm']<=a['terrainMaxRmsErrorMm'] and metrics['rmsBodyAccelerationMS2']<=a['terrainMaxBodyAccelMS2'] and contact>=a['terrainMinContactFraction'] and metrics['minTravelReserveDeg']>=a['terrainMinTravelReserveDeg'] and clearance>=a['minClearanceMm']
        status='pass' if passed else 'fail' if assessed and done or 'stop' in termination or termination=='underside-contact' else 'unknown'
        reason='Captured terrain, common ride-height controller and editable quarter-model thresholds.'
    return dict(status=status,reason=reason,metrics=metrics)


def atomic_json(path,value):
    path=Path(path);tmp=path.with_suffix('.tmp');tmp.write_text(canonical(value),encoding='utf-8');tmp.replace(path)


def run_comparison(request,output,*,progress=None,simulators=None):
    if (request.get('project') or {}).get('solverConfig',{}).get('fixture')=='pinned-chassis':
        raise ValueError('All-case actuator comparison requires a floating chassis; use the separate pinned terrain diagnostic for pin-force measurements.')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    a=validate_assumptions(request.get('assumptions'));budget=validate_budget(request.get('budget'))
    project=copy.deepcopy(request.get('project') or json.loads((ROOT/'saved-configurations/vsl-v45-nominal-alpha0.json').read_text(encoding='utf-8')))
    catalog=load_catalog();geometry=prepare_geometry(project,a);start=time.monotonic()
    identity=dict(projectId=project.get('id'),projectName=project.get('name'),projectHash=digest(project),
        catalogRevision=catalog['revision'],catalogHash=digest(catalog),assumptionsHash=digest(a),
        quarterModel=True,alphaDeg=project['params']['alpha'],massesKg={k:project['params'][k] for k in ('m1','m2','m3','m5','m6')})
    identity['captureHash']=digest(dict(project=project,assumptions=a,budget=budget,catalog=catalog['revision']))
    import platform
    from importlib.metadata import version,PackageNotFoundError
    identity['pythonVersion']=platform.python_version()
    identity['packageVersions']={}
    for name in ('numpy','scipy','pymunk'):
        try:identity['packageVersions'][name]=version(name)
        except PackageNotFoundError:identity['packageVersions'][name]=None
    identity['sourceSHA256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        for name in ('actuator_comparison.py','actuation_limits.py','dynamic_model.py','motor_model.py',
            'contact_cases.py','analytical_contact.py','contact_dynamics.py','finite_contact_model.py',
            'finite_pymunk_contact.py','terrain_profiles.py') if (ROOT/name).is_file()}
    def update(stage,completed,total,message):
        state=dict(stage=stage,completed=completed,total=total,progress=completed/max(total,1),message=message,elapsedSeconds=time.monotonic()-start)
        atomic_json(output/'progress.json',state)
        if progress:progress(state)
    update('screen',0,1,'Screening exact catalog combinations')
    rows=enumerate_candidates(catalog,geometry,a,request.get('selection'))
    ordered=rank_candidates(rows);eligible=[r for r in ordered if 'hardware' in r]
    selected=eligible[:budget['analyticalCandidates']];cross=selected[:budget['pymunkCandidates']]
    result=dict(schema='kinefold/automatic-actuator-comparison-v1',identity=identity,project=project,
        assumptions=a,budget=budget,missingMetrics=missing_metrics(catalog),candidates=rows,
        shortlist=[r['id'] for r in selected],summary={},warnings=[
            'All results conditional on editable missing-data assumptions; hardware compatibility and thermal life unverified.',
            'Screen estimates are not dynamic passes. Unrun cases remain not-run.',
            'Single floating-chassis quarter model; no roll, pitch or four-leg stability.',
            'Saved masses, alpha and original spring are preserved; motor/gear mass is reported, not added to the captured chassis mass.'])
    atomic_json(output/'result.json',result)
    total=3*(len(selected)+len(cross));done=0
    if simulators is None and total:
        from analytical_contact import simulate_contact as analytical
        from contact_dynamics import simulate_contact as pymunk
        simulators=dict(analytical=analytical,pymunk=pymunk)
    # Complete both engines for the crosscheck rows early, so a bounded or
    # cancelled job still contains paired evidence rather than only one engine.
    schedule=[(engine,row) for row in selected for engine in ('analytical','pymunk')
        if engine=='analytical' or row in cross]
    for engine,row in schedule:
        for kind in CASES:
            if time.monotonic()-start>budget['maxSeconds']:
                result['warnings'].append('Finite refinement stopped at wall-time budget; remaining cases unrun.')
                result['summary']['budgetExpired']=True;break
            update('finite-'+engine,done,total,f"{engine}: {row['motorName']} / {row['gearboxName']} / {kind}")
            payload=contact_payload(project,row['hardware'],a,kind,engine)
            try:
                actual=simulators[engine](payload)
                case=dynamic_metrics(actual,a,kind);row[engine][kind]=case
                # Retain complete actual case in bounded separate detail files.
                path=output/(digest(row['id'])[:20]+'-'+engine+'-'+kind+'.json')
                atomic_json(path,dict(candidateId=row['id'],engine=engine,kind=kind,payload=payload,result=actual,assessment=case))
            except Exception as error:
                row[engine][kind]=dict(status='numeric-failure',reason=str(error)[:1200],metrics={})
            done+=1;atomic_json(output/'result.json',result)
        if result['summary'].get('budgetExpired'):break
    for row in rows:
        actual=[v for engine in ('analytical','pymunk') for v in row[engine].values()]
        ran=[v for v in actual if v['status']!='not-run']
        row['status']='dynamic-fail' if any(v['status']=='fail' for v in ran) else 'numeric-failure' if any(v['status']=='numeric-failure' for v in ran) else 'conditional-dynamic-pass' if len(ran)==6 and all(v['status']=='pass' for v in ran) else 'partially-refined' if ran else row['status']
    ordered=rank_candidates(rows)
    result['summary'].update(candidateCount=len(rows),screenedCount=len(rows),actualCaseCount=done,
        conditionalDynamicPassCount=sum(r['status']=='conditional-dynamic-pass' for r in rows),
        screenAllCasesPassCount=sum(all(v['status']=='screen-pass' for v in r['screen'].values()) for r in rows),
        ranking='Hard dynamic failures / indeterminate / screen failures precede balanced endpoint margins and known mass; not a global optimum.',
        recommendedForInspection=[r['id'] for r in ordered[:8]],elapsedSeconds=time.monotonic()-start)
    atomic_json(output/'result.json',result);update('complete',done,max(total,done),'Comparison complete; inspect conditional assumptions and per-case outcomes.')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--request',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    try:run_comparison(json.loads(args.request.read_text(encoding='utf-8')),args.output)
    except Exception as error:
        args.output.mkdir(parents=True,exist_ok=True);atomic_json(args.output/'error.json',dict(error=str(error)[:2000]));raise


if __name__=='__main__':main()
