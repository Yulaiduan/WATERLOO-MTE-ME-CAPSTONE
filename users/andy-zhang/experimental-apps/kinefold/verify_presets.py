"""Check independent preset persistence, rollback and JS/Python validation parity.

Run python verify_presets.py (installed Node required). Inputs are synthetic
builder mm/deg/kg/N and solver/motor SI fixtures emitted by verify-presets.cjs.
Outputs unittest results; only temporary directories are written, no HTTP server
or live profiles are opened. These tests establish storage safety, not physics.
"""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from profile_service import ProfileService
from preset_service import SCHEMA, BUNDLE_SCHEMA, validate_record

CORPUS = json.loads(subprocess.check_output(['node', str(Path(__file__).with_name('verify-presets.cjs')), '--fixtures'], text=True))


class PresetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.service = ProfileService(self.root)
        self.data = copy.deepcopy(CORPUS['data'])

    def call(self, action, status=200, **values):
        result, actual = self.service.handle(dict(action=action, **values))
        self.assertEqual(actual, status, result)
        self.assertEqual(result['ok'], status == 200)
        return result

    def save(self, key, revision):
        return self.call('preset-save', expectedRevision=revision, record=self.data[key])

    def test_mirrored_js_validation_corpus(self):
        for case in CORPUS['cases']:
            with self.subTest(case=case['label']):
                if case['valid']:
                    self.assertEqual(validate_record(case['record']), case['record'])
                else:
                    with self.assertRaises((ValueError, TypeError)):
                        validate_record(case['record'])

    def test_independent_library_and_export_unchanged(self):
        self.assertEqual(self.call('preset-list')['revision'], 0)
        original = b'{"deliberately":"unreadable existing library"}'
        (self.root / 'profiles/library.json').write_bytes(original)
        self.save('s', 0)
        self.assertEqual((self.root / 'profiles/library.json').read_bytes(), original)
        self.assertFalse((self.root / 'profiles/browser-backup.json').exists())
        export = self.call('export', name='presets', mime='application/json', content=json.dumps(dict(schema=BUNDLE_SCHEMA, presets=[self.data['s']])))
        self.assertTrue((self.root / export['path']).is_file())
        self.assertEqual(self.call('preset-list')['revision'], 1)

    def test_roundtrip_version_conflicts_and_reload(self):
        state = self.save('a', 0)
        self.assertEqual(state['presets'], [self.data['a']])
        self.assertEqual(ProfileService(self.root).handle({'action': 'preset-list'})[0], state)
        self.call('preset-save', status=409, expectedRevision=0, record=self.data['s'])
        self.call('preset-save', status=409, expectedRevision=1, record=self.data['a'])
        revised = copy.deepcopy(self.data['a'])
        revised.update(version=2, name='Revised')
        self.call('preset-save', expectedRevision=1, record=revised)
        revised['kind'] = 'input'
        revised['values'] = self.data['i']['values']
        revised['version'] = 3
        self.call('preset-save', status=409, expectedRevision=2, record=revised)
        self.assertEqual(self.call('preset-list')['presets'][0]['name'], 'Revised')

    def test_study_frozen_when_component_updated_deleted(self):
        self.save('a', 0)
        self.save('study', 1)
        revised = copy.deepcopy(self.data['a'])
        revised['version'] = 2
        revised['values']['motorConfig']['gearRatio'] = 50
        self.call('preset-save', expectedRevision=2, record=revised)
        state = self.call('preset-remove', expectedRevision=3, id=revised['id'])
        self.assertEqual(state['presets'], [self.data['study']])
        self.call('preset-save', status=409, expectedRevision=4, record=self.data['study'])

    def test_import_copies_all_records_atomically_retains_inner_provenance(self):
        self.save('study', 0)
        bundle = dict(schema=BUNDLE_SCHEMA, presets=[self.data['study'], self.data['a']])
        state = self.call('preset-import', expectedRevision=1, bundle=bundle)
        self.assertEqual(state['revision'], 2)
        self.assertEqual(len(state['presets']), 3)
        self.assertNotEqual(state['presets'][1]['id'], self.data['study']['id'])
        self.assertEqual(state['presets'][1]['values'], self.data['study']['values'])
        self.assertNotEqual(state['presets'][2]['id'], self.data['a']['id'])
        self.assertEqual(bundle['presets'][0], self.data['study'])
        before = (self.root / 'profiles/presets.json').read_bytes()
        bad = copy.deepcopy(bundle)
        bad['presets'][1]['values']['motorConfig']['gearRatio'] = 0
        self.call('preset-import', status=400, expectedRevision=2, bundle=bad)
        self.assertEqual((self.root / 'profiles/presets.json').read_bytes(), before)
        self.call('preset-import', status=400, expectedRevision=2, bundle=dict(schema=BUNDLE_SCHEMA, presets=[self.data['a'], self.data['a']]))
        self.assertEqual((self.root / 'profiles/presets.json').read_bytes(), before)

    def test_atomic_write_failure_and_import_failure_leave_original_bytes(self):
        self.save('s', 0)
        path = self.root / 'profiles/presets.json'
        before = path.read_bytes()
        with patch('profile_service.os.replace', side_effect=OSError('test failure')):
            self.save_failure('a', 1)
            self.call('preset-import', status=500, expectedRevision=1, bundle=dict(schema=BUNDLE_SCHEMA, presets=[self.data['a'], self.data['study']]))
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(list(path.parent.glob('.write-*')), [])
        self.assertEqual(self.call('preset-list')['revision'], 1)

    def save_failure(self, key, revision):
        self.call('preset-save', status=500, expectedRevision=revision, record=self.data[key])

    def test_corrupt_presets_retained_and_original_profiles_still_work(self):
        self.call('preset-list')
        path = self.root / 'profiles/presets.json'
        path.write_text('{broken', encoding='utf-8')
        self.call('preset-list', status=422)
        self.assertEqual(path.read_text(), '{broken')
        self.assertEqual(self.call('list')['revision'], 0)
        self.assertFalse(self.service.file.exists())

    def test_strict_request_shape_unknown_actions_missing_revisions(self):
        for request in ({'action': 'preset-list', 'id': 'x'}, {'action': 'preset-save', 'record': self.data['a']}, {'action': 'preset-bad'}):
            self.assertEqual(self.service.handle(request)[1], 400)
        self.call('preset-save', status=409, expectedRevision=True, record=self.data['a'])
        self.call('preset-save', status=400, expectedRevision=0, record=dict(self.data['a'], version=2))
        self.assertEqual(self.call('preset-list')['presets'], [])

    def test_library_capacity_import_rolls_back_every_copy(self):
        self.save('a', 0)
        records = []
        for index in range(200):
            record = copy.deepcopy(self.data['a'])
            record['id'] = 'preset-import-' + str(index)
            records.append(record)
        path = self.root / 'profiles/presets.json'
        before = path.read_bytes()
        self.call('preset-import', status=400, expectedRevision=1,
                  bundle=dict(schema=BUNDLE_SCHEMA, presets=records))
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.call('preset-list')['revision'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
