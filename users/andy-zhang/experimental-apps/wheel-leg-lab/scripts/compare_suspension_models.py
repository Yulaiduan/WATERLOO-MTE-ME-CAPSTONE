"""Reproduce matched-input SciPy/Pymunk suspension deltas for the data browser.

Run from app root: .venv/Scripts/python.exe scripts/compare_suspension_models.py
Inputs: documented editable 200 mm wheel, 273 mm links, 45 degree initial pose,
30 mm / 250 ms quintic wheel-height step, 6 seconds; SI channel units below.
Outputs: portable run JSON and summary under ignored artifacts/model-comparison.
Requires app NumPy/SciPy/Pymunk. No canonical robot, tire contact or hardware
validation. Delta is Pymunk minus SciPy; physical pin forces are step averages,
mathematical loads instantaneous. Full-window and post-startup errors are separate.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from physics import config, simulate
from math_model import simulate_math
from suspension_architecture import constant_lift_profile

CHANNELS = {
    'chassis_displacement_mm': 'mm', 'theta_deg': 'deg',
    'chassis_vy': 'm/s', 'chassis_ay': 'm/s^2',
    'j1_force': 'N', 'j2_force': 'N', 'j3_force': 'N',
    'driver_force': 'N', 'guide_hip_reaction': 'N*m',
}


def differences(reference, candidate, start=0.):
    """Interpolate the reference only within shared time bounds; never extrapolate."""
    a, b = reference['rows'], candidate['rows']
    ta, tb = np.array([r['t'] for r in a]), np.array([r['t'] for r in b])
    assert np.all(np.diff(ta) > 0) and np.all(np.diff(tb) > 0)
    times = np.unique(np.concatenate((ta, tb)))
    times = times[(times >= max(ta[0], tb[0], start)) & (times <= min(ta[-1], tb[-1]))]
    out = {}
    for channel, unit in CHANNELS.items():
        delta = np.interp(times, tb, [r[channel] for r in b]) - np.interp(
            times, ta, [r[channel] for r in a])
        assert len(delta) and np.all(np.isfinite(delta))
        out[channel] = {'unit': unit, 'samples': len(delta),
                        'max_abs': float(np.max(np.abs(delta))),
                        'rms': float(np.sqrt(np.mean(delta**2))),
                        'final': float(delta[-1])}
    return out


def main():
    output = ROOT/'artifacts/model-comparison'
    output.mkdir(parents=True, exist_ok=True)
    report = {'delta': 'Pymunk minus SciPy', 'sampling': 'Union of recorded timestamps over overlap; linear interpolation; sample RMS.', 'cases': {},
              'scope': 'Bilateral prescribed wheel height; same masses, geometry, spring and input. Physical loads are finite-step averages; math loads instantaneous.'}
    for name, values in [('original-tip', config()), ('constant-lift', constant_lift_profile())]:
        values.update(duration=6., theta=45., wave='step', position_amplitude=.03,
                      start=.5, rise=.25, fall=.25, ramp_shape='quintic', dt=.001)
        reference, physical = simulate_math(values), simulate(values)
        physical['backend'] = 'pymunk'
        for backend, run in [('math', reference), ('pymunk', physical)]:
            packet = {'schema': 'wheel-leg-lab-record/v1', 'kind': 'run',
                      'name': f'{name} | {backend} | 30 mm step | 1 ms',
                      'backend': backend, 'config': run['config'], 'result': run}
            (output/f'{name}-{backend}.json').write_text(json.dumps(packet), encoding='utf-8')
        refined = simulate(dict(values, dt=.0005))
        refined_math = simulate_math(dict(values, dt=.0005))
        report['cases'][name] = {'config': values,
            'full_1ms': differences(reference, physical),
            'after_50ms_1ms': differences(reference, physical, .05),
            'full_half_ms': differences(refined_math, refined),
            'after_50ms_half_ms': differences(refined_math, refined, .05),
            'scipy_stopped': reference['diagnostics']['stop_steps'] > 0,
            'pymunk_stop_steps': physical['diagnostics']['stop_steps']}
        print(name, json.dumps(report['cases'][name]['full_1ms']), flush=True)
    (output/'summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Saved portable run records and matched-time delta summary:', output)


if __name__ == '__main__':
    main()
