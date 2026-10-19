"""Restore the supplemental historical development source without executing it.

Run: python restore_development_history.py [--source PACKAGE.json] --output NEW_DIRECTORY
Inputs: default adjacent development-history-2026-10-12.json or explicit package;
v1 base64 or v2 gzip-base64 records with byte sizes and SHA-256;
no physical units or network. Outputs: exact source files under a new directory.
Limitations: historical scratch/editing/QA helpers, not maintained runnable tools;
never imports or executes payloads, modifies originals, or overwrites an output.
"""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source', type=Path,
                        default=Path(__file__).resolve().with_name('development-history-2026-10-12.json'))
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise ValueError('Output must be a new directory; no files are overwritten.')
    source = args.source
    package = json.loads(source.read_text(encoding='utf-8'))
    if package['schema'] not in ('capstone-historical-source/v1', 'capstone-historical-source/v2'):
        raise ValueError('Unknown historical source schema.')
    verified, names = [], set()
    for entry in package['files']:
        name = entry['path']
        relative = PurePosixPath(name)
        destination = (output / name).resolve()
        if (relative.is_absolute() or '\\' in name or ':' in name or '..' in relative.parts
                or not name or name in names or not destination.is_relative_to(output)):
            raise ValueError('Unsafe or duplicate historical source path.')
        names.add(name)
        content = base64.b64decode(entry['base64'], validate=True)
        if package['schema'] == 'capstone-historical-source/v2':
            if entry.get('encoding') != 'gzip-base64':
                raise ValueError('Unknown historical source encoding.')
            content = gzip.decompress(content)
        if len(content) != entry['bytes'] or hashlib.sha256(content).hexdigest() != entry['sha256']:
            raise ValueError(f'Historical source checksum mismatch: {name}')
        verified.append((destination, content))
    output.mkdir(parents=True)
    for destination, content in verified:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(content)
    print(f'PASS: restored {len(verified)} historical development files with exact SHA-256; '
          'no payload code executed and no originals changed.')


if __name__ == '__main__':
    main()
