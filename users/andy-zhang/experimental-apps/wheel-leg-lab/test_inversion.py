"""Check geometric rope switching, work and actual ground-contact inversion.

Run .venv/Scripts/python.exe -m unittest -v test_inversion from this app.
Inputs SI demo profiles, actual Pymunk/SciPy cases; outputs assertions only.
Limitations: ideal massless routing/fixed-pitch fixture, not 3D/hardware proof.
"""
import math
import unittest
from inversion import config,preview,simulate,build,resolve_saved_profile
from invertible_spring import state,prepare,route,cross,sub,unit,mul,_line_clear

class InversionTests(unittest.TestCase):
    def test_offset_attachment_and_routing_geometry(self):
        c=config();p=prepare(c)
        for q in [-2.2,-1.,-.2,.2,1.,2.2]:
            s=state(q,.2,c,p);g=s['geometry'];self.assertGreaterEqual(s['red_tension'],0);self.assertGreaterEqual(s['blue_tension'],0)
            self.assertEqual(min(s['red_tension'],s['blue_tension']),0)
            for colour,sign in [('red',1),('blue',-1)]:
                r=g['routes'][colour];self.assertAlmostEqual(r['attachment_angle'],2*q+math.pi+sign*math.radians(5))
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
                    r=g['routes'][g['active']];a,b=r['upper_contact'],r['lower_contact'];F=mul(r['direction'],s[g['active']+'_tension'])
                else:a,b=g['femur_anchor'],g['crank_tip'];F=mul(unit(sub(a,b)),s['cap_force'])
                self.assertAlmostEqual(cross(b,F)*2,s['torque'],places=9)
                self.assertAlmostEqual(cross(sub(b,a),F),0.,places=9)
    def test_preview_inverted_and_not_stepped(self):
        v=preview();self.assertEqual(v['solver_steps'],0);self.assertGreater(v['frame']['hub'][1],v['frame']['hip'][1]);self.assertEqual(v['frame']['hip'][1],.055/2)
        m=build(v['config']);self.assertEqual(len(m['space'].constraints),5);self.assertIsNotNone(m['stop']);self.assertTrue(all(b.body_type!=b.KINEMATIC for b in m['space'].bodies))
    def test_both_actual_ground_demos_flip_without_position_driver(self):
        for preset in ['dual_rope','knee_bellcrank']:
            r=simulate({'preset':preset});self.assertIsNotNone(r['diagnostics']['flip_time_s']);self.assertGreater(max(x['theta_deg'] for x in r['rows']),30)
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
        for changes in [{'routing_offset':.010005},{'rope_eye_offset':.006},{'coil_free_length':.03},{'cap_reference_distance':.23},{'attachment_offset_deg':float('nan')},{'preset':'unknown'},{'rope_routing':'unknown'},{'rope_neutral_pose':'unknown'},{'initial_angle_deg':135},{'angle_max_deg':90}]:
            with self.assertRaises(ValueError):config(changes)

    def test_central_face_routes_inventory_and_cap_force(self):
        c=config({'rope_routing':'central_face','rope_neutral_pose':'straight','preload':.01,'rod_length':.12,'pulley_radius':.04,'routing_offset':.0105,'rope_eye_offset':.0001});p=prepare(c)
        for degrees in range(-179,180,2):
            s=state(math.radians(degrees),.2,c,p);g=s['geometry'];self.assertEqual(g['routing'],'central_face')
            q=math.radians(degrees);epsilon=1e-6
            gradient=(state(q+epsilon,0,c,p)['energy']-state(q-epsilon,0,c,p)['energy'])/(2*epsilon)
            self.assertAlmostEqual(s['torque'],-gradient,delta=1e-4)
            for colour,r in g['routes'].items():
                self.assertLess(abs(r['eye'][1]),c['routing_offset']-c['routing_radius'])
                length=math.dist(r['eye'],r['feed'])
                for piece in r['pieces']:
                    if piece['kind']=='arc':
                        self.assertNotEqual(piece['center'],(0,0));self.assertAlmostEqual(piece['radius'],c['routing_radius']);self.assertLessEqual(abs(piece['sweep']),math.pi)
                        length+=piece['radius']*abs(piece['sweep'])
                    else:length+=math.dist(piece['a'],piece['b'])
                self.assertAlmostEqual(length,r['length'],places=10)
                self.assertAlmostEqual(p['reference'][colour]-length,g['slack'][colour],delta=1e-9)
                if g['active']==colour:
                    self.assertAlmostEqual(g['slack'][colour],0.,delta=1e-9)
                    self.assertAlmostEqual(s[colour+'_tension']*r['cap_projection'],s['cap_force'],places=9)

    def test_prior_outer_route_remains_explicit_reproduction(self):
        c=config({'rope_routing':'outer_rim','rope_neutral_pose':'straight','preload':.01,'rod_length':.12,'routing_offset':.035});s=state(-2.2,0,c,prepare(c))
        self.assertTrue(any(piece['kind']=='arc' and piece['center']==(0,0) for r in s['geometry']['routes'].values() for piece in r['pieces']))

    def test_tight_gap_parallel_leads_and_knee_right_stops(self):
        c=config();self.assertAlmostEqual(2*(c['routing_offset']-c['routing_radius']),.0002)
        self.assertEqual(c['initial_angle_deg'],45);self.assertEqual((c['angle_min_deg'],c['angle_max_deg']),(-80,80))
        for preset in ['dual_rope','knee_bellcrank']:
            for backend in ['pymunk','math']:
                # The folded-neutral default need not hit a stop. Exercise real
                # stop reactions with a separate, explicitly stronger input.
                r=simulate({'preset':preset,**({'femur_torque':200.} if preset=='dual_rope' else {}),**({'fixture':'hip_fixed'} if backend=='math' else {})},backend)
                self.assertTrue(all(f['knee'][0]>f['hip'][0] for f in r['frames']))
                self.assertTrue(all(-80.5<=row['theta_deg']<=80.5 for row in r['rows']))
                self.assertTrue(any(abs(row['angle_stop_torque_Nm'])>0 for row in r['rows']))
                self.assertLess(max(max(row['red_lead_angle_deg'],row['blue_lead_angle_deg']) for row in r['rows']),1.1)
                if backend=='math':
                    self.assertGreater(r['rows'][-1]['stop_dissipated_energy_J'],0)
                    self.assertLess(max(abs(row['energy_balance_error_J']) for row in r['rows']),.001)

    def test_unlimited_saved_profile_has_no_extra_stop(self):
        c=config({'angle_limit_enabled':False,'initial_angle_deg':135})
        m=build(c);self.assertEqual(len(m['space'].constraints),4);self.assertIsNone(m['stop'])

    def test_central_wrap_tangents_inventory_and_energy(self):
        c=config();p=prepare(c);seen_wrap=False
        for degrees in range(-179,180,2):
            q=math.radians(degrees);s=state(q,.2,c,p);g=s['geometry'];self.assertEqual(g['routing'],'central_wrap')
            epsilon=1e-6;gradient=(state(q+epsilon,0,c,p)['energy']-state(q-epsilon,0,c,p)['energy'])/(2*epsilon)
            self.assertAlmostEqual(s['torque'],-gradient,delta=1e-4)
            for colour,r in g['routes'].items():
                self.assertTrue(_line_clear(r['eye'],r['feed'],c['pulley_radius'])) if r['eye']!=r['feed'] else None
                length=math.dist(r['eye'],r['feed'])
                for piece in r['pieces']:
                    if piece['kind']=='arc':
                        length+=piece['radius']*abs(piece['sweep'])
                        if piece['center']==(0,0):
                            seen_wrap=True;self.assertAlmostEqual(piece['radius'],c['pulley_radius'])
                            self.assertAlmostEqual(math.hypot(*r['lower_contact']),c['pulley_radius'])
                    else:
                        length+=math.dist(piece['a'],piece['b']);self.assertTrue(_line_clear(piece['a'],piece['b'],c['pulley_radius']))
                self.assertAlmostEqual(length,r['length'],places=9)
                self.assertAlmostEqual(p['reference'][colour]-length,g['slack'][colour],delta=1e-9)
        self.assertTrue(seen_wrap)
        with self.assertRaises(ValueError):config({'pulley_radius':.04})

    def test_fully_contracted_anchors_face_cylinder_and_spring_is_unloaded(self):
        c=config();p=prepare(c);self.assertEqual(c['rope_neutral_pose'],'folded');self.assertEqual(c['preload'],0.)
        for speed in [0.,1.,-1.]:
            s=state(0.,speed,c,p)
            for key in ['compression','takeup','cap_force','red_tension','blue_tension','torque','energy']:
                self.assertEqual(s[key],0.,key)
            self.assertEqual(s['coil_length'],c['coil_free_length']);self.assertEqual(s['geometry']['active'],'none')
            for r in s['geometry']['routes'].values():self.assertLess(r['anchor'][0],0.)
        for q in [-.5,-.01,.01,.5]:
            s=state(q,0.,c,p);self.assertGreater(s['compression'],0.);self.assertLess(s['torque']*q,0.)
        # Check real solvers at rest, not just the route drawing.
        for backend in ['math','pymunk']:
            r=simulate({'fixture':'hip_fixed','initial_angle_deg':0.,'start_inverted':False,'auto_rate':False,'gravity':0.,'femur_torque':0.,'duration':.1},backend)
            self.assertTrue(all(abs(row['theta_deg'])<1e-10 and row['cap_force_N']==0. and row['red_tension_N']==0. and row['blue_tension_N']==0. for row in r['rows']))

    def test_archived_wrapped_neutral_pose_is_reproducible(self):
        c=config({'rope_neutral_pose':'straight','preload':.01,'rod_length':.12});p=prepare(c)
        self.assertAlmostEqual(c['stiffness'],10848.293807645745,places=6)
        s=state(0.,0.,c,p);self.assertGreater(s['compression'],.09)
        self.assertTrue(all(r['anchor'][0]>0 for r in s['geometry']['routes'].values()))
        saved={'preset':'dual_rope','rope_routing':'central_wrap','angle_limit_enabled':True}
        resolved=resolve_saved_profile(saved);self.assertNotIn('rope_neutral_pose',saved)
        self.assertEqual(resolved['rope_neutral_pose'],'straight');self.assertEqual(resolved['preload'],.01);self.assertEqual(resolved['rod_length'],.12)
        self.assertEqual(config(resolved)['stiffness'],c['stiffness'])

if __name__=='__main__':unittest.main()
