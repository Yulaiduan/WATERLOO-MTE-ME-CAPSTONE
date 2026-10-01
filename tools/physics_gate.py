"""Run the required physics gate for an exact checked-out contribution.

Run: python tools/physics_gate.py --base origin/main
Inputs: Git base and checked-out files; physics uses SI units in the asset manifest.
Outputs: check diagnostics, exit 0/1. The first protocol-only installation is
explicitly exempt from robot validation; subsequent changed contributions are not.
"""

import argparse
import subprocess
import sys

from check_entry import ROOT, git, protocol_bootstrap, tree_files, working_files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    args = parser.parse_args()
    try:
        base = git("merge-base", args.base, "HEAD").decode().strip()
        previous = tree_files(base)
        current = working_files()
        if current == previous:
            print("No contribution changes relative to the base; no new physics to validate.")
            return 0
        if protocol_bootstrap(previous, current):
            print("PROTOCOL BOOTSTRAP ONLY: no robot assets or simulation implementation imported.")
            print("Robot physics remains BLOCKED until a canonical baseline is supplied.")
            print("This installation exception closes once the protocol exists on the target branch.")
            return 0
        for command in ([sys.executable, "simulation/run.py", "--headless-check"],
                        [sys.executable, "simulation/experiments/verify_backend.py"]):
            subprocess.run(command, cwd=ROOT, check=True)
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
