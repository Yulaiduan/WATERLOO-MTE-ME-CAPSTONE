"""Verify local profile storage without starting the Kinefold server.

Run: python verify_profiles.py. Inputs are temporary project-v3 mm/deg/kg/N/SI
fixtures, competing revisions and simulated I/O errors. Outputs are unittest
results; all generated profiles/exports stay in temporary directories. This
checks storage contracts, not HTTP guards, browser layout or physical behavior.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from profile_service import MAX_BYTES, ProfileService


def project(name="Saved design", angle=140.8954):
    params = dict(L2=300, L3=300, ra=50, rb=25, rc=35, rd=35, re=25, rf=25, rw=200, alpha=0, phi0=0, te=100, tc=165, m1=8.75, m2=0, m3=0, m5=0, m6=0, g=9.81, beta=0, Fn=85.8375, Ft=0, Fz=85.8375, loadMode="weight", Tab0=0, Tcd0=0, Tef0=0, springEnabled=True, springK=8, hornR=62.22694951186731, Sv=100, rs=10, p0=330.8692828089511, nu=0, Su=9.387776728149294, Fx=0, springLaw="v4", theta2=angle)
    config = dict(fixture="floating-chassis", duration=6.5, dt=.001, outputHz=100, initialVelocityDegS=0, hipTorqueNm=0, dampingNms=0, hipRotorInertiaKgM2=0, inertiaModel="uniform-rods-discs", I2=0, I3=0, I5=0, I6=0, iterations=80, inputHeightMm=150, inputPlateauMm=150, inputGapMm=150, inputSpeedMmS=100, inputRiseMm=0, inputDelayS=.5)
    view = {k: True for k in "labels dimensions belts path axes grid indices beltMarkers".split()}
    view.update(projection="side", loads=False)
    return dict(schema="kinefold/project-v3", id="design-11111111-1111-4111-8111-111111111111", name=name, params=params, view=view, solverConfig=config, createdAt="2026-10-22T10:00:00Z", updatedAt="2026-10-22T10:00:00Z")


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.service = ProfileService(self.root)

    def call(self, action, status=200, **values):
        body, actual = self.service.handle(dict(action=action, **values))
        self.assertEqual(actual, status, body)
        self.assertEqual(body["ok"], status == 200)
        return body

    def migrate(self):
        first, second, working = project("First", 132.5), project("Second", 145), project("Unsaved current", 140.8954)
        second["id"] = "design-22222222-2222-4222-8222-222222222222"
        raw = {"kinefold-project-v3": json.dumps(working), "kinefold-library-v3": json.dumps({"schema": "kinefold/library-v3", "designs": [first, second]})}
        return self.call("migrate", expectedRevision=0, designs=[first, second], working=working, browserBackup=raw), raw

    def test_migration_exact_working_pose_two_saved_designs_and_reload(self):
        state, raw = self.migrate()
        self.assertEqual(len(state["designs"]), 2)
        self.assertEqual(state["working"]["params"]["theta2"], 140.8954)
        self.assertEqual(json.loads((self.root / "profiles/browser-backup.json").read_text())["keys"], raw)
        self.assertEqual(ProfileService(self.root).handle({"action": "list"})[0], state)

    def test_optional_case_roundtrip_preserves_all_originals(self):
        state, _ = self.migrate()
        originals = copy.deepcopy(state['designs'])
        case = project('Landing study')
        case['id'] = 'design-case-4444'
        case['caseConfig'] = dict(kind='landing',jumpTorqueNm=20,landingDropMm=250,landingOpenFraction=2/3,landingBrakeTorqueNm=20,landingBrakeLimitNm=200,brakeStrategy='entered',undersideOffsetMm=50,energyMethod=True)
        saved = self.call('save', project=case, expectedRevision=state['revision'])
        self.assertEqual(saved['designs'][:2], originals)
        self.assertEqual(self.call('read', id=case['id'])['project'], case)
        self.assertNotIn('caseConfig', originals[0])
        for key, invalid in [('kind','unknown'),('landingDropMm',-1),('undersideOffsetMm',5001),('energyMethod','yes')]:
            broken = copy.deepcopy(case)
            broken['caseConfig'][key] = invalid
            self.call('save', status=400, project=broken, expectedRevision=saved['revision'])

    def test_optional_contact_roundtrip_preserves_legacy_profiles(self):
        state, _ = self.migrate()
        originals = copy.deepcopy(state["designs"])
        contact = project("Explicit contact demo")
        contact["id"] = "design-contact-3333"
        contact["params"]["m6"] = 1.5
        contact["contactConfig"] = dict(mode="terrain-contact", friction=.8, restitution=0, drive="free")
        saved = self.call("save", project=contact, expectedRevision=state["revision"])
        self.assertEqual(saved["designs"][:2], originals)
        self.assertEqual(self.call("read", id=contact["id"])["project"], contact)
        self.assertNotIn("contactConfig", originals[0])
        invalid = copy.deepcopy(contact)
        invalid["contactConfig"]["drive"] = "locked"
        self.call("save", status=400, project=invalid, expectedRevision=saved["revision"])

    def test_save_read_delete_restore_and_revision_conflict(self):
        state, _ = self.migrate()
        p = state["designs"][0]
        p["name"] = "Renamed"
        saved = self.call("save", project=p, expectedRevision=1)
        self.assertEqual(self.call("read", id=p["id"])["project"]["name"], "Renamed")
        self.call("working", status=409, project=p, expectedRevision=1)
        self.assertEqual(self.call("list")["working"]["params"]["theta2"], 140.8954)
        removed = self.call("remove", id=p["id"], expectedRevision=saved["revision"])
        self.assertEqual(len(removed["designs"]), 1)
        restored = self.call("save", project=p, expectedRevision=removed["revision"])
        self.assertEqual(len(restored["designs"]), 2)

    def test_competing_service_instances_reject_lost_updates(self):
        state, _ = self.migrate()
        other = ProfileService(self.root)
        self.call("working", expectedRevision=state["revision"], project=project("Tab one"))
        response, status = other.handle(dict(action="working", expectedRevision=state["revision"], project=project("Tab two")))
        self.assertEqual(status, 409, response)
        self.assertEqual(self.call("list")["working"]["name"], "Tab one")

    def test_failed_replace_preserves_original_bytes(self):
        self.migrate()
        original = self.service.file.read_bytes()
        with patch("profile_service.os.replace", side_effect=OSError("Simulated disk failure")):
            self.call("working", status=500, expectedRevision=1, project=project("Must not persist"))
        self.assertEqual(self.service.file.read_bytes(), original)
        self.assertEqual(list((self.root / "profiles").glob(".write-*")), [])

    def test_backup_remains_immutable_and_repeat_migration_is_idempotent(self):
        self.migrate()
        backup = (self.root / "profiles/browser-backup.json").read_bytes()
        self.call("migrate", expectedRevision=1, designs=[], working=None, browserBackup={})
        self.assertEqual((self.root / "profiles/browser-backup.json").read_bytes(), backup)
        self.assertEqual(len(self.call("list")["designs"]), 2)

    def test_corrupt_disk_fails_explicitly_without_overwriting(self):
        self.migrate()
        for data in (b"broken JSON", b'{"schema":"kinefold/disk-library-v1"}'):
            self.service.file.write_bytes(data)
            self.call("list", status=422)
            self.call("working", status=422, project=project(), expectedRevision=1)
            self.assertEqual(self.service.file.read_bytes(), data)

    def test_bad_profile_types_fields_numbers_and_limits(self):
        for change in (lambda p: p.update(id=123), lambda p: p["params"].update(L2=float("inf")), lambda p: p["params"].update(m2=-1), lambda p: p["params"].update(theta2=999), lambda p: p["params"].update(unexpected=1), lambda p: p["view"].update(labels="true"), lambda p: p["solverConfig"].update(duration=31), lambda p: p["solverConfig"].update(inputRiseMm=76), lambda p: p.update(createdAt="2026-99-99T00:00:00Z")):
            bad = project()
            change(bad)
            result, status = self.service.handle(dict(action="save", expectedRevision=0, project=bad))
            self.assertEqual(status, 400, result)
            self.assertFalse(self.service.file.exists())

    def test_duplicate_ids_and_limit_fail_without_new_library(self):
        self.call("migrate", status=400, expectedRevision=0, designs=[project(), project()], working=None, browserBackup={})
        self.call("migrate", status=400, expectedRevision=0, designs=[project()] * 201, working=None, browserBackup={})
        self.assertFalse(self.service.file.exists())

    def test_zero_gravity_static_profiles_remain_saveable(self):
        p = project()
        p["params"]["g"] = 0
        state = self.call("working", expectedRevision=0, project=p)
        self.assertEqual(state["working"]["params"]["g"], 0)

    def test_exports_use_app_folder_unique_names_exact_content(self):
        content = json.dumps({"comparison": "x" * (6 * 1024 * 1024)})
        first = self.call("export", name="Comparison results.json", content=content, mime="application/json")["path"]
        second = self.call("export", name="Comparison results.json", content=content, mime="application/json")["path"]
        self.assertNotEqual(first, second)
        self.assertTrue(first.startswith("exports/Comparison-results-"))
        self.assertEqual((self.root / first).read_text(encoding="utf-8"), content)
        csv = "time_s,value\n0,1\n"
        output = self.call("export", name="run.csv", content=csv, mime="text/csv")["path"]
        self.assertEqual((self.root / output).read_bytes(), csv.encode())

    def test_export_paths_formats_and_oversized_body_are_rejected(self):
        for name in ("../escape.json", "C:\\escape.json", "/tmp/escape.json", "bad\nname.json"):
            self.call("export", status=400, name=name, content="{}", mime="application/json")
        self.call("export", status=400, name="bad.json", content="{broken", mime="application/json")
        self.call("export", status=400, name="infinite.json", content='{"n":1e999}', mime="application/json")
        self.call("export", status=400, name="bad.html", content="x", mime="text/html")
        self.call("export", status=413, name="big.csv", content="x" * MAX_BYTES, mime="text/csv")
        self.assertFalse((self.root / "exports").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
