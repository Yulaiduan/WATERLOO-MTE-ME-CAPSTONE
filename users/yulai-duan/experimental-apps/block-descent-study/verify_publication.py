"""Compare portable study reruns with the published compact numerical evidence.

Run: python verify_publication.py after the four study commands in README.md.
Inputs: app-local ignored results and repository docs evidence; units per field.
Outputs: publication-validation.json and concise stdout; exits nonzero on mismatch.
Limits: reproduction checks, not hardware or canonical-robot validation.
"""
from pathlib import Path
import hashlib
import json
import math
from PIL import Image, ImageChops

APP=Path(__file__).resolve().parent
REPO=APP.parents[3]
STUDIES=['2026-10-18-jon-single-leg-descent','2026-10-18-jon-descent-heights',
         '2026-10-19-jon-baseline-descent']


def main():
    comparisons=0;case_count=0;max_error=0.
    for study in STUDIES:
        expected=json.loads((REPO/'docs/benchmarks'/study/'results.json').read_text())
        actual=json.loads((APP/'results'/study/'study.json').read_text())
        old={x['case']['name']:x for x in expected['cases']}
        new={x['case']['name']:x for x in actual['cases']}
        assert old.keys()==new.keys(),study
        for name,e in old.items():
            a=new[name];assert e['case']==a['case'],(study,name,'case')
            for key,value in e['metrics'].items():
                if key in {'wall_s','wall_seconds'}:continue
                found=a['metrics'][key]
                if isinstance(value,(int,float)):
                    err=abs(found-value);max_error=max(max_error,err)
                    assert math.isclose(found,value,rel_tol=1e-10,abs_tol=1e-10),(study,name,key,found,value)
                else:assert found==value,(study,name,key)
                comparisons+=1
            case_count+=1
    original=json.loads((REPO/'docs/design/simulation/assets/descent-profile-results.json').read_text())
    profile=json.loads((APP/'results/2026-10-19-descent-profile/results.json').read_text())
    for key in ['inputs','corner_clearance_duration_bound_s','critical_normalized_time','targets','example_at_100ms']:
        assert profile[key]==original[key],key
    assert profile['passive_trace']['sha256']==original['passive_trace']['sha256']
    figures=[]
    for study in STUDIES:
        for png in (REPO/'docs/benchmarks'/study/'assets').glob('*.png'):
            rerun=APP/'results'/study/'plots'/png.name
            assert ImageChops.difference(Image.open(png).convert('RGB'),Image.open(rerun).convert('RGB')).getbbox() is None,png
            figures.append(str(png.relative_to(REPO)))
    oldpng=REPO/'docs/design/simulation/assets/descent-profile-feasibility.png'
    newpng=APP/'results/2026-10-19-descent-profile/descent-profile-feasibility.png'
    assert ImageChops.difference(Image.open(oldpng).convert('RGB'),Image.open(newpng).convert('RGB')).getbbox() is None
    figures.append(str(oldpng.relative_to(REPO)))
    record=dict(status='PASS',physics_scope='isolated member research, not canonical robot validation',
                contact_integrations=case_count,metric_comparisons=comparisons,
                max_physical_metric_absolute_error=max_error,
                analytical_targets_and_geometry_match=True,passive_trace_sha256_matches=True,
                pixel_identical_figures=figures,
                source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in APP.iterdir() if p.suffix in {'.py','.cjs','.swift'}})
    (APP/'publication-validation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
