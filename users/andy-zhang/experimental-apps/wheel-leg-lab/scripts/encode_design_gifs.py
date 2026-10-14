"""Encode browser-rendered design frames into compact labelled GIF illustrations.

Run: python scripts/encode_design_gifs.py --frames artifacts/design-gif-frames --output web/design-examples/gifs
Inputs: PNG frame folders from export_design_examples.cjs; actual renderer pixels,
600x720 px, 48 frames over an illustrative 4.8-second prescribed-motion cycle.
Outputs: ten looping GIFs and sizes on stdout. Requires optional pinned Pillow.
Limits: visualization only; timing is not a motor rating or physical simulation.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frames',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    records=[]
    for folder in sorted(args.frames.iterdir()):
        if not folder.is_dir():continue
        paths=sorted(folder.glob('*.png'))
        if len(paths)!=48:raise ValueError(f'{folder.name}: expected 48 frames, got {len(paths)}')
        images=[Image.open(p).convert('RGB') for p in paths]
        # One adaptive palette across the complete cycle avoids color flicker.
        samples=Image.new('RGB',(600,720*len(images)))
        for i,im in enumerate(images):samples.paste(im,(0,720*i))
        palette=samples.quantize(colors=96,method=Image.Quantize.MEDIANCUT)
        frames=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in images]
        target=args.output/(folder.name+'.gif')
        frames[0].save(target,save_all=True,append_images=frames[1:],duration=100,loop=0,
                       optimize=True,disposal=1)
        if target.stat().st_size>1048576:raise ValueError(f'{target.name}: exceeds repository 1 MiB limit')
        with Image.open(target) as check:
            assert check.n_frames==48 and check.size==(600,720),target
            assert check.info['loop']==0
            duration=0
            for i in range(check.n_frames):check.seek(i);duration+=check.info['duration']
            assert duration==4800,(target,duration)
        records.append(dict(file=target.name,bytes=target.stat().st_size,frames=48,
                            cycle_ms=4800,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    print(json.dumps(records,indent=2))


if __name__=='__main__':main()
