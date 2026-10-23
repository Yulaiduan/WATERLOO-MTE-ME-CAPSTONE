"""Validate both floating dynamic engines against Jon's original VSL v4 statics.

Run here: .venv/Scripts/python.exe validate_static.py
Optional --output .preview/static-validation.json writes detailed generated evidence.
Inputs: original repository HTML (hash verified), explicit mm/deg/kg/N designs,
flat wheel input, zero initial speed/damping and source-derived holding torque.
Outputs: checked-case counts, tolerances and numerical errors as JSON; nonzero on
failure. Requires Node and this app's pinned SciPy/Pymunk environment. Does not
change profiles/server/browser state. Static-limit consistency only: the Pymunk
chassis is real but ideal linkage inertia is condensed; spring/support readouts
are derived force-law quantities, not independently measured contact forces.
"""
import argparse
import json
import math
from pathlib import Path
import platform
import subprocess

from dynamic_model import Model, R, defaults
from dynamics import simulate

ROOT = Path(__file__).resolve().parent
# Execute only the source's reviewed analytical blocks, never its UI scripts.
# The oracle uses the original HTML directly, not Python or the vendored adapter.
ORACLE_JS = r"""
const fs=require('fs'),vm=require('vm'),crypto=require('crypto'),path=require('path');
const provenance=JSON.parse(fs.readFileSync('reference.json','utf8'));
const src=fs.readFileSync(path.resolve('../../../..',provenance.source),'utf8').replace(/\r\n/g,'\n');
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
if(sha(src)!==provenance.source_sha256)throw Error('Original source hash differs');
const scripts=[...src.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
const retained=[...scripts.slice(0,2),scripts[2].split('const VSLDomains=')[0]].join('\n');
if(sha(retained)!==provenance.retained_blocks_sha256)throw Error('Original blocks hash differs');
vm.runInThisContext(retained);
const baseline={...VSLStatic.defaults,Fx:0,loadMode:'weight',springLaw:'v4',theta2:132.5};delete baseline.Fy;
const variants=[['baseline',{}],['unequal-ratios',{L2:340,L3:280,ra:47,rb:27,rc:31,rd:39,re:22,rf:29,alpha:13,phi0:17,m2:.5,m3:.5,m5:.2,m6:1}],['constant',{springLaw:'constant',alpha:25,m2:.3,m3:.8,m6:1.2}],['point-idler',{rs:0,Su:0,nu:8}],['spring-disabled',{springEnabled:false}],['additional-loads',{loadMode:'global',Fx:7,Fz:14,m2:.4,m6:1,ra:47,rb:27,rc:31,rd:39,re:22,rf:29}],['contact-loads',{loadMode:'contact',Fn:11,Ft:5,m2:.2,m3:.3}],['offset-support',{L2:340,L3:280,ra:47,rb:27,rc:31,rd:39,re:22,rf:29,alpha:13,phi0:17,beta:25,loadMode:'global',Fx:7,Fz:14,m2:.5,m3:.5,m5:.2,m6:1}]];
console.log(JSON.stringify({sha:sha(src),variants:variants.map(([name,v])=>{const p={...baseline,...v};const mt=['m1','m2','m3','m5','m6'].reduce((a,k)=>a+p[k],0);const b=p.beta*Math.PI/180;let Fy,FzExtra;if(p.loadMode==='weight'){Fy=0;FzExtra=0;}else if(p.loadMode==='global'){Fy=-p.Fx;FzExtra=p.Fz;}else{Fy=p.Fn*Math.sin(b)+p.Ft*Math.cos(b);FzExtra=p.Fn*Math.cos(b)-p.Ft*Math.sin(b);}
const ref={...p,loadMode:'yz',Fy,Fz:mt*p.g,springK:p.springLaw==='constant'?0:p.springK};
return {name,p,Fy,FzExtra,support:mt*p.g-FzExtra,rows:[100.1,105,115,125,132.5,140,150,160,164.9].map(theta=>{const s=VSLStatic.solve(ref,theta,true);if(!s.valid)throw Error(name+':'+s.reason);return{theta,tau:s.tau2,Fs:s.Fs,C:s.Cg,tau4:s.tau4,maxForce:s.maxForce,maxMoment:s.maxMoment};})};})}));
"""

TOLERANCES = dict(torqueNm=2e-10, springN=2e-9, geometryMm=2e-9,
                  angleDriftDeg=1e-8, chassisDriftMm=1e-8,
                  supportN=1e-8, accelerationMmS2=1e-7)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def flat_config(torque, duration=1):
    return {**defaults(), 'duration': duration, 'inputHeightMm': 0,
            'initialVelocityDegS': 0, 'dampingNms': 0, 'hipTorqueNm': torque}


def actual_run(engine, params, torque, duration=1):
    result = simulate(dict(engine=engine, params=params,
                           runConfig=flat_config(torque, duration)))
    require(result['diagnostics']['termination'] == 'duration',
            f'{engine}: travel termination cannot count as equilibrium')
    require(abs(result['rows'][-1]['t'] - duration) < 1e-10,
            f'{engine}: requested interval was not integrated')
    # The square scheduler still reports zero-height boundaries at its delay.
    require(all(abs(event['inputJumpMm']) < 1e-12 for event in result['events']),
            f'{engine}: flat input must have no nonzero jumps')
    require(all(abs(row['appliedInputMm']) < 1e-12 for row in result['rows']),
            f'{engine}: wheel input was not flat')
    return result


def summarize_run(result, params, support):
    rows = result['rows']
    return dict(
        maxAngleDriftDeg=max(abs(row['theta2'] - params['theta2']) for row in rows),
        maxChassisDriftMm=max(abs(row['chassisZMm'] - rows[0]['chassisZMm']) for row in rows),
        maxSupportErrorN=max(abs(row['inputReactionN'] - support) for row in rows),
        maxAccelerationMmS2=max(abs(row['chassisAccelerationMmS2']) for row in rows),
        maxSpringDriftN=max(abs(row['Fs'] - rows[0]['Fs']) for row in rows))


def validate():
    import numpy
    import scipy
    import pymunk

    oracle = json.loads(subprocess.check_output(['node', '-e', ORACLE_JS],
                                               cwd=ROOT, text=True))
    cases = []
    for variant in oracle['variants']:
        for row in variant['rows']:
            p = {**variant['p'], 'theta2': row['theta']}
            initial = Model(p, flat_config(0))
            # Jon puts the TOTAL load at rim P; dynamic support R acts at C.
            # Remove only the rim moment of R; explicit extra loads retain beta.
            correction = p['rw'] / 1000 * variant['support'] * math.sin(p['beta'] * R) * initial.K
            holding = row['tau'] - correction
            model = Model(p, flat_config(holding))
            q = model.q0
            error_torque = abs(-model.generalized(q) - holding)
            error_spring = abs(model.spring(q)['force'] - row['Fs'])
            center = model.sites(q)['6'][0]
            error_geometry = max(abs(center[i] * 1000 - row['C'][i]) for i in (0, 1))
            label = f"{variant['name']} at {row['theta']} degrees"
            require(error_torque <= TOLERANCES['torqueNm'], label + ': holding torque mismatch')
            require(error_spring <= TOLERANCES['springN'], label + ': spring mismatch')
            require(error_geometry <= TOLERANCES['geometryMm'], label + ': geometry mismatch')
            require(row['maxForce'] < 1e-8 and row['maxMoment'] < 1e-8,
                    label + ': original source FBD is not balanced')
            runs = {}
            for engine in ('analytical', 'pymunk'):
                result = actual_run(engine, p, holding)
                metrics = summarize_run(result, p, variant['support'])
                for metric, tolerance in (
                    ('maxAngleDriftDeg', 'angleDriftDeg'),
                    ('maxChassisDriftMm', 'chassisDriftMm'),
                    ('maxSupportErrorN', 'supportN'),
                    ('maxAccelerationMmS2', 'accelerationMmS2'),
                    ('maxSpringDriftN', 'springN')):
                    require(metrics[metric] <= TOLERANCES[tolerance], label + f': {engine} {metric}')
                runs[engine] = metrics
            cases.append(dict(variant=variant['name'], theta2Deg=row['theta'],
                              sourceHoldingTorqueNm=row['tau'], floatingHoldingTorqueNm=holding,
                              rimSupportCorrectionNm=correction, supportN=variant['support'],
                              springN=row['Fs'], torqueErrorNm=error_torque,
                              springErrorN=error_spring, geometryErrorMm=error_geometry,
                              engines=runs))

    # Controls deliberately violate equilibrium; they must move, not falsely pass.
    controls = []
    for name, variant, applied in (
        ('baseline-zero-torque', oracle['variants'][0], 0),
        ('offset-support-without-moment-correction', oracle['variants'][-1], None)):
        row = next(row for row in variant['rows'] if row['theta'] == 132.5)
        p = {**variant['p'], 'theta2': 132.5}
        applied = row['tau'] if applied is None else applied
        model = Model(p, flat_config(applied, .2))
        initial_acceleration = model.chassis(0, model.q0, 0,
                                             model.acceleration(model.q0, 0))[2] * 1000
        runs = {}
        for engine in ('analytical', 'pymunk'):
            result = actual_run(engine, p, applied, .2)
            first, last = result['rows'][0], result['rows'][-1]
            require(abs(first['chassisAccelerationMmS2'] - initial_acceleration) < 1e-7,
                    name + ': engine initial acceleration differs from force residual')
            drift = last['chassisZMm'] - first['chassisZMm']
            require(abs(drift) > .1, name + ': negative control did not detect motion')
            require(drift * initial_acceleration > 0, name + ': unexpected motion direction')
            runs[engine] = dict(chassisDriftMm=drift,
                                angleDriftDeg=last['theta2'] - p['theta2'])
        controls.append(dict(name=name, durationS=.2, appliedTorqueNm=applied,
                             requiredFloatingTorqueNm=-model.generalized(model.q0),
                             initialChassisAccelerationMmS2=initial_acceleration, engines=runs))

    baseline = next(c for c in cases if c['variant'] == 'baseline' and c['theta2Deg'] == 132.5)
    report = dict(status='PASS', source= 'users/jonathan-xie/experimental-apps/vsl-solver/v4/v4-pulley.html',
                  originalSourceSha256=oracle['sha'], sourceAndRetainedBlockHashesVerified=True,
                  versions=dict(python=platform.python_version(), numpy=numpy.__version__,
                                scipy=scipy.__version__, pymunk=pymunk.version,
                                node=subprocess.check_output(['node', '--version'], text=True).strip()),
                  matchedCases=len(cases), equilibriumRuns=2 * len(cases),
                  durationPerEquilibriumRunS=1, negativeControlRuns=4,
                  safeInteriorPosesDeg=[row['theta'] for row in oracle['variants'][0]['rows']],
                  tolerances=TOLERANCES, baseline=baseline,
                  worst=dict(torqueErrorNm=max(c['torqueErrorNm'] for c in cases),
                             springErrorN=max(c['springErrorN'] for c in cases),
                             geometryErrorMm=max(c['geometryErrorMm'] for c in cases),
                             engines={engine: {metric: max(c['engines'][engine][metric] for c in cases)
                                               for metric in cases[0]['engines'][engine]}
                                      for engine in ('analytical', 'pymunk')}),
                  negativeControls=controls, cases=cases)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = validate()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'cases'}, indent=2))


if __name__ == '__main__':
    main()
