"""Restore and verify the legacy workspace without overwriting any files.

Run: python restore_archive.py --output NEW_DIRECTORY from this app root.
Inputs: adjacent archive-manifest.json, split ZIP parts and an unused output directory.
Outputs: reconstructed files plus retained .archive-package.zip, SHA-256 report.
Standard library only; no physical units, downloads or script execution.
Historical launchers/models may contain old paths; prefer the maintained apps.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise ValueError('Output must be a new directory; no files are overwritten.')
    package = json.loads((ROOT/'archive-manifest.json').read_text(encoding='utf-8'))
    output.mkdir(parents=True)
    combined = output/'.archive-package.zip'
    digest = hashlib.sha256()
    with combined.open('xb') as stream:
        for part in package['chunks']:
            path = (ROOT/part['path']).resolve()
            if not path.is_relative_to(ROOT):
                raise ValueError('Part path escapes package.')
            content = path.read_bytes()
            if len(content) != part['bytes'] or hashlib.sha256(content).hexdigest() != part['sha256']:
                raise ValueError(f'Invalid archive part: {part["path"]}')
            stream.write(content)
            digest.update(content)
    if digest.hexdigest() != package['zip_sha256']:
        raise ValueError('Combined ZIP checksum mismatch.')
    expected = {f['path']: f for f in package['files']}
    with zipfile.ZipFile(combined) as archive:
        if set(archive.namelist()) != set(expected):
            raise ValueError('Archive entries differ from inventory.')
        for name, item in expected.items():
            relative = PurePosixPath(name)
            destination = (output/name).resolve()
            if relative.is_absolute() or '\\' in name or not destination.is_relative_to(output):
                raise ValueError('Unsafe archive entry.')
            destination.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            count = 0
            with archive.open(name) as source, destination.open('xb') as target:
                while chunk := source.read(1024*1024):
                    target.write(chunk)
                    digest.update(chunk)
                    count += len(chunk)
            if count != item['bytes'] or digest.hexdigest() != item['sha256']:
                raise ValueError(f'Restored file checksum mismatch: {name}')
    print(f'PASS: restored all {len(expected)} files with exact SHA-256. '
          'No originals changed; no archived scripts executed.')


if __name__ == '__main__':
    main()
