"""Verify native Kinefold prescribed/contact rendering and owned lifecycle.

Run: app .venv Python verify_viewer.py [--gui]. Inputs: retained JS builder
baseline in mm/deg/kg/N and explicit engine run controls in seconds/SI units.
Outputs unittest evidence; --gui actually executes Pymunk, opens Tk, verifies
frame progress and pause/end-scrub/replay, then closes only its own windows.
Ignored .preview logs/state may be overwritten. Requires Node; GUI mode also
requires installed SciPy, Pymunk, Tk and an interactive desktop. No screenshot,
all-body linkage, hardware or canonical physics certification. Contact checks
verify backend dispatch and returned collision/spin data, not tire fidelity.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from desktop_viewer import (PlaybackWindow, contact_mesh, floor_height, floor_points,
                            index_endpoint, is_contact, parent_alive, simulate_snapshot)
from dynamic_model import Model, defaults
from dynamics import simulate
from contact_dynamics import validate_contact_request
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

    def contact_request(self, **changes):
        return self.request(params={**self.params, 'rw': 100, 'm6': 1.5},
                            contactConfig={'mode': 'terrain-contact', 'friction': .8,
                                           'restitution': 0, 'drive': 'free'}, **changes)

    def test_contact_validation_capture_and_fixed_dispatch(self):
        request = self.contact_request()
        validator, contact_simulator = mock.Mock(), mock.Mock(return_value={'real': 'contact'})
        module = SimpleNamespace(validate_contact_request=validator, simulate_contact=contact_simulator)
        with mock.patch.dict(sys.modules, {'contact_dynamics': module}), mock.patch('viewer_service.Model') as prescribed:
            snapshot = ViewerService._validate(request)
            prescribed.assert_not_called()
            validator.assert_called_once_with({key: value for key, value in request.items() if key not in ('action', 'name')} | {'engine': 'pymunk'})
            self.assertEqual(simulate_snapshot(snapshot), {'real': 'contact'})
            contact_simulator.assert_called_once_with(validator.call_args.args[0])
            request['contactConfig']['friction'] = .2
            self.assertEqual(snapshot['contactConfig']['friction'], .8)
            self.assertEqual(snapshot['params']['m6'], 1.5)
            self.assertEqual(snapshot['params']['rw'], 100)
        with mock.patch('desktop_viewer.simulate',return_value={'old':'prescribed'}) as old_engine:
            explicit=self.request(contactConfig={'mode':'prescribed-height','friction':.8,'restitution':0,'drive':'free'})
            snapshot=ViewerService._validate(explicit)
            self.assertEqual(simulate_snapshot(snapshot),{'old':'prescribed'})
            old_engine.assert_called_once()
        for contact in (None, {}, {'mode': 'prescribed'}, {'mode': 'contact_dynamics.py'}):
            data, status = ViewerService(ROOT).handle(self.request(contactConfig=contact))
            self.assertEqual(status, 400, data)
        with mock.patch('desktop_viewer.simulate', return_value={'old': 'prescribed'}) as prescribed:
            self.assertEqual(simulate_snapshot(self.request()), {'old': 'prescribed'})
            prescribed.assert_called_once_with({'engine': 'pymunk', 'params': self.params, 'runConfig': self.config})

    def test_contact_mesh_is_returned_world_geometry_and_spin(self):
        result = {'schema': 'kinefold/contact-v1', 'scope': {'mode': 'terrain-contact'},
                  'terrain': {'baseSegmentMm': [[-1000, 0, 0], [1000, 0, 0]]}}
        polygon = [[40, 0, 0], [40, 0, 150], [190, 0, 150], [190, 0, 0]]
        frame = {'terrainOffsetMm': [-20, 0, 0], 'terrainPolygonsMm': [polygon]}
        polygons, base = contact_mesh(result, frame)
        self.assertEqual(polygons, [[(40, 0), (40, 150), (190, 150), (190, 0)]])
        self.assertEqual(base, [(-1020, 0), (980, 0)])
        self.assertEqual(contact_mesh(result, {**frame, 't': 123, 'CxMm': 9999, 'wheelZMm': -9999}), (polygons, base))
        self.assertTrue(is_contact(result))
        self.assertFalse(is_contact({'schema': 'kinefold/contact-v1', 'scope': {'mode': 'prescribed-input'}}))
        with self.assertRaises(ValueError):
            contact_mesh({}, frame)
        self.assertEqual(index_endpoint([12, 0, 300], 100, 0), (-88, 300))
        x, z = index_endpoint([12, 0, 300], 100, 90)
        self.assertAlmostEqual(x, 12)
        self.assertAlmostEqual(z, 400)

    def test_real_contact_result_draw_never_calls_prescribed_input(self):
        if importlib.util.find_spec('contact_dynamics') is None:
            self.skipTest('Contact backend must be integrated or supplied on PYTHONPATH.')
        request = self.contact_request()
        result = simulate_snapshot(ViewerService._validate(request))
        self.assertTrue(is_contact(result))
        self.assertEqual(result['params']['rw'], 100)
        self.assertEqual(result['params']['m6'], 1.5)
        # Exercise the full native drawing path without taking over the desktop.
        window = PlaybackWindow.__new__(PlaybackWindow)
        window.result, window.contact = result, True
        window.model = validate_contact_request({key: result[key] for key in ('engine', 'params', 'runConfig', 'contactConfig', 'caseConfig') if key in result})
        window.rows, window.frames = result['rows'], result['frames']
        window.times = [row['t'] for row in window.rows]
        window.index = len(window.frames) - 1
        window.canvas, window.clock, window.readout = mock.Mock(), mock.Mock(), mock.Mock()
        window.canvas.winfo_width.return_value = 1100
        window.canvas.winfo_height.return_value = 450
        window.bounds = (-500, 500, -100, 1000)
        with mock.patch('desktop_viewer.floor_points', side_effect=AssertionError('Contact must not prescribe the floor.')):
            window._bounds()
            window.index=0
            window.draw()  # Initial/airborne slip is None, never a formatting error.
            window.index=len(window.frames)-1
            window.draw()
        self.assertTrue(window.canvas.create_polygon.called)
        self.assertIn('actual spin', window.readout.configure.call_args.kwargs['text'])
        self.assertNotIn('input reaction', window.readout.configure.call_args.kwargs['text'])
        for frame in window.frames:
            self.assertEqual(frame['A'], frame['actualA'])
            self.assertEqual(frame['C'], frame['actualC'])
        self.assertGreater(abs(window.frames[-1]['wheelAngle'] - window.frames[0]['wheelAngle']), .01)

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

    def test_gui_contact_controls_and_auto_close(self):
        if not GUI:
            self.skipTest('Use --gui for actual contact Pymunk + visible Tk tests.')
        envelope = {'request': self.contact_request(), 'token': 'verify-contact-self-test', 'parentPid': os.getpid()}
        result = subprocess.run([sys.executable, str(ROOT / 'desktop_viewer.py'), '--request-stdin', '--self-test'],
                                input=json.dumps(envelope), text=True, capture_output=True, cwd=ROOT, timeout=35)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        state = json.loads((ROOT / '.preview' / 'viewer-state.json').read_text())
        self.assertEqual(state['state'], 'closed')
        self.assertTrue(state['selfTestPassed'], state)

    def test_gui_constant_force_payout_witness(self):
        if not GUI:
            self.skipTest('Use --gui for actual constant-force Tk canvas drawing.')
        request = self.request(params={**self.params, 'm6': 1.5, 'springLaw': 'constant'},
                               contactConfig={'mode': 'terrain-contact', 'friction': .8, 'restitution': 0, 'drive': 'free'},
                               runConfig={**self.config, 'duration': .3, 'dt': .00025, 'inputHeightMm': 0})
        result = simulate_snapshot(ViewerService._validate(request))
        window = PlaybackWindow(result, 'Constant cable force verification', mock.Mock(), os.getpid())
        try:
            window.root.update_idletasks()
            vectors = []
            for index in (0, len(window.frames) - 1):
                window.index = index
                window.draw()
                items = window.canvas.find_withtag('spring-payout-witness')
                self.assertEqual(len(items), 1)
                x1, y1, x2, y2 = window.canvas.coords(items[0])
                vectors.append((x2 - x1, y2 - y1))
            self.assertGreater(sum(abs(a - b) for a, b in zip(*vectors)), 5)
            self.assertTrue(all(row['Fs'] == self.params['p0'] for row in result['rows']))
        finally:
            window.close()

    def test_case_capture_and_native_jump_draw(self):
        from contact_cases import CASE_DEFAULTS
        request=self.request(params={**self.params,'rw':200,'m6':1.5},contactConfig={'mode':'terrain-contact','friction':.8,'restitution':0,'drive':'free'},caseConfig={**CASE_DEFAULTS,'kind':'jump'},runConfig={**self.config,'dt':.00025})
        captured=ViewerService._validate(request)
        result=simulate_snapshot(captured)
        self.assertEqual(result['caseConfig']['kind'],'jump')
        self.assertEqual(result['terrain']['translationVelocityMmS'],[0,0,0])
        self.assertEqual(captured['caseConfig']['undersideOffsetMm'],50)
        window=PlaybackWindow.__new__(PlaybackWindow)
        window.result,window.contact=result,True
        window.model=validate_contact_request({key:result[key] for key in ('engine','params','runConfig','contactConfig','caseConfig') if key in result})
        window.rows,window.frames=result['rows'],result['frames']
        window.times=[row['t'] for row in window.rows]
        window.index=0
        window.canvas,window.clock,window.readout=mock.Mock(),mock.Mock(),mock.Mock()
        window.canvas.winfo_width.return_value=1100
        window.canvas.winfo_height.return_value=450
        window._bounds();window.draw();window.index=len(window.frames)-1;window.draw()
        self.assertIn('phase',window.readout.configure.call_args.kwargs['text'])
        self.assertEqual(result['frames'][0]['theta2'],self.params['tc'])

    def test_gui_jump_case_controls_and_auto_close(self):
        if not GUI:self.skipTest('Use --gui for actual case playback and Tk controls.')
        from contact_cases import CASE_DEFAULTS
        request=self.request(params={**self.params,'rw':200,'m6':1.5},contactConfig={'mode':'terrain-contact','friction':.8,'restitution':0,'drive':'free'},caseConfig={**CASE_DEFAULTS,'kind':'jump'},runConfig={**self.config,'dt':.00025})
        envelope={'request':request,'token':'verify-jump-self-test','parentPid':os.getpid()}
        result=subprocess.run([sys.executable,str(ROOT/'desktop_viewer.py'),'--request-stdin','--self-test'],input=json.dumps(envelope),text=True,capture_output=True,cwd=ROOT,timeout=35)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        state=json.loads((ROOT/'.preview'/'viewer-state.json').read_text())
        self.assertTrue(state['selfTestPassed'],state)

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
