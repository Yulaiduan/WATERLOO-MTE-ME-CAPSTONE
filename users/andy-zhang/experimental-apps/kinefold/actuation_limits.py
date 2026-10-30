"""Bounded four-quadrant actuator and quarter-leg comparison controllers.

Import validate_actuator_config/ActuatorController from contact_cases; run
verify_actuator_comparison.py for checks. Inputs are SI joint radians, seconds,
Nm, W and captured numeric motor/gear assumptions. Outputs actual delivered
joint torque and separate shaft/electrical/loss diagnostics. This approximate
current/torque plateau and linear speed rolloff is not a measured motor map;
constant Coulomb detent is a worst-case dissipative proxy, not periodic cogging.
"""
import math


ACTUATOR_DEFAULTS = dict(schema='kinefold/actuator-limits-v1',ratio=1.,hipBeltRatio=1.,peakShaftNm=1.,
    continuousShaftNm=None,peakDurationS=2.,noLoadRpm=6000.,baseSpeedFraction=.5,
    forwardEfficiency=.9,reverseEfficiency=.9,gearboxPeakNm=10000.,gearboxContinuousNm=None,
    maxInputRpm=None,maxOutputRpm=None,torqueConstantNmPerA=None,peakPhaseCurrentA=None,
    continuousPhaseCurrentA=None,dcBusV=48.,motoringPowerW=5000.,brakingPowerW=5000.,
    regenPowerW=5000.,regenEnergyJ=5000.,regenAcceptance=True,
    minClearanceMm=50.,undersideOffsetMm=50.,rideKpNPerM=5000.,rideKdNsPerM=350.,
    recoveryKpNPerM=3000.,recoveryKdNsPerM=300.,holdKpNmPerRad=120.,holdKdNms=15.)


def validate_actuator_config(raw=None):
    if raw is None:return None
    if not isinstance(raw,dict) or not set(ACTUATOR_DEFAULTS)-{'hipBeltRatio'} <= set(raw) <= set(ACTUATOR_DEFAULTS):
        raise ValueError('actuatorConfig requires exactly '+', '.join(ACTUATOR_DEFAULTS))
    c=dict(raw)
    if c['schema']!=ACTUATOR_DEFAULTS['schema'] or type(c['regenAcceptance']) is not bool:
        raise ValueError('Invalid actuator schema or regenAcceptance.')
    nullable={'continuousShaftNm','gearboxContinuousNm','maxInputRpm','maxOutputRpm',
              'torqueConstantNmPerA','peakPhaseCurrentA','continuousPhaseCurrentA'}
    for key,value in c.items():
        if key in ('schema','regenAcceptance'):continue
        if key in nullable and value is None:continue
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=1e8:
            raise ValueError('Actuator '+key+' must be finite/nonnegative or documented null.')
    if not 1e-6<=c['ratio']<=10000 or c['peakShaftNm']<=0 or c['noLoadRpm']<=0:
        raise ValueError('Actuator ratio, peak shaft torque and no-load speed must be positive.')
    if not 1<=c.get('hipBeltRatio',1)<=3:raise ValueError('hipBeltRatio must be within [1,3].')
    for key in ('forwardEfficiency','reverseEfficiency'):
        if not .01<=c[key]<=1:raise ValueError(key+' must be in [.01,1].')
    if not .01<=c['baseSpeedFraction']<1:raise ValueError('baseSpeedFraction must be in [.01,1).')
    return c


def torque_limit(config,qd,requested_joint_nm,*,peak_elapsed_s=0.,regen_used_j=0.,dt_s=0.):
    """Clip delivered torque, respecting sign-dependent shaft/joint power flow.

    Motoring: joint = eta_forward*N*shaft. Backdrive braking: shaft =
    eta_reverse*joint/N. At rest use conservative forward conversion. Mechanical
    shaft power is only an electrical-power proxy (no copper-loss motor model).
    """
    c=config;belt=c.get('hipBeltRatio',1);n=c['ratio']*belt;speed=abs(qd*n);rpm=speed*30/math.pi
    gearbox_rpm=abs(qd)*belt*30/math.pi
    braking=requested_joint_nm*qd<0
    eta=c['reverseEfficiency'] if braking else c['forwardEfficiency']
    conversion=n/eta if braking else n*eta
    shaft_peak=c['peakShaftNm']
    kt=c['torqueConstantNmPerA'];current=c['peakPhaseCurrentA']
    if kt is not None and current is not None:shaft_peak=min(shaft_peak,kt*current)
    continuous=c['continuousShaftNm']
    if kt is not None and c['continuousPhaseCurrentA'] is not None:
        icap=kt*c['continuousPhaseCurrentA'];continuous=min(continuous,icap) if continuous is not None else icap
    if peak_elapsed_s>=c['peakDurationS'] and continuous is not None:shaft_peak=min(shaft_peak,continuous)
    base=c['noLoadRpm']*c['baseSpeedFraction']
    speed_factor=max(0.,min(1.,(c['noLoadRpm']-rpm)/(c['noLoadRpm']-base)))
    shaft_available=shaft_peak*speed_factor
    if c['maxInputRpm'] is not None and rpm>c['maxInputRpm']:shaft_available=0.
    if c['maxOutputRpm'] is not None and gearbox_rpm>c['maxOutputRpm']:shaft_available=0.
    power=c['brakingPowerW'] if braking else c['motoringPowerW']
    if braking:
        power=min(power,c['regenPowerW'])
        if not c['regenAcceptance'] or regen_used_j>=c['regenEnergyJ']:power=0.
        elif dt_s>0:power=min(power,max(0.,c['regenEnergyJ']-regen_used_j)/dt_s)
    if speed>1e-12:shaft_available=min(shaft_available,power/speed)
    elif braking:shaft_available=0.
    joint_available=min(c['gearboxPeakNm']*belt,shaft_available*conversion)
    if peak_elapsed_s>=c['peakDurationS'] and c['gearboxContinuousNm'] is not None:
        joint_available=min(joint_available,c['gearboxContinuousNm']*belt)
    actual=math.copysign(min(abs(requested_joint_nm),joint_available),requested_joint_nm)
    shaft=actual/conversion
    joint_power=actual*qd;shaft_power=shaft*n*qd
    loss=max(0.,shaft_power-joint_power) if not braking else max(0.,-joint_power+shaft_power)
    return dict(motorTorqueNm=actual,shaftCommandNm=shaft,
        actuatorRequestedNm=requested_joint_nm,actuatorAvailableNm=joint_available,
        actuatorLimited=abs(actual-requested_joint_nm)>1e-8,
        actuatorMode='braking' if braking else 'motoring-or-hold',
        shaftMechanicalPowerW=shaft_power,jointMechanicalPowerW=joint_power,
        gearboxLossPowerW=loss,regenPowerW=max(0.,-shaft_power),
        phaseCurrentA=abs(shaft)/kt if kt else None,shaftRpm=rpm,
        gearboxOutputRpm=gearbox_rpm,gearboxOutputTorqueNm=actual/belt,totalReduction=n,
        peakTimeUsedS=peak_elapsed_s,regenEnergyUsedJ=regen_used_j)


class ActuatorController:
    """Same bounded policy for both engines, using actual chassis state."""
    def __init__(self,m,case,config):
        self.m=m;self.case=case;self.config=validate_actuator_config(config)
        self.contacted=False;self.recovered=False;self.extended=False
        self.last_time=None;self.previous=None;self.peak_elapsed=0.;self.regen_used=0.
        self.q_start=m.hi if case['kind']=='jump' else m.hi+case['landingOpenFraction']*(m.lo-m.hi) if case['kind']=='landing' else m.q0
        self.target_h=m.p['rw']/1000-m.sites(self.q_start)['6'][0][1]
        terrain=getattr(m,'terrain_config',None) or {}
        self.grade=terrain.get('gradePercent',0.)/100 if case['kind']=='terrain-stability' else 0.
        self.target_h+=m.p['rw']/1000*(math.sqrt(1+self.grade*self.grade)-1)
        self.target_v=self.grade*m.c['inputSpeedMmS']/1000

    def command(self,q,qd,contacted=False,*,time=0.,state=None):
        m=self.m;c=self.config;state=state or {};target_h=self.target_h+self.target_v*time
        h=state.get('h',target_h);vh=state.get('vh',0.)
        if self.last_time is not None and time>self.last_time and self.previous:
            dt=time-self.last_time
            cont=c['continuousShaftNm']
            if cont is None or abs(self.previous['shaftCommandNm'])>cont:self.peak_elapsed+=dt
            self.regen_used+=self.previous['regenPowerW']*dt
        self.last_time=time
        self.contacted=self.contacted or bool(contacted)
        passive=m.motor.motor_state(q,qd,0)['jointPassiveNm']
        spring=m.spring(q)['torque'];damping=m.c['dampingNms']*qd
        Czprime=m.sites(q)['6'][1][1]
        if hasattr(m,'grounded_gravity'):gravity=m.grounded_gravity(q)
        else:
            sites=m.sites(q);M=sum(m.p['m'+k] for k in ('1','2','3','5','6'))
            gravity=m.p['g']*(sum(m.p['m'+k]*sites[k][1][1] for k in ('2','3','5','6'))-M*Czprime)
        hold=gravity-spring-passive+damping
        kind=self.case['kind']
        if kind=='jump':
            self.extended=self.extended or q<=m.lo+1e-6
            lost_contact=self.contacted and not contacted
            request=0. if self.extended or lost_contact else -1e8
            phase='jump-coast' if request==0 else 'jump-max-extension'
        elif kind=='landing' and not self.contacted:
            request=-spring-passive+damping+c['holdKpNmPerRad']*(self.q_start-q)-c['holdKdNms']*qd
            phase='airborne-bounded-hold'
        elif kind=='landing' and not self.recovered:
            self.recovered=vh>=-.01 and time>0
            request=-1e8 if not self.recovered and qd>0 else hold
            phase='landing-max-brake' if not self.recovered else 'landing-recovery'
        else:request=hold;phase='landing-recovery' if kind=='landing' else 'terrain-ride-height'
        if kind=='terrain-stability' or (kind=='landing' and self.recovered):
            kp=c['recoveryKpNPerM'] if kind=='landing' else c['rideKpNPerM']
            kd=c['recoveryKdNsPerM'] if kind=='landing' else c['rideKdNsPerM']
            request=hold-Czprime*(kp*(target_h-h)-kd*(vh-self.target_v))
        bounded=torque_limit(c,qd,request,peak_elapsed_s=self.peak_elapsed,regen_used_j=self.regen_used,dt_s=m.c['dt'])
        # Delivered work belongs in the mechanical ledger. Transmission losses
        # remain a separate electrical-sizing diagnostic, avoiding double count.
        ms=m.motor.motor_state(q,qd,bounded['motorTorqueNm'])
        ms.pop('rotorKineticJ',None);ms.pop('coggingPotentialJ',None)
        ms.update(bounded);ms.update(holdTorqueNm=bounded['motorTorqueNm'] if 'hold' in phase else 0.,
            brakeTorqueNm=bounded['motorTorqueNm'] if 'brake' in phase else 0.,controllerPhase=phase,
            rideTargetHeightMm=target_h*1000,rideTargetVelocityMmS=self.target_v*1000)
        self.previous=bounded
        return ms
