"""Extract labelled Motion Lab examples from the retained offline path study.

Run: python scripts/build_design_examples.py from the Motion Lab app root.
Inputs: sibling inversion-path-results.json; lengths mm, angles degrees.
Outputs: web/design-examples/data.js with five exact configs and reported metrics.
Uses Python standard library. This selects evidence, without running a search or
altering any solver, spring, saved profile, or report. No hardware claim.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'leg-design-study/docs/inversion-path-results.json'
CHOICES = [
    ('practical_equal350_7over4_start115', 'simple-guide', '01', 'Equal links · simple 7:4 guide',
     'Ratio-only example', '325 mm working stroke; accept about 10 mm bow. The inverted branch mirrors its tilt.'),
    ('equal_325', 'longer-links', '02', 'Equal links · straighter long-link branch',
     'Ratio-only example', 'Lower bow at greater size; the 450 mm link bound is active in the search.'),
    ('phase_near_equal_12p5', 'near-equal-indexed', '03', 'Near-equal links · fixed assembly indexing',
     'Assembly-phase alternative', 'Lower-link phase is fixed at -25°. This relaxes the original phase-zero constraint.'),
    ('phase_equal_12p5', 'exact-line-indexed', '04', 'Equal links · exact indexed straight line',
     'Assembly-phase alternative', 'An exact 12.5° line at alpha=0, with fixed -25° lower-link phase. The wheel crosses the hip.'),
    ('screenshot_250_5over3', 'screenshot-reference', '05', 'Original screenshot · 250 mm links',
     'Reference', 'The original 5:3 guide and 100–165° working range; included for direct comparison.'),
]


def main():
    evidence = json.loads(SOURCE.read_text(encoding='utf-8'))
    cases = {c['id']: c for group in ['selected', 'practical', 'examples'] for c in evidence[group]}
    designs = []
    for identifier, slug, number, label, role, note in CHOICES:
        source = cases[identifier]
        designs.append(dict(id=identifier, slug=slug, number=number, label=label,
                            role=role, note=note, config=source['config'],
                            metrics=source['metrics'], full=source['full_inversion']))
    result = dict(schema='motion-lab/design-examples/v1', source_revision='12e227c',
                  source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  units=dict(length='mm', angle='degrees'), designs=designs,
                  scope='Prescribed ideal kinematics; no spring, contact, collision or motor simulation.')
    target = ROOT / 'web/design-examples/data.js'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(('/* Selected geometry and metrics for Motion Lab drawings.\n'
                        ' * Regenerate: python scripts/build_design_examples.py. Inputs: retained mm/degree evidence.\n'
                        ' * Outputs: five labelled configs. Prescribed kinematics only; no physics/hardware claim.\n'
                        ' */\n'
                        'export const data = ' + json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2)
                        + ';\n').encode('utf-8'))
    print('Built five labelled design examples from retained evidence.')


if __name__ == '__main__':
    main()
