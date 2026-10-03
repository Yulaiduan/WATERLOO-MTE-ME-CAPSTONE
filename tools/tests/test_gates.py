"""Regression tests for contribution gates and canonical physics validation.

Run: python -m unittest discover -s tools/tests -v
Inputs: synthetic temporary Git repositories and MJCF fixtures (kg, m, rad, s).
Outputs: unittest results; temporary artifacts are removed. Fixtures are not
canonical robot assets and cannot satisfy the repository's real physics gate.
"""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "simulation/experiments"))
import check_entry as entry
import verify_backend as physics
import physics_gate as gate


def contribution(paths, checked=False):
    tick = "x" if checked else " "
    return ("## Entry: 2026-10-01 — test — regression\n"
            "## 1. Scope & Objective\n"
            "- **Target Subsystem:** simulation\n"
            "- **Associated Issue/Task:** Test validation behavior\n"
            "## 2. Structural Modifications\n"
            "- **Files Modified/Added:** " + ", ".join(f"`{p}`" for p in paths) + "\n"
            "- **API/Interface Changes:** None.\n"
            "## 3. Local Validation Checklist\n" +
            "\n".join(f"- [{tick}] {check}" for check in entry.CHECKS) +
            "\n## 4. Compute Saving Handoff State\n"
            "This temporary contribution exercises the gate. It changes no physical robot parameters. "
            "The next agent can rerun the regression suite.\n")


class ContributionTests(unittest.TestCase):
    def test_branch_names_are_member_owned_and_tool_neutral(self):
        self.assertTrue(entry.BRANCH.fullmatch("members/ali-muizz/work"))
        self.assertTrue(entry.BRANCH.fullmatch("members/andy-zhang/control-loop"))
        self.assertTrue(entry.BRANCH.fullmatch("contributors/external-user/control-loop"))
        for invalid in ("main", "members/ali-muizz", "members/unknown/task", "members/ali-muizz/../../main"):
            self.assertFalse(entry.BRANCH.fullmatch(invalid))

    def test_bootstrap_closes_after_protocol_is_on_base(self):
        files = {"assets/manifest.json": b'{"schema_version":1,"status":"blocked-no-canonical-robot","models":[]}',
                 "simulation/run.py": b'"""Scaffold."""'}
        self.assertTrue(entry.protocol_bootstrap({}, files))
        self.assertFalse(entry.protocol_bootstrap({"ENTRY_TEMPLATE.md": b"installed"}, files))
        self.assertFalse(entry.protocol_bootstrap({}, {**files, "assets/robot.xml": b"model"}))
        self.assertFalse(entry.protocol_bootstrap({}, {**files, "simulation/src/controllers/new.py": b"controller"}))

    def test_log_covers_renames_and_deletions(self):
        paths = {"simulation/src/controllers/old.py", "simulation/src/controllers/new.py", "ENTRY_TEMPLATE.md"}
        before = "# Agent Contribution Log\n"
        after = before + contribution(paths, True)
        self.assertEqual([], entry.contribution_errors(before, after, paths, True))
        errors = entry.contribution_errors(before, after, paths | {"docs/deleted.md"})
        self.assertIn("docs/deleted.md", " ".join(errors))

    def test_existing_history_cannot_be_rewritten(self):
        errors = entry.contribution_errors("old history\n", contribution({"a.md"}), {"a.md"})
        self.assertIn("retain", errors[0])

    def test_unchecked_validation_blocks_publication(self):
        text = contribution({"docs/a.md"})
        self.assertEqual([], entry.contribution_errors("", text, {"docs/a.md"}))
        self.assertEqual(3, len(entry.contribution_errors("", text, {"docs/a.md"}, True)))

    def test_missing_summary_and_empty_commits(self):
        self.assertEqual([], entry.contribution_errors("same", "same", set()))
        self.assertTrue(entry.contribution_errors("same", "same", {"docs/a.md"}))

    def test_recovered_check_preserves_failed_attempt(self):
        text = contribution({"docs/a.md"}) + "\n" + contribution({"docs/a.md"}, checked=True)
        self.assertEqual([], entry.contribution_errors("", text, {"docs/a.md"}, True))

    def test_bad_paths_artifacts_and_undocumented_scripts(self):
        cases = {"simulation/results/run.csv": b"x", "mystery/a.md": b"x",
                 "simulation/src/controllers/a.py": b"print('hello')",
                 "database/code_prototypes/model.xml": b"<mujoco/>",
                 "docs/.env.production": b"placeholder", "docs/big.bin": b"x" * (1024 * 1024 + 1)}
        errors = "\n".join(entry.structural_errors(cases))
        for path in cases:
            self.assertIn(path, errors)

    def test_staged_snapshot_is_independent_of_unstaged_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            script = root / "script.py"
            script.write_text("print('staged, undocumented')\n")
            entry.git("add", "script.py", root=root)
            script.write_text('"""Unstaged documentation fix."""\n')
            snapshot = entry.tree_files(entry.git("write-tree", root=root).decode().strip(), root=root)
            self.assertEqual(b"print('staged, undocumented')\n", snapshot["script.py"])
            self.assertNotEqual(snapshot["script.py"], entry.working_files(root)["script.py"])

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "README.md").symlink_to("/etc/hosts")
            with self.assertRaises(ValueError):
                entry.working_files(root)


class ValidationScopeTests(unittest.TestCase):
    def setUp(self):
        self.previous = {
            "ENTRY_TEMPLATE.md": b"# Existing log\n",
            "assets/manifest.json": b'{"schema_version":1,"models":[]}',
        }

    def research(self, changes=None):
        files = {"docs/study.md": b"Proposed assumptions, not validated performance."}
        files.update(changes or {})
        log = contribution(set(files) | {"ENTRY_TEMPLATE.md"})
        log = log.replace("## 3. Local Validation Checklist\n",
            "## 3. Local Validation Checklist\n"
            "- **Validation Scope:** preliminary\n"
            "- **Research/Policy Validation:** Analytical checks and reference links pass.\n")
        return {**self.previous, **files,
                "ENTRY_TEMPLATE.md": self.previous["ENTRY_TEMPLATE.md"] + log.encode()}

    def test_research_after_bootstrap_does_not_need_canonical_robot(self):
        current = self.research({"database/code_prototypes/analysis.py": b'"""Analytical research."""'})
        self.assertFalse(entry.protocol_bootstrap(self.previous, current))
        self.assertEqual("preliminary", entry.validation_scope(self.previous, current))
        with patch.object(gate.subprocess, "run") as run, redirect_stdout(StringIO()) as output:
            gate.run_validation(self.previous, current)
        self.assertEqual(1, run.call_count)
        self.assertIn("unittest", run.call_args.args[0])
        self.assertIn("NOT APPLICABLE", output.getvalue())

    def test_runtime_assets_dependencies_and_unknown_changes_require_physics(self):
        for path in ("assets/manifest.json", "assets/robot.xml", "simulation/run.py",
                     "simulation/src/controllers/control.py", "simulation/config/presets/terrain.json",
                     "simulation/experiments/new.py", "simulation/requirements.txt",
                     "firmware/main.c", "training/train.py", "shared/interface.json",
                     "deploy/Dockerfile", "tools/unknown.py", "docs/hidden.py", ".gitignore"):
            with self.subTest(path=path):
                current = self.research({path: b"changed"})
                self.assertEqual("physics", entry.validation_scope(self.previous, current))

    def test_policy_changes_can_be_reviewed_without_robot(self):
        current = self.research({"tools/physics_gate.py": b"changed",
                                 "AGENTS.md": b"Updated policy"})
        self.assertEqual("preliminary", entry.validation_scope(self.previous, current))

    def test_deleting_or_moving_runtime_into_research_still_requires_physics(self):
        previous = {**self.previous, "simulation/src/controllers/old.py": b"runtime"}
        current = self.research({"database/code_prototypes/old.py": b"runtime"})
        self.assertEqual("physics", entry.validation_scope(previous, current))

    def test_research_deletion_and_unchanged_branch(self):
        previous = {**self.previous, "docs/old.md": b"old"}
        self.assertEqual("preliminary", entry.validation_scope(previous, self.research()))
        self.assertEqual("unchanged", entry.validation_scope(previous, previous))

    def test_preliminary_declaration_never_claims_physics_pass(self):
        log = self.research()["ENTRY_TEMPLATE.md"].decode()
        self.assertEqual([], entry.preliminary_validation_errors(log))
        for invalid in (log.replace("**Validation Scope:** preliminary", "**Validation Scope:** physics"),
                        log.replace("**Research/Policy Validation:**", "**Omitted Evidence:**"),
                        log.replace("- [ ] Executed", "- [x] Executed")):
            self.assertTrue(entry.preliminary_validation_errors(invalid))

    def test_mixed_change_runs_real_checks_even_if_log_claims_preliminary(self):
        current = self.research({"simulation/run.py": b"runtime change"})
        with patch.object(gate.subprocess, "run") as run:
            gate.run_validation(self.previous, current)
        self.assertEqual(["simulation/run.py", "simulation/experiments/verify_backend.py"],
                         [call.args[0][1] for call in run.call_args_list])

    def test_validation_failures_propagate_for_both_scopes(self):
        for current in (self.research(), self.research({"assets/robot.xml": b"new"})):
            with patch.object(gate.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "check")):
                with self.assertRaises(subprocess.CalledProcessError):
                    gate.run_validation(self.previous, current)


class PhysicsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "assets").mkdir()
        self.manifest_path = self.root / "assets/manifest.json"

    def fixture(self):
        # A one-kilogram sliding test body, not a CAMEL robot.
        xml = ('<mujoco><option timestep="0.002" gravity="0 0 0"/>'
               '<worldbody><body name="test_body"><joint name="slide" type="slide" '
               'axis="0 0 1" limited="true" range="-1 1"/>'
               '<geom type="sphere" size="0.1" mass="1"/></body></worldbody></mujoco>')
        (self.root / "assets/test.xml").write_text(xml)
        manifest = {"schema_version": 1, "files": {"test.xml": hashlib.sha256(xml.encode()).hexdigest()},
                    "models": [{"path": "test.xml", "body_masses_kg": {"test_body": 1.0},
                                "joints": {"slide": {"type": "slide", "limited": True, "range": [-1, 1]}}}]}
        self.manifest_path.write_text(json.dumps(manifest))
        return manifest

    def require_physics(self):
        try:
            physics.dependencies()
        except physics.ValidationError:
            self.skipTest("Install simulation requirements for physics fixture tests.")

    def test_missing_model_fails_closed(self):
        self.manifest_path.write_text('{"schema_version": 1, "models": []}')
        with self.assertRaisesRegex(physics.ValidationError, "no canonical robot"):
            physics.check(self.root)

    def test_hash_mismatch_and_unlisted_assets_fail(self):
        self.fixture()
        (self.root / "assets/test.xml").write_text("changed")
        with self.assertRaisesRegex(physics.ValidationError, "checksum"):
            physics.load_manifest(self.root)
        self.fixture()
        (self.root / "assets/forgotten.xml").write_text("changed")
        with self.assertRaisesRegex(physics.ValidationError, "exactly all"):
            physics.load_manifest(self.root)

    def test_external_paths_fail(self):
        for path in ("../outside.xml", "/tmp/outside.xml", "C:\\outside.xml"):
            with self.assertRaises(physics.ValidationError):
                physics.asset_path(self.root / "assets", path)

    def test_finite_repeatability_and_physical_baseline(self):
        self.require_physics()
        manifest = self.fixture()
        result = physics.check(self.root, steps=10)
        self.assertEqual(0.0, result["models"][0]["max_absolute_drift"])
        self.assertEqual(1.0, result["models"][0]["total_mass_kg"])
        manifest["models"][0]["body_masses_kg"]["test_body"] = 2.0
        self.manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(physics.ValidationError, "mass mismatch"):
            physics.check(self.root, steps=10)

    def test_changed_joint_limit_fails(self):
        self.require_physics()
        manifest = self.fixture()
        manifest["models"][0]["joints"]["slide"]["range"] = [-2, 2]
        self.manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(physics.ValidationError, "joint range"):
            physics.check(self.root, steps=10)


if __name__ == "__main__":
    unittest.main()
