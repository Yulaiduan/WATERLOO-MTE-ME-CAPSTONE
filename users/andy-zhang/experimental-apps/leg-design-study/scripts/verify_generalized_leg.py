"""Verify all nine generalized spring mechanisms through actual Pymunk motion.

Invocation: python scripts/verify_generalized_leg.py from leg-design-study root.
Inputs: fixed documented central 325 mm candidate, assumed kg allocation and
SI spring laws. Outputs: compact JSON verification metrics on stdout; nonzero
exit on any failed analytical/engine/refinement check. NumPy/SciPy/Pymunk needed.
Limitations: independent experimental fixtures, no hardware, real belt-bearing
forces, tire rolling/contact or canonical robot validation. No files are written.
"""
from pathlib import Path
import json
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generalized_leg as g


def main():
    c = g.physical_allocation(g.config(dict(L2=180., L3=340., ra=106.5, rb=60.,
                                          alpha=4.375, tc=159.81088834775142)))
    rows, travel = g.trajectory(c, 1., 101)
    checks = []
    for topology in g.CATALOG:
        fit = g.fit_spring(c, topology, [row['q_rad'] for row in rows])
        if not fit['feasible']:
            checks.append(dict(topology=topology, passed=False, reason=fit['reason']))
            continue
        work = g.virtual_work_checks(c, fit['config'], [row['q_rad'] for row in rows[::10]])
        physical = g.verify_pymunk(c, fit['config'])
        checks.append(dict(topology=topology, passed=physical['passed'] and work['passed'],
                           virtual_work=work, refinement=[{key: value for key, value in run.items()
                                                          if key not in ('trace', 'resolved_config')}
                                                         for run in physical['refinement']]))
        print(json.dumps(checks[-1], allow_nan=False), flush=True)
    # Nonzero wheel/compound slopes verify all belt carriers beyond the common
    # qcd=qef=1 locked-drive special case.
    tilted = g.physical_allocation(g.config(dict(L2=290., L3=235., ra=96., rb=60., rc=30., rd=35.,
                                                re=36., rf=32., alpha=17., phi0=10.)))
    fixed = g.verify_pymunk(tilted, None, 'fixed_a')
    summary = dict(candidate=c, travel=travel, all_nine_passed=all(x['passed'] for x in checks),
                   fixed_a_generalized_passed=fixed['passed'], tests=len(checks)+1)
    print(json.dumps(summary, allow_nan=False), flush=True)
    return 0 if summary['all_nine_passed'] and fixed['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
