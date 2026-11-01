"""Run a bounded, exact-profile V5 compatibility matrix in both actual engines.

Run with the app's installed Python environment:
  python verify_v5_scenarios.py --profile saved-configurations/v5-alpha0-4to1.json --profile saved-configurations/v5-alpha20-4to1.json --output .preview/v5-scenarios
Inputs: one or two complete project-v3 JSONs (builder mm/deg/kg/N, solver s/Nm), SciPy,
  NumPy and Pymunk. The prescribed bench is a stationary flat-ground support
  check with zero height/speed/transition/delay; actual contact uses saved terrain/jump/landing
  commands. Every override and exact request is captured with source hashes.
Outputs: eight core captures plus two one-second flat-support diagnostics per profile, a compact
  summary and per-engine comparison in
  the specified ignored app-local output folder. No live service/profile writes.
Limitations: runnable/finite cases are distinct from successful target outcomes;
  endpoint sizing, rigid-contact impulses and numerical residuals are not hardware
  certification. No controller, friction, motor or substitute mass is invented.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import dynamics
from analytical_contact import simulate_contact as analytical_contact
from contact_dynamics import simulate_contact as pymunk_contact
from contact_cases import CASE_DEFAULTS, validate_contact_request
from dynamic_model import Model
from profile_service import _project

ROOT = Path(__file__).resolve().parent
CASES = ('prescribed-height', 'terrain-stability', 'jump', 'landing')
ENGINES = ('analytical', 'pymunk')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_write(path, value):
    Path(path).write_text(json.dumps(value, allow_nan=False, indent=2), encoding='utf-8')


def make_request(project, kind, engine):
    """Freeze saved settings with only the explicit interaction/case switch."""
    p = copy.deepcopy(project)
    c = p['solverConfig']
    c['fixture'] = 'floating-chassis'
    c['inputRiseMm'] = 0.
    if kind == 'prescribed-height':
        c.update(inputHeightMm=0., inputSpeedMmS=0., inputDelayS=0.)
    request = dict(engine=engine, params=p['params'], runConfig=c)
    if 'motorConfig' in p:
        request['motorConfig'] = p['motorConfig']
    p['contactConfig'] = {**p.get('contactConfig', {}), 'mode': 'prescribed-height' if kind == 'prescribed-height' else 'terrain-contact'}
    if kind != 'prescribed-height':
        request['contactConfig'] = p['contactConfig']
        p['caseConfig'] = {**CASE_DEFAULTS, **p.get('caseConfig', {}), 'kind': kind}
        request['caseConfig'] = p['caseConfig']
        if 'terrainConfig' in p:
            request['terrainConfig'] = p['terrainConfig']
    return request, p


def summarize(result, request, flat_support=False):
    rows, frames = result['rows'], result['frames']
    assert len(rows) == len(frames) >= 2, 'Every output row must have its actual frame.'
    assert all(rows[i]['t'] <= rows[i+1]['t'] for i in range(len(rows)-1)), 'Output times must be ordered.'
    json.dumps(result, allow_nan=False)
    assert result['params'] == request['params'], 'Solver silently changed builder parameters.'
    assert result['runConfig'] == request['runConfig'], 'Solver silently changed run settings.'
    kind = 'flat-support' if flat_support else request.get('caseConfig', {}).get('kind', 'prescribed-height')
    diag, metrics = result['diagnostics'], result.get('caseMetrics', {})
    assert diag['termination'] == 'duration', 'Unexpected early termination: ' + diag['termination']
    assert abs(rows[-1]['t']-request['runConfig']['duration']) < 1e-7
    if kind == 'prescribed-height':
        assert diag['inputLaw'] == 'stationary-flat-ground'
        assert all(r['requestedInputMm'] == r['appliedInputMm'] == 0 for r in rows), 'Ground-check input must remain flat.'
        assert all(r['inputVelocityMmS'] == r['inputAccelerationMmS2'] == 0 for r in rows)
        assert all(abs(r['inputWorkJ']) < 1e-12 for r in rows), 'Stationary prescribed ground supplies no input work.'
        assert abs(diag['wheelCoefficientK']+.25) < 1e-12, 'Expected both1:2 wheel-drive stages.'
    else:
        assert diag['finiteLinkDynamics'] and diag['rigidBodies'] == 4
        assert result['scope']['wheelTerrainBound'] is False
        assert diag['maxPenetrationMm'] < 1
        if kind == 'terrain-stability':
            assert any(e['type'] == 'first-raised-terrain-contact' for e in result['events'])
            assert max(abs(r['wheelAngularVelocityDegS']) for r in rows) > 1, 'Free wheel did not spin.'
        elif kind == 'jump':
            assert metrics.get('takeoffTimeS') is not None
            assert metrics.get('jumpComRiseMm') is not None
        elif kind == 'landing':
            assert metrics.get('impactTimeS') is not None
            assert metrics.get('firstArrestTimeS') is not None
    early = [r for r in rows if r['t'] <= min(.4, request['runConfig']['inputDelayS'])+1e-9]
    return dict(kind=kind, engine=result['engine'], designHash=result['designHash'], samples=len(rows),
        elapsedSeconds=rows[-1]['t'], termination=diag['termination'],
        chassisHeightRangeMm=[min(r['chassisZMm'] for r in rows), max(r['chassisZMm'] for r in rows)],
        maxAbsHipRateDegS=max(abs(r.get('velocityDegS', r.get('angularVelocityDegS', 0))) for r in rows),
        minimumClearanceMm=metrics.get('minimumUndersideClearanceMm'),
        firstContactTimeS=metrics.get('impactTimeS'), takeoffTimeS=metrics.get('takeoffTimeS'),
        apexTimeS=metrics.get('apexTimeS'), jumpComRiseMm=metrics.get('jumpComRiseMm'),
        landingSuccess=metrics.get('landingSuccess'), firstArrestTimeS=metrics.get('firstArrestTimeS'),
        outcome=metrics.get('outcome'), maxPenetrationMm=diag.get('maxPenetrationMm'),
        maxConstraintPositionErrorMm=diag.get('maxConstraintPositionErrorMm'),
        energyBalanceResidualJ=diag.get('energyBalanceResidualJ', diag.get('maxWorkEnergyResidualJ')),
        preBumpMaxChassisDriftMm=max(abs(r['chassisZMm']-rows[0]['chassisZMm']) for r in early) if kind in ('terrain-stability', 'flat-support') and early else None,
        eventTypes=sorted(set(e['type'] for e in result['events'])),
        targetOutcomeMeaning='Observed outcome of the entered saved command; no hardware motor capacity or target pass is inferred from a completed run.')


def compare(a, b):
    assert a['designHash'] == b['designHash'], 'Paired engines must capture the same settings.'
    pairs = []
    for x in a['rows']:
        y = min(b['rows'], key=lambda r: abs(r['t']-x['t']))
        if abs(x['t']-y['t']) < 1e-7:
            pairs.append((x, y))
    assert len(pairs) >= 2
    return dict(matchedSamples=len(pairs), maxChassisHeightDifferenceMm=max(abs(x['chassisZMm']-y['chassisZMm']) for x, y in pairs),
        maxHipAngleDifferenceDeg=max(abs(x['theta2']-y['theta2']) for x, y in pairs),
        interpretation='Same-time output differences, not an accuracy tolerance or convergence certificate; impact events can occur on different substeps.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', action='append', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('.preview/v5-scenarios'))
    args = parser.parse_args()
    if not 1 <= len(args.profile) <= 2:
        parser.error('Provide one or two V5 profile JSONs.')
    args.output.mkdir(parents=True, exist_ok=True)
    source_names = ('dynamics.py', 'dynamic_model.py', 'contact_cases.py', 'analytical_contact.py', 'contact_dynamics.py', 'finite_contact_model.py', 'finite_pymunk_contact.py', 'motor_model.py')
    report = dict(schema='kinefold/v5-scenario-check-v1', python=platform.python_version(),
        sourceHashes={name: sha(ROOT/name) for name in source_names}, profiles=[], failures=[], flatSupport=[],
        limitations='Experimental finite-link quarter models. Prescribed wheel height and actual contact are different boundary conditions. Constant joint commands are illustrative; no hidden ride controller. No canonical robot or hardware acceptance.')
    manifest = dict(schema='kinefold/v5-capture-manifest-v1', captures=[], flatSupportCaptures=[])
    for path in args.profile:
        project = json.loads(path.read_text(encoding='utf-8-sig'))
        original = json.dumps(project, sort_keys=True)
        _project(project)
        p = project['params']
        assert p['te'] > (180+p['phi0'])/2 and p['tc']-p['te'] <= 90
        assert p['m2'] == p['m3'] == 1 and p['m6'] == .5
        assert p['rc']/p['rd'] == p['re']/p['rf'] == .5
        item = dict(name=project['name'], id=project['id'], profileSha256=sha(path), alphaDeg=p['alpha'], cases=[], comparisons={})
        report['profiles'].append(item)
        for kind in CASES:
            captures = {}
            for engine in ENGINES:
                request, snapshot = make_request(project, kind, engine)
                if kind == 'prescribed-height':
                    Model(request['params'], request['runConfig'], request.get('motorConfig'))
                    simulate = dynamics.simulate
                else:
                    validate_contact_request(request)
                    simulate = analytical_contact if engine == 'analytical' else pymunk_contact
                started = time.perf_counter()
                filename = f"alpha{p['alpha']:g}-{kind}-{engine}.json"
                result = None
                try:
                    result = simulate(request)
                    json_write(args.output/filename, dict(payload=request, projectSnapshot=snapshot, result=result))
                    summary = summarize(result, request)
                except Exception as error:
                    failure = dict(alphaDeg=p['alpha'], profileId=project['id'], kind=kind, engine=engine, error=str(error), wallSeconds=time.perf_counter()-started)
                    if result is not None:
                        failure.update(capture=filename, termination=result['diagnostics'].get('termination'),
                            elapsedSeconds=result['rows'][-1]['t'])
                        manifest['captures'].append(dict(profileId=project['id'], profileName=project['name'], alphaDeg=p['alpha'], kind=kind, engine=engine,
                            capturePath=filename, payloadKey='payload', resultKey='result', projectKey='projectSnapshot', sha256=sha(args.output/filename), compatibilityPass=False))
                        json_write(args.output/'manifest.json', manifest)
                    json_write(args.output/(filename+'.failure.json'), dict(**failure, payload=request, projectSnapshot=snapshot))
                    report['failures'].append(failure)
                    item['cases'].append(dict(**failure, compatibilityPass=False))
                    json_write(args.output/'summary.json', report)
                    print(json.dumps(failure), flush=True)
                    continue
                summary['wallSeconds'] = time.perf_counter()-started
                summary['capture'] = filename
                summary['compatibilityPass'] = True
                item['cases'].append(summary)
                captures[engine] = result
                manifest['captures'].append(dict(profileId=project['id'], profileName=project['name'], alphaDeg=p['alpha'], kind=kind, engine=engine,
                    capturePath=filename, payloadKey='payload', resultKey='result', projectKey='projectSnapshot', sha256=sha(args.output/filename), compatibilityPass=True))
                json_write(args.output/'manifest.json', manifest)
                json_write(args.output/'summary.json', report)
                print(json.dumps(dict(alpha=p['alpha'], **summary)), flush=True)
            if set(captures) == set(ENGINES):
                item['comparisons'][kind] = compare(captures['analytical'], captures['pymunk'])
        assert json.dumps(project, sort_keys=True) == original
        assert sha(path) == item['profileSha256']
        for engine in ENGINES:
            request, snapshot = make_request(project, 'terrain-stability', engine)
            request['runConfig'].update(duration=1., inputHeightMm=0., inputSpeedMmS=0., hipTorqueNm=0., dampingNms=0.)
            request.pop('terrainConfig', None)
            snapshot.pop('terrainConfig', None)
            started = time.perf_counter()
            result = (analytical_contact if engine == 'analytical' else pymunk_contact)(request)
            summary = summarize(result, request, flat_support=True)
            summary.update(profileId=project['id'], alphaDeg=p['alpha'], wallSeconds=time.perf_counter()-started)
            rows = result['rows']
            settled = [r['contactNormalForceN'] for r in rows if r['t'] >= .5]
            summary.update(chassisEndDriftMm=rows[-1]['chassisZMm']-rows[0]['chassisZMm'],
                maximumChassisDriftMm=max(abs(r['chassisZMm']-rows[0]['chassisZMm']) for r in rows),
                expectedStaticContactN=sum(p[k] for k in ('m1', 'm2', 'm3', 'm5', 'm6'))*p['g'],
                meanSettledContactN=sum(settled)/len(settled), hipEndDriftDeg=rows[-1]['theta2']-rows[0]['theta2'],
                meaning='Zero entered torque/damping, stationary flat floor, free wheel and floating chassis; residual fit drift and cold-contact settling are retained, not pinned out.')
            filename = f"alpha{p['alpha']:g}-flat-support-{engine}.json"
            json_write(args.output/filename, dict(payload=request, projectSnapshot=snapshot, result=result))
            summary['capture'] = filename
            report['flatSupport'].append(summary)
            manifest['flatSupportCaptures'].append(dict(profileId=project['id'], alphaDeg=p['alpha'], kind='flat-support', engine=engine, capturePath=filename,
                payloadKey='payload', resultKey='result', projectKey='projectSnapshot', sha256=sha(args.output/filename)))
            json_write(args.output/'manifest.json', manifest)
            print(json.dumps(summary), flush=True)
        json_write(args.output/'summary.json', report)
    assert sum(len(p['cases']) for p in report['profiles']) == 8*len(args.profile)
    json_write(args.output/'summary.json', report)
    if report['failures']:
        raise SystemExit('FAIL: '+str(len(report['failures']))+' V5 case(s); inspect retained failure requests and summary.')
    assert len(report['flatSupport']) == 2*len(args.profile)
    print(f'PASS {8*len(args.profile)} actual V5 cases plus {2*len(args.profile)} flat-support diagnostics; exact profile inputs and both engine captures retained under '+str(args.output), flush=True)


if __name__ == '__main__':
    main()
