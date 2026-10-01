"""Portable agent entry point for canonical headless simulation validation.

Run: python simulation/run.py --headless-check
Inputs: assets/manifest.json and canonical MJCF, with SI units.
Outputs: JSON evidence on stdout and exit 0/1. No GUI or generated files.
Interactive environments and controller scenarios have not yet been imported.
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET

from experiments.verify_backend import check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headless-check", action="store_true", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(check(repeat=False), indent=2))
        return 0
    except (ValueError, RuntimeError, OSError, ET.ParseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
