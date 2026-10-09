"""Validate contribution structure and handoff records without physics dependencies.

Run: python tools/check_entry.py --base origin/main [--staged] [--require-passed]
Inputs: Git merge base and working/staged files (bytes); no physical units.
Outputs: concise diagnostics on stdout/stderr and exit 0/1; writes no files.
Limitations: checks structure and declarations, not scientific correctness or secrets.
"""

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MEMBERS = ("ali-muizz", "andy-zhang", "jonathan-xie", "yulai-duan", "jiaan-li")
BRANCH = re.compile(r"(?:members/(?:" + "|".join(MEMBERS) + r")|contributors/[a-zA-Z0-9][a-zA-Z0-9-]*)/[a-z0-9][a-z0-9-]*\Z")
ROOT_FILES = {"README.md", "CONTRIBUTING.md", "AGENTS.md", "CLAUDE.md",
              "ENTRY_TEMPLATE.md", ".gitignore", ".gitattributes"}
ROOT_DIRS = {".github", ".githooks", "assets", "simulation", "database",
             "agent_skills", "docs", "firmware", "training", "deploy", "shared", "tools",
             "context", "users"}
REQUIRED = ROOT_FILES - {".gitattributes"} | {
    ".github/CODEOWNERS", ".github/workflows/simulation-ci.yml",
    ".github/pull_request_template.md", ".githooks/pre-commit", ".githooks/pre-push",
    "assets/README.md", "assets/manifest.json", "simulation/README.md",
    "simulation/run.py", "simulation/requirements.txt",
    "simulation/config/presets/README.md", "simulation/src/environments/README.md",
    "simulation/src/controllers/README.md", "simulation/src/viewers/README.md",
    "simulation/experiments/verify_backend.py", "database/README.md",
    "database/md_research/entry-protocol.md", "database/md_research/team.md",
    "database/brainstorming_tex/README.md", "database/code_prototypes/README.md",
    "agent_skills/README.md", "agent_skills/physics_validation.md",
    "agent_skills/notion_ingestion.md", "agent_skills/git_hygiene.md",
    "agent_skills/preliminary_research.md",
    "context/README.md", "context/start-here.md", "users/README.md",
    "tools/README.md", "tools/check_entry.py", "tools/pre_push.py", "tools/physics_gate.py",
}
BLOCKED_DIRS = {"results", "runs", "checkpoints", "logs", "__pycache__", ".venv",
                "node_modules", ".pytest_cache", ".scratch", "build"}
BLOCKED_SUFFIXES = {".pyc", ".pyo", ".log", ".mp4", ".mov", ".npy", ".npz",
                    ".pt", ".pth", ".ckpt", ".pem", ".key", ".aux", ".out", ".synctex"}
HEADINGS = ("## 1. Scope & Objective", "## 2. Structural Modifications",
            "## 3. Local Validation Checklist", "## 4. Compute Saving Handoff State")
CHECKS = (
    "Executed `python simulation/run.py --headless-check` cleanly.",
    "Executed `python simulation/experiments/verify_backend.py` with zero drift.",
    "Physics limits (mass, joint constraints) verified against canonical `/assets/`.",
)
PRELIMINARY_FILES = {
    "README.md", "CONTRIBUTING.md", "AGENTS.md", "CLAUDE.md", "ENTRY_TEMPLATE.md",
    "database/README.md", "simulation/README.md", "firmware/README.md",
    "training/README.md", "deploy/README.md", "shared/README.md",
    ".github/CODEOWNERS", ".github/pull_request_template.md",
    ".github/workflows/simulation-ci.yml", ".githooks/pre-commit", ".githooks/pre-push",
    "tools/README.md", "tools/check_entry.py", "tools/physics_gate.py",
    "tools/pre_push.py", "tools/tests/test_gates.py",
}
RESEARCH_CONTENT_SUFFIXES = {".md", ".tex", ".csv", ".json", ".png", ".jpg",
                             ".jpeg", ".svg", ".pdf"}


def preliminary_path(path):
    """Allow only research artifacts, isolated prototypes and contribution policy.

    Runtime code/config, dependencies, assets and unknown paths fail closed.
    Production components must never import database/code_prototypes/.
    """
    if path in PRELIMINARY_FILES:
        return True
    suffix = PurePosixPath(path).suffix.lower()
    if path.startswith(("context/", "users/")):
        # Only Markdown context/scaffolding is exempt; app code and configs are not.
        return suffix == ".md"
    if path.startswith("docs/"):
        return suffix in RESEARCH_CONTENT_SUFFIXES
    if path.startswith(("database/md_research/", "agent_skills/")):
        return suffix == ".md"
    if path.startswith("database/brainstorming_tex/"):
        return suffix in {".md", ".tex"}
    if path.startswith("database/code_prototypes/"):
        return suffix in {".md", ".py", ".csv", ".json"}
    return False


def validation_scope(previous, current):
    """Classify the complete diff, including deletions, without trusting labels."""
    changed = {p for p in previous.keys() | current.keys()
               if previous.get(p) != current.get(p)}
    if not changed:
        return "unchanged"
    if protocol_bootstrap(previous, current):
        return "bootstrap"
    if all(preliminary_path(path) for path in changed):
        return "preliminary"
    return "physics"


def preliminary_validation_errors(log):
    """Require an explicit non-physics declaration and actual validation evidence."""
    latest = re.split(r"^## Entry: .+$", log, flags=re.MULTILINE)[-1]
    errors = []
    if not re.search(r"^- \*\*Validation Scope:\*\* preliminary\s*$", latest, re.MULTILINE):
        errors.append("Latest entry must declare '**Validation Scope:** preliminary'.")
    evidence = re.search(r"^- \*\*Research/Policy Validation:\*\* ([^\n]+)", latest, re.MULTILINE)
    if not evidence or not evidence[1].strip() or evidence[1].lstrip().startswith("["):
        errors.append("Latest entry must record actual Research/Policy Validation evidence.")
    # An exemption is not a successful canonical robot run.
    for check in CHECKS:
        if re.search(r"^- \[[xX]\] " + re.escape(check) + r"$", latest, re.MULTILINE):
            errors.append("Preliminary entries must leave canonical physics checks unchecked (not applicable).")
    return errors


def git(*args, root=ROOT):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode().strip() or "Git command failed")
    return result.stdout


def tree_files(ref, root=ROOT):
    """Read exact tracked blobs; do not honor export-ignore or follow symlinks."""
    files = {}
    for item in git("ls-tree", "-rz", ref, root=root).split(b"\0"):
        if not item:
            continue
        metadata, raw_path = item.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        path = raw_path.decode("utf-8")
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"Unsupported symlink/submodule/special file: {path}")
        size = int(git("cat-file", "-s", oid, root=root))
        if size > 1024 * 1024:
            raise ValueError(f"File exceeds 1 MiB: {path}")
        files[path] = git("cat-file", "blob", oid, root=root)
    return files


def working_files(root=ROOT):
    files = {}
    paths = set(git("ls-files", "-z", "--cached", "--others", "--exclude-standard",
                    root=root).decode().split("\0")) - {""}
    for path in sorted(paths):
        candidate = root / path
        if candidate.is_symlink() or candidate.resolve() != root.resolve() / path:
            raise ValueError(f"Symlinks are not allowed: {path}")
        if not candidate.exists():
            continue  # Deleted tracked path; still appears in change coverage below.
        if not candidate.is_file():
            raise ValueError(f"Unsupported tracked directory/submodule: {path}")
        if candidate.stat().st_size > 1024 * 1024:
            raise ValueError(f"File exceeds 1 MiB: {path}")
        files[path] = candidate.read_bytes()
    return files


def structural_errors(files):
    errors = [f"Missing required file: {p}" for p in sorted(REQUIRED - files.keys())]
    for path, content in files.items():
        parts = PurePosixPath(path).parts
        if not parts or any(part in {".", ".."} for part in parts) or path.startswith("/"):
            errors.append(f"Invalid repository path: {path}")
            continue
        if (len(parts) == 1 and path not in ROOT_FILES) or (len(parts) > 1 and parts[0] not in ROOT_DIRS):
            errors.append(f"Unapproved repository location: {path}")
        if parts[0] == "simulation" and len(parts) > 1 and parts[1] not in {
            "README.md", "run.py", "requirements.txt", "config", "src", "experiments"
        }:
            errors.append(f"Unapproved simulation location: {path}")
        if path.startswith("simulation/src/") and parts[2] not in {"environments", "controllers", "viewers"}:
            errors.append(f"Unapproved simulation source location: {path}")
        if path.startswith("simulation/config/") and parts[2] != "presets":
            errors.append(f"Configuration must live in presets: {path}")
        if parts[0] == "database" and len(parts) > 1 and parts[1] not in {
            "README.md", "md_research", "brainstorming_tex", "code_prototypes"
        }:
            errors.append(f"Unapproved database location: {path}")
        name = parts[-1]
        if (set(parts) & BLOCKED_DIRS or Path(path).suffix.lower() in BLOCKED_SUFFIXES
                or name in {".DS_Store", "MUJOCO_LOG.TXT", "credentials.json"}
                or (name.startswith(".env") and name != ".env.example")):
            errors.append(f"Generated output or local/private file: {path}")
        if len(content) > 1024 * 1024:
            errors.append(f"File exceeds 1 MiB: {path}")
        if Path(path).suffix.lower() in {".xml", ".urdf", ".stl", ".obj", ".mjb"} and parts[0] != "assets":
            errors.append(f"Model/mesh must be canonical under assets/: {path}")
        if path.endswith(".py"):
            try:
                module = ast.parse(content, filename=path)
                if not ast.get_docstring(module):
                    errors.append(f"Undocumented Python script: {path}")
            except (SyntaxError, ValueError) as exc:
                errors.append(f"Invalid Python in {path}: {exc}")
    return errors


def contribution_errors(previous, current, changed, require_passed=False):
    if not changed:
        return []
    errors = []
    if previous and not current.startswith(previous):
        return ["ENTRY_TEMPLATE.md must retain the entire previous log and append new entries."]
    appended = current[len(previous):] if previous else current.split("<!-- CONTRIBUTIONS -->", 1)[-1]
    entries = re.split(r"^## Entry: .+$", appended, flags=re.MULTILINE)[1:]
    if not entries:
        return ["Append a completed '## Entry: YYYY-MM-DD — member — task' contribution."]
    documented = set()
    for index, entry in enumerate(entries, 1):
        for heading in HEADINGS:
            if heading not in entry:
                errors.append(f"Entry {index}: missing {heading}")
        for field in ("Target Subsystem", "Associated Issue/Task", "Files Modified/Added", "API/Interface Changes"):
            match = re.search(r"\*\*" + re.escape(field) + r":\*\*\s*([^\n]+)", entry)
            if not match or match[1].strip().startswith("["):
                errors.append(f"Entry {index}: fill in {field}")
        structural = entry.split(HEADINGS[1], 1)[-1].split(HEADINGS[2], 1)[0]
        documented.update(re.findall(r"`([^`\n]+)`", structural))
        for check in CHECKS:
            pattern = r"^- \[([ xX])\] " + re.escape(check) + r"$"
            match = re.search(pattern, entry, re.MULTILINE)
            if not match or (require_passed and index == len(entries) and match[1].lower() != "x"):
                errors.append(f"Entry {index}: missing or unpassed check: {check}")
        handoff = entry.split(HEADINGS[3], 1)[-1].split("\n---", 1)[0].strip()
        if "Provide a concise" in handoff or len(handoff.split()) < 15:
            errors.append(f"Entry {index}: write the three-sentence handoff.")
    missing = changed - documented
    if missing:
        errors.append("Contribution log must list exact paths in backticks: " + ", ".join(sorted(missing)))
    return errors


def protocol_bootstrap(previous, current):
    """Allow installation once, before the target branch contains the protocol.

    The exception cannot install robot assets, controllers or environments, and
    cannot apply to a subsequent PR once ENTRY_TEMPLATE.md exists on the base.
    """
    if "ENTRY_TEMPLATE.md" in previous or "simulation/run.py" in previous:
        return False
    try:
        manifest = json.loads(current.get("assets/manifest.json", b"null"))
    except (ValueError, UnicodeError):
        return False
    if manifest != {"schema_version": 1, "status": "blocked-no-canonical-robot", "models": []}:
        return False
    bootstrap_simulation = {"simulation/run.py", "simulation/experiments/verify_backend.py",
                            "simulation/requirements.txt"}
    for path in current:
        if path.startswith("assets/") and path not in {"assets/README.md", "assets/manifest.json"}:
            return False
        if path.startswith("simulation/") and not path.endswith(".md") and path not in bootstrap_simulation:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--branch", help="CI source branch (required for detached CI checkout)")
    parser.add_argument("--require-passed", action="store_true")
    args = parser.parse_args()
    try:
        branch = args.branch or git("symbolic-ref", "--quiet", "--short", "HEAD").decode().strip()
        if not BRANCH.fullmatch(branch):
            raise ValueError(f"Use your members/<member>/<topic> branch; got {branch!r}.")
        base = git("merge-base", args.base, "HEAD").decode().strip()
        previous = tree_files(base)
        files = tree_files(git("write-tree").decode().strip()) if args.staged else working_files()
        changed = {p for p in previous.keys() | files.keys() if previous.get(p) != files.get(p)}
        scope = validation_scope(previous, files)
        errors = structural_errors(files)
        errors += contribution_errors(previous.get("ENTRY_TEMPLATE.md", b"").decode(),
                                      files.get("ENTRY_TEMPLATE.md", b"").decode(), changed,
                                      args.require_passed and scope == "physics")
        if args.require_passed and scope == "preliminary":
            errors += preliminary_validation_errors(files.get("ENTRY_TEMPLATE.md", b"").decode())
        if errors:
            for error in errors:
                print(f"FAIL: {error}")
            return 1
        print(f"PASS: entry architecture ({len(files)} files, {len(changed)} changed paths; scope={scope}).")
        return 0
    except (ValueError, UnicodeError, OSError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
