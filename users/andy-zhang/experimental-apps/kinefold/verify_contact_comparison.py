"""Compare independent contact engines for the same saved-style jump/landing.

Run app .venv Python verify_contact_comparison.py. Inputs: unchanged final JS
V4 geometry plus explicit1.5kg wheel, friction0.8, zero bounce, saved case
defaults and SI steps. Outputs compact convergence evidence to stdout and
ignored .preview/contact-case-comparison.json. Tests independent numerical
agreement/refinement and energy identities, not hardware or peak torque ratings.
"""
import json
from pathlib import Path
import subprocess
import sys

from analytical_contact import simulate_contact as analytical
from contact_dynamics import simulate_contact as pymunk
from contact_cases import CASE_DEFAULTS
from dynamic_model import defaults


def main():
    root = Path(__file__).resolve().parent
    source = "const fs=require('fs'),vm=require('vm');for(const p of ['reference-v4.js','model.js'])vm.runInThisContext(fs.readFileSync(p,'utf8'));console.log(JSON.stringify(Kinefold.defaults));"
    params = json.loads(subprocess.check_output(['node', '-e', source], cwd=root, text=True))
    params['m6'] = 1.5
    probe = subprocess.run([sys.executable, '-c', "import analytical_contact,sys;assert not any(k.startswith('pymunk') for k in sys.modules)"], cwd=root, capture_output=True, text=True)
    assert probe.returncode == 0, probe.stderr
    report = {}
    for kind in ('jump', 'landing'):
        values = []
        for dt in (.0005, .00025, .000125):
            request = dict(engine='analytical', params=params,
                           runConfig={**defaults(), 'duration': 2, 'dt': dt},
                           contactConfig=dict(mode='terrain-contact', friction=.8, restitution=0, drive='free'),
                           caseConfig={**CASE_DEFAULTS, 'kind': kind})
            a = analytical(request)
            b = pymunk({**request, 'engine': 'pymunk'})
            assert a['designHash'] == b['designHash']
            assert a['caseConfig'] == b['caseConfig']
            assert a['diagnostics']['termination'] == b['diagnostics']['termination'] == 'duration'
            aa = {round(row['t'], 8): row for row in a['rows']}
            bb = {round(row['t'], 8): row for row in b['rows']}
            common = sorted(aa.keys() & bb.keys())
            assert len(common) == len(a['rows']) == len(b['rows']) == 201
            error = max(abs(aa[t]['chassisZMm'] - bb[t]['chassisZMm']) for t in common)
            for result in (a, b):
                for row in result['rows']:
                    assert abs(row['chassisKineticJ'] - .5 * params['m1'] * (row['chassisVelocityMmS']/1000)**2) < 1e-9
            if kind == 'landing':
                assert a['caseMetrics']['landingSuccess'] and b['caseMetrics']['landingSuccess']
            values.append(dict(dt=dt, matched=len(common), maxChassisDifferenceMm=error,
                               analyticalEvents=a['caseMetrics'], pymunkEvents=b['caseMetrics'],
                               motorWorkDifferenceJ=b['rows'][-1]['motorWorkJ']-a['rows'][-1]['motorWorkJ'],
                               analyticalLedgerResidualJ=a['rows'][-1]['energyBalanceResidualJ'],
                               pymunkLedgerResidualJ=b['rows'][-1]['energyBalanceResidualJ']))
        assert values[0]['maxChassisDifferenceMm'] > values[1]['maxChassisDifferenceMm'] > values[2]['maxChassisDifferenceMm'], values
        report[kind] = values
    target = root / '.preview' / 'contact-case-comparison.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'status':'PASS', 'independentImport':True, 'cases':{kind:[dict(dt=v['dt'],maxChassisDifferenceMm=v['maxChassisDifferenceMm'],motorWorkDifferenceJ=v['motorWorkDifferenceJ']) for v in values] for kind,values in report.items()}}, indent=2))


if __name__ == '__main__':
    main()
