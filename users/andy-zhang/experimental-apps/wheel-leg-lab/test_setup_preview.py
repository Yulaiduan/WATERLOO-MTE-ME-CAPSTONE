"""Verify initial preview geometry, with no integration or invented load results.

Run: python -m unittest test_setup_preview. Inputs: catalog SI demo profiles;
outputs: assertions for geometry/build validation, not hardware acceptance.
"""
import json
import math
import unittest
from unittest.mock import patch
from physics import DEFAULTS
from setup_preview import preview
from spring_mechanisms import CATALOG, apply_preset
from suspension_architecture import constant_lift_profile


class SetupPreviewTests(unittest.TestCase):
    def test_every_catalog_preset_builds_without_stepping_or_load_rows(self):
        with patch('pymunk.Space.step', side_effect=AssertionError('Preview must never integrate')):
            for key in CATALOG:
                with self.subTest(topology=key):
                    data=preview(apply_preset(DEFAULTS,key))
                    self.assertEqual(data['kind'],'setup-preview')
                    self.assertEqual(data['solver_steps'],0)
                    self.assertNotIn('rows',data)
                    self.assertEqual(data['frame']['spring_geometry']['topology'],key)
                    self.assertAlmostEqual(data['geometry']['height'],2*data['config']['length']*math.sin(math.radians(data['config']['theta'])))
                    json.dumps(data,allow_nan=False)

    def test_replacement_preview_uses_upper_chassis_anchors_and_actual_sensors(self):
        data=preview(constant_lift_profile())
        sites=data['frame']['spring_geometry']['force_sites']
        self.assertEqual({site['body'] for site in sites},{'hip','upper'})
        self.assertEqual(len(data['model']['shapes']),6)
        self.assertNotIn('auxiliary_spring_geometry',data['frame'])
        self.assertEqual(data['frame']['guide_pulleys']['ratio'],2)

    def test_edited_geometry_changes_preview_and_invalid_geometry_is_rejected(self):
        a=preview({'spring_topology':'hip_pulley','theta':30})
        b=preview({'spring_topology':'hip_pulley','theta':60,'length':.35})
        self.assertNotEqual(a['frame']['knee'],b['frame']['knee'])
        self.assertNotEqual(a['geometry']['height'],b['geometry']['height'])
        with self.assertRaises(ValueError):preview({'length':.01})


if __name__=='__main__':unittest.main()
