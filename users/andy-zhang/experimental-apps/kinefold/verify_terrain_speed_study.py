"""Check bounded speed-study capture and exact weighted metric contracts.

Run app Python: python verify_terrain_speed_study.py. Inputs synthetic unequal
time samples plus the two exact catalogue motors and saved V4.5 geometry in
kg/mm/deg/s/Nm. Outputs unittest results; no physics integration, GUI, profile
mutation or hardware validation. Model construction checks the shared spatial
terrain and additional-belt requests; actual engine runs are a separate study.
"""
import copy
import json
import math
import unittest

import terrain_speed_study as speed
from actuation_limits import torque_limit
from motor_model import Motor


class TerrainSpeedStudyTests(unittest.TestCase):
    def test_config_bounded_and_explicit(self):
        c=speed.default_config();self.assertEqual(speed.validate_config(c),c)
        self.assertEqual(len(c['candidateIds'])*len(c['speedsMps'])*2+4,20)
        self.assertEqual(c['terrain']['seed'],481)
        self.assertEqual(c['shared']['frictionSmoothingRadS'],.5)
        for key,value in (('hipBeltRatio',.9),('hipBeltRatio',3.1),('speedsMps',[.4]*4),
            ('speedsMps',[.4,1,2,3,4]),('evaluationStartDistanceMm',1800),
            ('noLoadRpm',{'odrive-8325':4800}),('candidateIds',['unknown'])):
            bad=copy.deepcopy(c);bad[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):speed.validate_config(bad)

    def test_piecewise_linear_integrals_are_time_weighted(self):
        rows=[dict(t=0,x=0),dict(t=.1,x=.1),dict(t=1,x=1)]
        m=speed.weighted_moments(rows,0,1,lambda r:r['x'])
        self.assertAlmostEqual(m['mean'],.5);self.assertAlmostEqual(m['variance'],1/12)
        self.assertAlmostEqual(m['rms'],math.sqrt(1/3))
        middle=speed.weighted_moments(rows,.2,.8,lambda r:r['x'])
        self.assertAlmostEqual(middle['mean'],.5);self.assertAlmostEqual(middle['variance'],.6**2/12)
        self.assertAlmostEqual(middle['observedSeconds'],.6)
        # Adding collinear samples cannot change a true time-weighted integral.
        dense=[dict(t=i/100,x=i/100) for i in range(101)]
        d=speed.weighted_moments(dense,.2,.8,lambda r:r['x'])
        self.assertAlmostEqual(d['rms'],middle['rms'])
        self.assertEqual(rows,[dict(t=0,x=0),dict(t=.1,x=.1),dict(t=1,x=1)])

    def test_boolean_fraction_is_left_held_and_incomplete_window_exposed(self):
        rows=[dict(t=0,on=False),dict(t=.1,on=True),dict(t=.6,on=False)]
        self.assertAlmostEqual(speed.weighted_fraction(rows,0,1,lambda r:r['on']),5/6)
        m=speed.weighted_moments(rows,0,1,lambda r:r['t'])
        self.assertAlmostEqual(m['observedSeconds'],.6)
        self.assertIsNone(speed.weighted_moments(rows,.7,1,lambda r:r['t']))
        with self.assertRaises(ValueError):speed.weighted_moments([dict(t=1),dict(t=0)],0,1,lambda r:0)

    def test_capture_uses_source_and_belt_once(self):
        c=speed.default_config();catalog=json.loads((speed.ROOT/'motor-gearbox-catalog.json').read_text(encoding='utf-8'))
        for candidate_id in speed.MOTORS:
            selected=speed.selected_hardware(c,catalog,candidate_id);hw=selected['hardware']
            request=speed.make_payload(c,selected,'terrain-stability','analytical',3.)
            native=speed.make_payload(c,selected,'terrain-stability','pymunk',3.)
            a=copy.deepcopy(request);b=copy.deepcopy(native);a.pop('engine');b.pop('engine');self.assertEqual(a,b)
            self.assertEqual(request['motorConfig']['gearRatio'],10)
            self.assertEqual(request['motorConfig']['hipBeltRatio'],2)
            self.assertEqual(request['actuatorConfig']['ratio'],10)
            self.assertEqual(request['actuatorConfig']['hipBeltRatio'],2)
            self.assertEqual(request['runConfig']['hipRotorInertiaKgM2'],0)
            self.assertEqual(request['params']['m1'],45/4)
            self.assertEqual(request['params']['alpha'],20)
            self.assertEqual(request['motorConfig']['coggingAmplitudeNm'],0)
            self.assertEqual(request['motorConfig']['coulombFrictionNm'],.05)
            self.assertAlmostEqual(Motor.resolve(request['motorConfig']).reflected_inertia,
                400*(hw['rotorInertiaKgM2']+hw['gearboxInputInertiaKgM2']))
            self.assertEqual(hw['actuatorConfig']['noLoadRpm'],c['noLoadRpm'][candidate_id])
            self.assertEqual(hw['actuatorConfig']['peakDurationS'],c['peakDurationS'][candidate_id])
            expected=selected['source']['peakShaftNm']*20*hw['actuatorConfig']['forwardEfficiency']
            self.assertAlmostEqual(torque_limit(hw['actuatorConfig'],0,1e8)['actuatorAvailableNm'],expected)
        odrive=speed.selected_hardware(c,catalog,'odrive-8325')
        self.assertAlmostEqual(odrive['source']['peakShaftNm'],6.64)
        self.assertAlmostEqual(odrive['source']['continuousShaftNm'],3.32)

    def test_exact_spatial_strip_seed_and_phase_are_shared(self):
        c=speed.default_config();catalog=json.loads((speed.ROOT/'motor-gearbox-catalog.json').read_text(encoding='utf-8'))
        candidate=speed.selected_hardware(c,catalog,'odrive-8325');reference=None
        for velocity in c['speedsMps']:
            request=speed.make_payload(c,candidate,'terrain-stability','analytical',velocity)
            self.assertAlmostEqual(request['runConfig']['duration']*velocity*1000,1800)
            self.assertAlmostEqual(request['runConfig']['inputDelayS']*velocity*1000,200)
            m=speed.validate_contact_request(request)
            signature=speed.terrain_signature(speed.terrain_spec(m,request['caseConfig'])['terrain'])
            if reference is None:reference=signature
            else:speed.assert_same_spatial_input(reference,signature)
        for mutation in ('seed','contour','phase'):
            changed=copy.deepcopy(reference)
            if mutation=='seed':changed['seed']+=1
            elif mutation=='contour':changed['contourMm'][10][2]+=.01
            else:changed['startCycle']+=1
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):speed.assert_same_spatial_input(reference,changed)

    def test_output_stays_in_app_and_fingerprint_covers_new_sources(self):
        with self.assertRaises(ValueError):speed.app_local(speed.ROOT.parent/'outside')
        h=speed.fingerprints()
        for name in ('terrain_speed_study.py','motor-gearbox-catalog.json','actuator_comparison.py',
                     'terrain_profiles.py','motor_model.py','actuation_limits.py'):
            self.assertEqual(len(h[name]),64)


if __name__=='__main__':unittest.main()
