"""Save one synced actual analytical/Pymunk terrain GIF with a small PNG poster.

Run from Kinefold: python encode_terrain_animation.py --analytical CAPTURE_JSON
--pymunk CAPTURE_JSON --output-prefix exports/my-terrain [--label TEXT]
[--sharp-module INSTALLED_MODULE_PATH]. Inputs use saved world mm/deg/SI rows.
Requires Node.js, installed Sharp and Pillow; no physics or browser runs.
Outputs only GIF, midpoint poster PNG and small playback/provenance JSON in this
app. The private PNG cache is temporary under .preview and is removed on exit.
Rigid quarter-model replay is not measured hardware or whole-vehicle stability.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent


def encode(args):
    prefix = args.output_prefix.resolve()
    if ROOT not in prefix.parents:
        raise ValueError('Animation outputs must stay inside this Kinefold app.')
    prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = {key: Path(str(prefix) + suffix) for key, suffix in
               (('gif', '.gif'), ('poster', '-poster.png'), ('manifest', '-playback.json'))}
    if any(p.exists() for p in outputs.values()):
        raise ValueError('Output exists; choose a new prefix rather than overwrite evidence.')
    preview = ROOT / '.preview'
    preview.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='terrain-animation-', dir=preview) as temporary:
        folder = Path(temporary)
        command = ['node', str(ROOT / 'export_terrain_animation.cjs'),
                   '--analytical', str(args.analytical.resolve()),
                   '--pymunk', str(args.pymunk.resolve()), '--frames-dir', str(folder),
                   '--fps', str(args.fps), '--label', args.label]
        if args.sharp_module:
            command += ['--sharp-module', str(args.sharp_module.resolve())]
        subprocess.run(command, check=True)
        manifest = json.loads((folder / 'render-manifest.json').read_text(encoding='utf-8'))
        samples = manifest['selections']
        images = []
        for sample in samples:
            with Image.open(folder / sample['file']) as im:
                if im.size != (manifest['width'], manifest['height']):
                    raise ValueError('Rendered frame dimensions differ.')
                images.append(im.convert('RGB'))
        contact = Image.new('RGB', (manifest['width'] * 3, manifest['height']))
        for column, index in enumerate((0, len(images) // 2, len(images) - 1)):
            contact.paste(images[index], (column * manifest['width'], 0))
        palette = contact.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
        durations = [max(10, round((b['timeS'] - a['timeS']) * 1000 / 10) * 10)
                     for a, b in zip(samples, samples[1:])] + [manifest['finalPauseMs']]
        frames[0].save(outputs['gif'], save_all=True, append_images=frames[1:],
                       duration=durations, loop=0, disposal=2, optimize=False)
        with Image.open(outputs['gif']) as check:
            if check.n_frames != len(images) or check.info.get('loop') != 0:
                raise ValueError('GIF lost saved frames or its replay loop.')
            total = 0
            for i in range(check.n_frames):
                check.seek(i); check.load(); total += check.info['duration']
            if total != sum(durations):
                raise ValueError('GIF timing differs from captured playback.')
        if outputs['gif'].stat().st_size >= 20 * 1024 * 1024:
            raise ValueError('GIF exceeds20MiB; reduce fps for this capture.')
        images[len(images) // 2].save(outputs['poster'])
        manifest.update(playbackDurationMs=sum(durations), encodedFrames=len(images),
                        gifBytes=outputs['gif'].stat().st_size,
                        gifSHA256=hashlib.sha256(outputs['gif'].read_bytes()).hexdigest(),
                        encoderSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                        outputs={k: p.name for k, p in outputs.items()},
                        cacheRetained=False,
                        limitations='Actual saved frames; no interpolation or new simulation. '
                        'One half-second final reading pause; loop resets rather than simulates a seamless cycle.')
        # Frame names are temporary implementation details; retain the exact indices/times.
        for sample in manifest['selections']:
            sample.pop('file')
        outputs['manifest'].write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(dict(outputs={k: str(v) for k, v in outputs.items()},
                          frames=manifest['encodedFrames'], bytes=manifest['gifBytes'],
                          physicalDurationS=manifest['physicalDurationS'],
                          playbackDurationMs=manifest['playbackDurationMs'])), flush=True)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analytical', type=Path, required=True)
    parser.add_argument('--pymunk', type=Path, required=True)
    parser.add_argument('--output-prefix', type=Path, required=True)
    parser.add_argument('--fps', type=int, default=20)
    parser.add_argument('--label', default='Saved terrain comparison')
    parser.add_argument('--sharp-module', type=Path)
    encode(parser.parse_args())


if __name__ == '__main__':
    main()
