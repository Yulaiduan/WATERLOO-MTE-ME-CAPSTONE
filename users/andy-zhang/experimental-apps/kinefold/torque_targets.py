"""Observe and size jump/landing targets with independent supplied integrators.

Imported by contact engines/study; inputs SI step states, saved target mm/Nm.
Outputs step-resolved first-flight/first-arrest observations and bounded tested
torque brackets. Does not apply forces, interpolate output rows, or certify a
global minimum, later landing safety, hardware peaks, or an unobserved apex.
"""
import copy
import math

TARGET_DEFAULTS = dict(jumpHeightMm=100., landingClearanceMm=50., jumpTorqueLimitNm=200.)


def resolve_targets(raw=None):
    if raw is None:
        return dict(TARGET_DEFAULTS)
    if not isinstance(raw, dict) or set(raw) != set(TARGET_DEFAULTS):
        raise ValueError('Torque targets require exactly ' + ', '.join(TARGET_DEFAULTS))
    for key, value in raw.items():
        maximum = 10000 if key == 'jumpTorqueLimitNm' else 5000
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= maximum:
            raise ValueError(key + ' must be finite from 0 to ' + str(maximum) + '.')
    return dict(raw)


class TargetObservation:
    """Step-level observations independent of export sample frequency."""
    def __init__(self, case, dt):
        self.case, self.dt = case, dt
        self.contacted = False
        self.takeoff = self.apex = self.recontact = None
        self.maximum_gap_mm = 0.
        self.minimum_clearance_mm = None
        self.arrest_time = None

    def step(self, t, h, vh, wheel_z, wheel_vz, radius, active, events):
        gap = (wheel_z - radius) * 1000
        if self.case['kind'] == 'jump':
            if active:
                if self.takeoff is not None and self.apex is None and self.recontact is None:
                    self.recontact = t
                self.contacted = True
            if self.contacted and self.takeoff is None and not active and gap > .0001 and wheel_vz > 0 and vh > 0:
                self.takeoff = dict(t=t, chassisZMm=h*1000)
            if self.takeoff is not None and self.recontact is None and self.apex is None:
                self.maximum_gap_mm = max(self.maximum_gap_mm, gap)
                if self.apex is None and vh <= 0:
                    self.apex = dict(t=t, chassisZMm=h*1000)
        elif self.case['kind'] == 'landing':
            self.contacted = self.contacted or active
            if self.contacted and self.arrest_time is None:
                offset = self.case['undersideOffsetMm']
                if offset is not None:
                    clearance = h*1000-offset
                    self.minimum_clearance_mm = clearance if self.minimum_clearance_mm is None else min(self.minimum_clearance_mm, clearance)
                arrest = next((e for e in events if e['type'] == 'chassis-arrest'), None)
                if arrest is not None:
                    self.arrest_time = arrest['t']

    def jump_finished(self):
        return self.apex is not None or self.recontact is not None

    def result(self):
        genuine = bool(self.takeoff and self.apex and self.recontact is None and
                       self.apex['t']-self.takeoff['t'] >= 2*self.dt and self.maximum_gap_mm > .01)
        return dict(takeoff=self.takeoff, firstFlightApex=self.apex, recontactBeforeApexTimeS=self.recontact,
                    genuineFirstFlight=genuine, flightRiseMm=self.apex['chassisZMm']-self.takeoff['chassisZMm'] if genuine else None,
                    maximumFirstFlightGapMm=self.maximum_gap_mm, minimumClearanceThroughArrestMm=self.minimum_clearance_mm,
                    firstArrestTimeS=self.arrest_time, sampling='Every integration step, not decimated rows; output sample boundaries can change numerical substeps')


def target_torque_search(payload, simulate, iterations=5):
    """Coarse bounded scan/local refinement; solver failures are indeterminate."""
    from contact_cases import resolve_case
    from motor_model import Motor
    case = resolve_case(payload)
    if case['kind'] not in ('jump', 'landing'):
        raise ValueError('Choose Jump or Landing before sizing torque.')
    if 'torqueTargetConfig' in payload and payload['torqueTargetConfig'] is None:
        raise ValueError('Explicit torqueTargetConfig must be an object; omit it for defaults.')
    targets = resolve_targets(payload.get('torqueTargetConfig'))
    if case['kind'] == 'landing' and case['undersideOffsetMm'] is None:
        raise ValueError('Landing clearance sizing requires an explicit underside offset below hip A.')
    motor = Motor.resolve(payload.get('motorConfig'))
    limit = targets['jumpTorqueLimitNm'] if case['kind'] == 'jump' else case['landingBrakeLimitNm']
    request_base = {k: v for k, v in payload.items() if k not in ('study', 'torqueTargetConfig')}
    trials = []

    def trial(torque):
        request = copy.deepcopy(request_base)
        request['caseConfig'] = {**case, 'brakeStrategy': 'entered',
                                ('jumpTorqueNm' if case['kind'] == 'jump' else 'landingBrakeTorqueNm'): torque}
        try:
            result = simulate(request)
            observation = result.get('targetObservations', {})
            termination = result.get('diagnostics', {}).get('termination')
            metrics = result.get('caseMetrics', {})
            numerical = termination not in ('duration', 'assessment-outcome', 'underside-contact')
            if case['kind'] == 'jump':
                observed = observation.get('genuineFirstFlight', False)
                achieved = observation.get('flightRiseMm')
                success = bool(observed and achieved >= targets['jumpHeightMm'])
                complete = bool(observed or observation.get('recontactBeforeApexTimeS') is not None)
                outcome = 'target-reached' if success else 'below-target' if observed else 'recontact-before-apex' if complete else 'unobserved-apex-or-takeoff'
            else:
                achieved = observation.get('minimumClearanceThroughArrestMm')
                observed = bool(metrics.get('landingSuccess'))
                success = bool(observed and achieved is not None and achieved >= targets['landingClearanceMm'])
                complete = bool(observed or metrics.get('outcome') in ('bottom-out-before-arrest', 'underside-contact'))
                outcome = 'arrested-above-target' if success else 'clearance-target-missed' if observed else metrics.get('outcome', 'unobserved-arrest')
            status = 'numerical-failure' if numerical else 'passing' if success else 'failed-target' if complete else 'insufficient-duration'
            trials.append(dict(torqueNm=torque, success=success if not numerical else False,
                               status=status, outcome=outcome, achievedMm=achieved, termination=termination,
                               firstArrestTimeS=observation.get('firstArrestTimeS'), observation=observation))
        except (ValueError, ArithmeticError, RuntimeError) as error:
            trials.append(dict(torqueNm=torque, success=False, status='numerical-failure', outcome=str(error)))
        return trials[-1]

    for torque in sorted(set(limit*i/4 for i in range(5))):
        trial(torque)
    passing = [r['torqueNm'] for r in trials if r['status'] == 'passing']
    hi = min(passing) if passing else None
    lower = max((r['torqueNm'] for r in trials if hi is not None and r['torqueNm'] < hi and r['status'] == 'failed-target'), default=None)
    if hi is not None and hi > 0:
        explore_lo = lower if lower is not None else 0.
        for _ in range(min(7, max(0, iterations))):
            mid = (explore_lo+hi)/2
            row = trial(mid)
            if row['status'] == 'passing':
                hi = mid
            elif row['status'] == 'failed-target':
                lower = mid
                explore_lo = mid
            else:
                explore_lo = mid  # Exploratory bound only, never a proven failure.
    best = next((r for r in reversed(trials) if r['torqueNm'] == hi), None)
    indeterminate = any(r['status'] in ('numerical-failure', 'insufficient-duration') for r in trials)
    return dict(engine=payload['engine'],kind=case['kind'],targets=targets,commandBasis=motor.config['commandBasis'] if motor.enabled else 'joint',
                feasible=hi is not None,status='passing-tested-torque' if hi is not None else 'indeterminate' if indeterminate else 'no-passing-tested-torque',
                torqueNm=hi,lowerBoundNm=lower,limitNm=limit,evaluations=len(trials),trials=trials,bestTrial=best,
                limitation='Lowest passing tested command and a local failing bracket only; not a global minimum, peak rating, or post-arrest safety guarantee.',
                assessmentStopPolicy='Jump trials observe first genuine flight apex before recontact. Landing trials stop at first arrest/bottom-out/underside contact. Duration is never extended; numerical failures and unobserved events are indeterminate.')
