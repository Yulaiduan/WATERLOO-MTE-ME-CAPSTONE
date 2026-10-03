"""Run the required physics gate for an exact checked-out contribution.

Run: python tools/physics_gate.py --base origin/main
Inputs: Git base and checked-out files; physics uses SI units in the asset manifest.
Outputs: check diagnostics, exit 0/1. Preliminary research/contribution-policy
changes run gate regressions and do not claim canonical robot validation.
Runtime, assets, dependencies and unclassified changes require actual physics.
"""

import argparse
import subprocess
import sys

from check_entry import (ROOT, git, preliminary_validation_errors,
                         tree_files, validation_scope, working_files)


def run_validation(previous, current):
    """Run the applicable checks; a mixed research/runtime diff requires physics."""
    scope = validation_scope(previous, current)
    if scope == "unchanged":
        print("No contribution changes relative to the base; no new physics to validate.")
        return
    if scope == "bootstrap":
        print("PROTOCOL BOOTSTRAP ONLY: no robot assets or simulation implementation imported.")
        print("Robot physics remains BLOCKED until a canonical baseline is supplied.")
        print("This installation exception closes once the protocol exists on the target branch.")
        return
    if scope == "preliminary":
        errors = preliminary_validation_errors(current.get("ENTRY_TEMPLATE.md", b"").decode())
        if errors:
            raise ValueError(" ".join(errors))
        subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tools/tests", "-v"],
                       cwd=ROOT, check=True)
        print("PASS: preliminary research/contribution-policy checks.")
        print("Canonical robot physics: NOT APPLICABLE to these changed paths; no physics pass claimed.")
        return
    for command in ([sys.executable, "simulation/run.py", "--headless-check"],
                    [sys.executable, "simulation/experiments/verify_backend.py"]):
        subprocess.run(command, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    args = parser.parse_args()
    try:
        base = git("merge-base", args.base, "HEAD").decode().strip()
        previous = tree_files(base)
        current = working_files()
        run_validation(previous, current)
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
