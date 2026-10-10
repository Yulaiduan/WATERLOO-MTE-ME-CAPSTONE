"""Preserve the inventoried legacy workspace as small, checksummed ZIP parts.

Run: python scripts/create_archive.py --source ARCHIVE --inventory MANIFEST.
Inputs: original file inventory with byte sizes/SHA-256; no physical units.
Outputs: archive-manifest.json, payload/parts and an ignored staging ZIP in this app.
Standard library only. Copies source/evidence/outputs without executing them;
installed dependencies, bytecode, server logs and rebuildable dist stay local.
Existing payloads are never overwritten. This is history, not active app code.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'node_modules', '.venv', '__pycache__', '.preview', 'dist', '.git'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--inventory', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    inventory = json.loads(args.inventory.read_text(encoding='utf-8'))
    selected = [f for f in inventory['files']
                if not EXCLUDED.intersection(Path(f['path']).parts)]
    payload = ROOT/'payload'
    if (ROOT/'archive-manifest.json').exists() or list(payload.glob('*.part')):
        raise ValueError('Archive already exists; refusing to overwrite.')
    payload.mkdir(parents=True, exist_ok=True)
    staging = ROOT/'.staging'
    staging.mkdir(exist_ok=True)
    combined = staging/'legacy-workspace.zip'
    with zipfile.ZipFile(combined, 'x', zipfile.ZIP_DEFLATED,
                         compresslevel=9) as archive:
        for item in selected:
            relative = Path(item['path'])
            path = (source/relative).resolve()
            if not path.is_relative_to(source):
                raise ValueError('Inventory path escapes source.')
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != item['sha256']:
                raise ValueError(f'Source changed: {relative}')
            entry = zipfile.ZipInfo(relative.as_posix(), (2026, 10, 10, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, content, compresslevel=9)
    chunks = []
    digest = hashlib.sha256()
    with combined.open('rb') as stream:
        for index in range(10000):
            content = stream.read(900_000)
            if not content:
                break
            name = f'payload/legacy-workspace-{index:04d}.part'
            with (ROOT/name).open('xb') as output:
                output.write(content)
            chunks.append({'path': name, 'bytes': len(content),
                           'sha256': hashlib.sha256(content).hexdigest()})
            digest.update(content)
    result = {'format': 'split-zip-v1', 'date': '2026-10-10',
              'scope': 'Legacy source, documentation, references, data and outputs',
              'excluded_categories': sorted(EXCLUDED),
              'local_only_file_count': len(inventory['files'])-len(selected),
              'zip_sha256': digest.hexdigest(), 'chunks': chunks, 'files': selected}
    (ROOT/'archive-manifest.json').write_text(json.dumps(result, indent=2)+'\n',
                                   encoding='utf-8', newline='\n')
    print(f'Packaged {len(selected)} files in {len(chunks)} parts; '
          f'{combined.stat().st_size:,} ZIP bytes; originals untouched.')


if __name__ == '__main__':
    main()
