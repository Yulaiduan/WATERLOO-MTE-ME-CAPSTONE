"""Verify the narrow V4 route and unchanged embedded source model.

Run: python -m unittest -v test_vsl_integration from the app root.
Inputs: original sibling V4 files, text and hashes; no numerical units are modified.
Outputs: unittest results. Does not execute solver snippets or certify model physics.
"""
import hashlib
import re
import unittest
from vsl_integration import resource, SOURCE, FILES

class VSLIntegrationTests(unittest.TestCase):
    def test_original_models_are_byte_identical_in_served_html(self):
        raw=(SOURCE/'v4-pulley.html').read_bytes()
        page,mime=resource('/vsl-v4/')
        self.assertEqual(mime,'text/html; charset=utf-8')
        original=re.findall(rb'<script(?: id="[^"]+")?>(.*?)</script>',raw,re.S)
        served=re.findall(rb'<script(?: id="[^"]+")?>(.*?)</script>',page,re.S)
        self.assertEqual(original,served)
        self.assertIn(hashlib.sha256(raw).hexdigest().encode(),page)
        self.assertIn(b'/sizing/vsl-bridge.js',page)

    def test_only_explicit_v4_resources_are_served(self):
        for route in ['/vsl-v4/../README.md','/vsl-v4/context/README.md','/vsl-v4/v1-kinematics.html','/other/']:
            self.assertIsNone(resource(route))
        for name in FILES:
            self.assertTrue((SOURCE/name).is_file(),name)
            data,mime=resource('/vsl-v4/'+name)
            self.assertTrue(data)

    def test_preset_bytes_are_preserved(self):
        self.assertEqual(resource('/vsl-v4/v4-textbook-10mm.json')[0],(SOURCE/'v4-textbook-10mm.json').read_bytes())

if __name__=='__main__':unittest.main()
