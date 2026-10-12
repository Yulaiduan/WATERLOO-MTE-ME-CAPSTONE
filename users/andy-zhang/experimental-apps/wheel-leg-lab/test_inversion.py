"""Check geometric rope switching, work and actual ground-contact inversion.

Run .venv/Scripts/python.exe -m unittest -v test_inversion from this app.
Inputs SI demo profiles, actual Pymunk/SciPy cases; outputs assertions only.
Limitations: ideal massless routing/fixed-pitch fixture, not 3D/hardware proof.
"""
import math
import unittest
from inversion import config,preview,simulate,build
from invertible_spring import state,prepare,route,cross,sub,unit,mul

class InversionTests(unittest.TestCase):
    def test_offset_attachment_and_routing_geometry(self):
        c=config();p=prepare(c)
        for q in [-2.2,-1.,-.2,.2,1.,2.2]:
            s=state(q,.2,c,p);g=s['geometry'];self.assertGreaterEqual(s['red_tension'],0);self.assertGreaterEqual(s['blue_tension'],0)
            self.assertEqual(min(s['red_tension'],s['blue_tension']),0)
            for colour,sign in [('red',1),('blue',-1)]:
                r=g['routes'][colour];self.assertAlmostEqual(r['attachment_angle'],2*q+sign*math.radians(5))
                self.assertGreaterEqual(g['slack'][colour],-1e-9)
                self.assertEqual(len([piece for piece in r['pieces'] if piece['kind']=='line']),1)
            e=1e-6
            fd=(state(q+e,.2,c,p)['energy']-state(q-e,.2,c,p)['energy'])/(2*e)
            self.assertAlmostEqual(s['torque'],-fd,delta=1e-4)
        left=state(-.5,0,c,p);right=state(.5,0,c,p)
        self.assertNotEqual(left['geometry']['active'],right['geometry']['active'])
        self.assertAlmostEqual(left['energy'],right['energy'],places=9)
        self.assertAlmostEqual(left['torque'],-right['torque'],places=9)
    def test_symmetric_bellcrank_mount_and_energy(self):
        c=config({'preset':'knee_bellcrank'});self.assertEqual(c['femur_anchor_distance'],.05);p=prepare(c)
        for q in [.2,.7,1.1]:
            a=state(q,0,c,p);b=state(-q,0,c,p)
            self.assertAlmostEqual(a['energy'],b['energy'],places=10);self.assertAlmostEqual(a['torque'],-b['torque'],places=10)
            self.assertEqual(a['geometry']['femur_anchor'][0],-(c['length']-.05))
        dead=state(math.pi/2,0,c,p);self.assertGreater(dead['cap_force'],0);self.assertAlmostEqual(dead['torque'],0.,places=10)
    def test_force_sites_reproduce_virtual_torque(self):
        for preset in ['dual_rope','knee_bellcrank']:
            c=config({'preset':preset});p=prepare(c)
            for degrees in range(-179,180,2):
                s=state(math.radians(degrees),.2,c,p);g=s['geometry']
                if preset=='dual_rope':
                    if g['active']=='none':continue
                    r=g['routes'][g['active']];a,b=r['upper_contact'],r['lower_contact'];F=mul(r['direction'],s['cap_force'])
                else:a,b=g['femur_anchor'],g['crank_tip'];F=mul(unit(sub(a,b)),s['cap_force'])
                self.assertAlmostEqual(cross(b,F)*2,s['torque'],places=9)
                self.assertAlmostEqual(cross(sub(b,a),F),0.,places=9)
    def test_preview_inverted_and_not_stepped(self):
        v=preview();self.assertEqual(v['solver_steps'],0);self.assertGreater(v['frame']['hub'][1],v['frame']['hip'][1]);self.assertEqual(v['frame']['hip'][1],.055/2)
        m=build(v['config']);self.assertEqual(len(m['space'].constraints),4);self.assertTrue(all(b.body_type!=b.KINEMATIC for b in m['space'].bodies))
    def test_both_actual_ground_demos_flip_without_position_driver(self):
        for preset in ['dual_rope','knee_bellcrank']:
            r=simulate({'preset':preset});self.assertIsNotNone(r['diagnostics']['flip_time_s']);self.assertGreater(max(x['theta_deg'] for x in r['rows']),45)
            self.assertGreater(max(x['wheel_ground_force_N'] for x in r['rows']),0);self.assertGreater(max(x['chassis_ground_force_N'] for x in r['rows']),0)
            self.assertLess(max(abs(x['guide_error_rad']) for x in r['rows']),1e-8)
            self.assertTrue(all(f['hub'][1]>=r['config']['radius']-.003 and f['hip'][1]>=.0275-.003 for f in r['frames']))
            self.assertEqual(r['config']['damping'],0)
    def test_fixed_hip_independent_math_refines_and_energy_closes(self):
        for preset in ['dual_rope','knee_bellcrank']:
            c={'preset':preset,'fixture':'hip_fixed','gravity':0.,'auto_rate':False,'stiffness':500.,'femur_torque':2.,'duration':.45}
            reference=simulate(c,'math');self.assertLess(max(abs(r['energy_balance_error_J']) for r in reference['rows']),.001)
            errors=[]
            for dt in [.001,.0005,.00025,.000125]:
                r=simulate(dict(c,dt=dt));errors.append(abs(r['rows'][-1]['theta_deg']-reference['rows'][-1]['theta_deg']))
            self.assertLess(errors[-1],errors[0]);self.assertLess(errors[-1],.1)
    def test_invalid_geometry_not_silently_repaired(self):
        for changes in [{'routing_offset':.015},{'coil_free_length':.03},{'cap_reference_distance':.23},{'attachment_offset_deg':float('nan')},{'preset':'unknown'}]:
            with self.assertRaises(ValueError):config(changes)

if __name__=='__main__':unittest.main()
