"""Refresh the embedded position-step/square Pymunk remote recordings.

Run: .venv/Scripts/python.exe scripts/record_position_preview.py from app root.
Inputs: explicit illustrative 30 mm / 250 ms C2 wheel-height commands, SI model.
Outputs: updates only pm-data in animations/pymunk-remote-preview.html; frames
are decimated to about 22 Hz and trace buckets retain per-channel extrema.
Requires pinned Pymunk. Recorded bilateral-fixture playback is not tire contact,
live browser physics, or hardware validation; full-resolution CSV uses the app.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from physics import simulate

KEYS = ['t', 'input', 'j1_force', 'j2_force', 'j3_force',
        'spring_knee_moment', 'guide_hip_reaction', 'chassis_vy', 'chassis_ay',
        'theta_deg', 'driver_force', 'input_mm', 'position_actual_mm',
        'chassis_displacement_mm']


def rounded(value):
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, list):
        return [rounded(v) for v in value]
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    return value


def main():
    data = {'keys': KEYS, 'cases': {}}
    for wave in ['step', 'square']:
        result = simulate({'target': 'position', 'fixture': 'floating',
                           'wave': wave, 'position_amplitude': .03,
                           'ramp_shape': 'quintic', 'rise': .25, 'fall': .25,
                           'duration': 3., 'bias_force': 0.})
        indices = {0, len(result['rows'])-1}
        for start in range(0, len(result['rows']), 12):
            bucket = list(range(start, min(start+12, len(result['rows']))))
            indices.update([bucket[0], bucket[-1]])
            for key in KEYS[1:]:
                indices.add(min(bucket, key=lambda i: result['rows'][i][key]))
                indices.add(max(bucket, key=lambda i: result['rows'][i][key]))
        frames = result['frames'][::4]
        if frames[-1] is not result['frames'][-1]:
            frames.append(result['frames'][-1])
        data['cases'][wave] = {
            'label': f'30 mm {wave} · 250 ms smooth ramps · floating chassis · forces measured',
            'config': result['config'], 'model': result['model'],
            'position_origin': result['position_origin'],
            'diagnostics': result['diagnostics'], 'warnings': result['warnings'],
            'rows': [[result['rows'][i][k] for k in KEYS] for i in sorted(indices)],
            'frames': [[f['t'], *f['hip'], *f['knee'], *f['hub'], *f['tip'],
                        f['upper_angle'], f['lower_angle'], f['debug_draw']]
                       for f in frames]}
    path = ROOT/'animations/pymunk-remote-preview.html'
    text = path.read_text(encoding='utf-8')
    payload = json.dumps(rounded(data), separators=(',', ':'), allow_nan=False)
    text, count = re.subn(r'(<script type="application/json" id="pm-data">).*?(</script>)',
                         lambda m: m[1]+payload+m[2], text, flags=re.S)
    if count != 1:
        raise ValueError('Expected exactly one pm-data script.')
    if len(text.encode('utf-8')) >= 1_000_000:
        raise ValueError('Recording exceeds inline size limit.')
    path.write_text(text, encoding='utf-8', newline='\n')
    print(f'Recorded position preview: {len(text.encode("utf-8"))} bytes.')


if __name__ == '__main__':
    main()
