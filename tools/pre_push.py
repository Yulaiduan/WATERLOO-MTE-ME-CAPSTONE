"""Validate each exact outgoing branch tip in a disposable checkout.

Run by .githooks/pre-push; input is Git's ref-update lines on stdin, no units.
Outputs: gate diagnostics and exit 0/1. Uses temporary directories, never resets
the user's checkout. Requires the active pinned Python environment and fetched
origin/main. Tags, branch deletions, symlinks and submodules are unsupported.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from check_entry import BRANCH, ROOT, git, tree_files


def main():
    try:
        updates = [line.split() for line in sys.stdin if line.strip()]
        base = git("rev-parse", os.environ.get("CAMEL_BASE_REF", "origin/main")).decode().strip()
        # Git hooks can export paths to the source worktree/index. They must not
        # redirect commands intended for the disposable clone back to the source.
        isolated_env = dict(os.environ)
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            isolated_env.pop(key, None)
        isolated_env["PYTHONDONTWRITEBYTECODE"] = "1"
        for local_ref, local_sha, remote_ref, remote_sha in updates:
            branch = remote_ref.removeprefix("refs/heads/")
            if not remote_ref.startswith("refs/heads/") or not BRANCH.fullmatch(branch):
                raise ValueError(f"Push only a personal branch: {remote_ref}")
            if set(local_sha) == {"0"}:
                raise ValueError("Branch deletion needs a separate maintainer operation.")
            if set(remote_sha) != {"0"}:
                result = subprocess.run(["git", "merge-base", "--is-ancestor", remote_sha, local_sha], cwd=ROOT)
                if result.returncode:
                    raise ValueError("Non-fast-forward push or unknown remote tip; fetch and integrate first.")
            # Read exact blobs without archive export-ignore or working-tree content.
            files = tree_files(local_sha)
            with tempfile.TemporaryDirectory(prefix="camel-entry-") as temporary:
                target = Path(temporary) / "repo"
                subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(target)], check=True, env=isolated_env)
                subprocess.run(["git", "checkout", "--quiet", "--detach", local_sha], cwd=target, check=True, env=isolated_env)
                subprocess.run(["git", "update-ref", "refs/remotes/origin/main", base], cwd=target, check=True, env=isolated_env)
                for path, content in files.items():
                    candidate = target / path
                    candidate.parent.mkdir(parents=True, exist_ok=True)
                    candidate.write_bytes(content)
                commands = [
                    [sys.executable, "tools/check_entry.py", "--base", base, "--branch", branch, "--require-passed"],
                    [sys.executable, "tools/physics_gate.py", "--base", base],
                ]
                for command in commands:
                    subprocess.run(command, cwd=target, check=True, env=isolated_env)
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"PUSH BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
