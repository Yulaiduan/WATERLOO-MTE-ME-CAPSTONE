"""Verify native Kinefold playback validation, floor law and owned lifecycle.

Run: app .venv Python verify_viewer.py [--gui]. Inputs: retained JS builder
baseline in mm/deg/kg/N and explicit engine run controls in seconds/SI units.
Outputs unittest evidence; --gui actually executes Pymunk, opens Tk, verifies
frame progress and pause/end-scrub/replay, then closes only its own windows.
Ignored .preview logs/state may be overwritten. Requires Node; GUI mode also
requires installed SciPy, Pymunk, Tk and an interactive desktop. No screenshot,
tire/contact, all-body linkage, hardware or canonical physics certification.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from desktop_viewer import floor_height, floor_points, parent_alive
from dynamic_model import Model, defaults
from dynamics import simulate
from viewer_service import ViewerService

ROOT = Path(__file__).resolve().parent
GUI = False


def baseline():
    source = "const fs=require('fs'),vm=require('vm');for(const p of ['reference-v4.js','model.js'])vm.runInThisContext(fs.readFileSync(p,'utf8'));console.log(JSON.stringify(Kinefold.defaults));"
    return json.loads(subprocess.check_output(['node', '-e', source], cwd=ROOT, text=True))


class ViewerChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = baseline()
        cls.config = {**defaults(), 'duration': .8}

    def request(self, **changes):
        return {'action': 'open', 'params': dict(self.params), 'runConfig': dict(self.config),
                'name': 'Viewer verification', **changes}

    def wait_state(self, service, wanted, timeout=30):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state, code = service.handle({'action': 'status'})
            self.assertEqual(code, 200)
            if state['state'] in wanted:
                return state
            if state['state'] == 'error':
                self.fail(str(state))
            time.sleep(.05)
        self.fail('Timed out waiting for viewer: ' + str(service.handle({'action': 'status'})))

    def test_validation_and_snapshot(self):
        service = ViewerService(ROOT)
        invalid = [None, [], {}, {'action': 'run'}, {'action': 'status', 'path': 'bad'},
                   {'action': 'close', 'pid': os.getpid()}, self.request(command='calc'),
                   self.request(name='a' * 101), self.request(name='a\nb'),
                   self.request(params={}), self.request(runConfig={}),
                   self.request(runConfig={**self.config, 'dt': float('nan')})]
        for request in invalid:
            result, code = service.handle(request)
            self.assertEqual(code, 400, result)
            self.assertIn('error', result)
        request = self.request()
        snapshot = ViewerService._validate(request)
        request['params']['m1'] = 2
        self.assertEqual(snapshot['params']['m1'], self.params['m1'])
        self.assertEqual(service.handle({'action': 'status'}), ({'state': 'closed'}, 200))
        self.assertEqual(service.handle({'action': 'close'})[1], 200)

    def test_missing_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            service = ViewerService(directory)
            data, code = service.handle(self.request())
            self.assertEqual(code, 503)
            self.assertIn('Setup Kinefold.cmd', data['error'])

    def test_start_failure_is_readable_and_retained(self):
        service = ViewerService(ROOT)
        service._runtime = lambda: Path(sys.executable)
        with mock.patch('viewer_service.subprocess.Popen', side_effect=OSError('verification start failure')):
            data, code = service.handle(self.request())
        self.assertEqual(code, 503)
        self.assertIn('verification start failure', data['error'])
        self.assertEqual(service.handle({'action': 'status'})[0], data)
        service.close()

    def test_floor_exact_event_delay_and_anchor(self):
        result = simulate({'engine': 'pymunk', 'params': self.params, 'runConfig': self.config})
        self.assertEqual(result['diagnostics']['termination'], 'duration')
        self.assertEqual(result['diagnostics']['rigidBodies'], 1)
        model = Model(self.params, self.config)
        event_rows = [row for row in result['rows'] if row.get('eventSide')]
        self.assertEqual([row['eventSide'] for row in event_rows], ['before', 'after'])
        for row, frame in zip(result['rows'], result['frames']):
            self.assertAlmostEqual(frame['A'][2], row['chassisZMm'], places=9)
            self.assertAlmostEqual(floor_height(model, row, row['CxMm']), row['wheelZMm'] - self.params['rw'], places=8)
            self.assertAlmostEqual(floor_height(model, row, row['CxMm'], False), row['requestedInputMm'], places=8)
        before, after = event_rows
        self.assertEqual(floor_height(model, before, before['CxMm']), 0)
        self.assertEqual(floor_height(model, after, after['CxMm']), 150)
        row = result['rows'][0]
        self.assertEqual(floor_height(model, row, row['CxMm'] + 49), 0)
        self.assertEqual(floor_height(model, row, row['CxMm'] + 51), 150)
        points = floor_points(model, row, row['CxMm'] - 100, row['CxMm'] + 400)
        edge = [z for x, z in points if abs(x - row['CxMm'] - 50) < 1e-8]
        self.assertEqual(edge, [0, 150])

    def test_floor_finite_rise_and_translation(self):
        config = {**self.config, 'inputRiseMm': 10}
        model = Model(self.params, config)
        row = {'t': .55, 'CxMm': 40, 'wheelZMm': 275, 'appliedInputMm': 75}
        self.assertAlmostEqual(floor_height(model, row, 40), 75, places=7)
        self.assertEqual(floor_height(model, row, 40, False), 150)
        # A fixed spatial phase moves toward -x as time advances, at fixed Cx.
        later = {**row, 't': .65}
        self.assertAlmostEqual(floor_height(model, row, 40), floor_height(model, later, 30), places=7)
        points = floor_points(model, row, -100, 400)
        self.assertGreater(len(points), 40)
        self.assertTrue(all(-1e-10 <= z <= 150 + 1e-10 for _, z in points))
        with self.assertRaisesRegex(ValueError, 'too dense'):
            floor_points(model, row, -1e7, 1e7)
        self.assertTrue(parent_alive(os.getpid()))

    def test_gui_engine_controls_and_auto_close(self):
        if not GUI:
            self.skipTest('Use --gui for actual Pymunk + visible Tk tests.')
        envelope = {'request': self.request(runConfig=defaults()), 'token': 'verify-self-test', 'parentPid': os.getpid()}
        result = subprocess.run([sys.executable, str(ROOT / 'desktop_viewer.py'), '--request-stdin', '--self-test'],
                                input=json.dumps(envelope), text=True, capture_output=True, cwd=ROOT, timeout=35)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        state = json.loads((ROOT / '.preview' / 'viewer-state.json').read_text())
        self.assertEqual(state['state'], 'closed')
        self.assertTrue(state['selfTestPassed'], state)

    def test_service_open_progress_reject_duplicate_close_restart(self):
        if not GUI:
            self.skipTest('Use --gui for service-owned native lifecycle test.')
        service = ViewerService(ROOT)
        # Verification uses its invoking installed runtime. Production resolution
        # remains exclusively the app-local .venv, with no user-supplied path.
        service._runtime = lambda: Path(sys.executable)
        sentinel = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
        try:
            data, code = service.handle(self.request(runConfig=defaults()))
            self.assertEqual(code, 202, data)
            first = service._process
            state = self.wait_state(service, {'ready'})
            self.assertEqual(state['playback'], 'prerecorded-results')
            self.assertEqual(state['frameCount'], 656)
            time.sleep(.35)
            state = self.wait_state(service, {'ready'})
            self.assertGreater(state['frameIndex'], 0)
            self.assertEqual(service.handle(self.request())[1], 409)
            self.assertEqual(service.handle({'action': 'close'})[0]['state'], 'closed')
            self.assertIsNotNone(first.poll())
            self.assertIsNone(sentinel.poll(), 'Closing playback affected an unrelated process.')
            self.assertEqual(service.handle(self.request())[1], 202)
            second = service._process
            self.assertNotEqual(first.pid, second.pid)
            self.wait_state(service, {'ready'})
            service.close()
            self.assertIsNotNone(second.poll())
        finally:
            service.close()
            sentinel.terminate()
            sentinel.wait(timeout=3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gui', action='store_true')
    args, remaining = parser.parse_known_args()
    GUI = args.gui
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)
