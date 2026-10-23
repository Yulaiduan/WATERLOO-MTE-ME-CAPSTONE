"""Verify isolated Kinefold two-body sharp-terrain Pymunk contact mechanics.

Run app .venv Python verify_contact.py from this directory. Inputs: unchanged
VSL/Kinefold JS defaults in mm/deg/kg/N, explicit 1.5kg wheel study assumption
and SI contact controls. Outputs unittest results and compact numerical evidence.
Requires Node/Pymunk. Tests rigid contact, free spin, exact-guide virtual work,
gravity, geometry/shape guards, gap bridging and timestep refinement; no tire,
hardware, arbitrary linkage or canonical robot validation is established.
"""
import json
import math
from pathlib import Path
import subprocess
import unittest

from contact_dynamics import ContactGeometry, simulate_contact, validate_contact_request
from dynamic_model import R, defaults

ROOT=Path(__file__).resolve().parent
JS="const fs=require('fs'),vm=require('vm');vm.runInThisContext(fs.readFileSync('reference-v4.js','utf8'));vm.runInThisContext(fs.readFileSync('model.js','utf8'));console.log(JSON.stringify(Kinefold.defaults));"


class ContactChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads(subprocess.check_output(['node','-e',JS],cwd=ROOT,text=True))
        cls.base['m6']=1.5
        cls.report={}

    def payload(self,params=None,contact=None,**config):
        return dict(engine='pymunk',params={**self.base,**(params or {})},runConfig={**defaults(),**config},
                    contactConfig=dict(mode='terrain-contact',friction=.8,restitution=0,drive='free',**(contact or {})))

    def run_case(self,params=None,**config):
        return simulate_contact(self.payload(params,**config))

    def test_exact_line_inverse_and_virtual_work(self):
        errors=[]
        for edits in ({},{'alpha':17,'phi0':14,'te':110}):
            payload=self.payload(edits);m=validate_contact_request(payload)
            for deg in (115,132.5,155,164):
                q=deg*R;C,prime,_=m.sites(q)['6'];s=m.distance(q);j=m.jacobian(q)
                self.assertAlmostEqual(C[0],s*m.axis[0],delta=2e-15)
                self.assertAlmostEqual(C[1],s*m.axis[1],delta=2e-15)
                self.assertAlmostEqual(m.inverse(s),q,delta=2e-14)
                Q=m.spring(q)['torque']+m.c['hipTorqueNm']
                F=m.internal_force(q,0)
                self.assertAlmostEqual(F*(prime[0]*m.axis[0]+prime[1]*m.axis[1]),Q,delta=2e-12)
                dq=1e-6
                energyQ=-(m.spring(q+dq)['energy']-m.spring(q-dq)['energy'])/(2*dq)
                errors.append(abs(energyQ-m.spring(q)['torque']))
                self.assertAlmostEqual(energyQ,m.spring(q)['torque'],delta=2e-7)
        self.report['max_spring_virtual_work_error_Nm']=max(errors)

    def test_all_unsupported_geometry_and_request_guards(self):
        variants=[({'L3':299},{}),({'ra':59},{}),({'m2':.1},{}),({'m3':.1},{}),({'m5':.1},{}),
                  ({'m6':0},{}),({'m1':0},{}),({'te':90},{}),({'loadMode':'contact'},{}),
                  ({},{'hipRotorInertiaKgM2':.1}),({},{'inertiaModel':'custom'}),({},{'I6':.1}),({},{'inputRiseMm':1})]
        for p,c in variants:
            with self.subTest(p=p,c=c),self.assertRaises(ValueError):validate_contact_request(self.payload(p,**c))
        for key,value in (('mode','bench'),('friction',-1),('friction',float('nan')),('restitution',.1),('drive','locked')):
            request=self.payload();request['contactConfig'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate_contact_request(request)
        for transform in (lambda p:p.update(engine='unknown'),lambda p:p['contactConfig'].update(extra=1),lambda p:p.pop('contactConfig')):
            request=self.payload();transform(request)
            with self.assertRaises(ValueError):validate_contact_request(request)

    def test_flat_gravity_holding_normal_force_and_actual_bodies(self):
        r=self.run_case(inputHeightMm=0,duration=1,hipTorqueNm=-.027168833380,dt=.00025)
        expected=(8.75+1.5)*9.81;tail=r['rows'][-20:]
        normal=sum(row['contactNormalForceN'] for row in tail)/len(tail)
        self.assertEqual(r['diagnostics']['termination'],'duration')
        self.assertAlmostEqual(normal,expected,delta=.002)
        self.assertEqual(r['diagnostics']['rigidBodies'],2)
        self.assertAlmostEqual(r['diagnostics']['wheelMomentKgM2'],.5*1.5*.2**2,delta=1e-15)
        drift=max(abs(row['chassisZMm']-r['rows'][0]['chassisZMm']) for row in r['rows'])
        self.assertLess(drift,.01)
        for frame in r['frames']:
            self.assertEqual(frame['A'],frame['bodyPositionsMm']['1']);self.assertEqual(frame['C'],frame['bodyPositionsMm']['6'])
            self.assertEqual(frame['actualA'],frame['A']);self.assertEqual(frame['actualC'],frame['C'])
        self.report.update(flat_normal_N=normal,flat_expected_normal_N=expected,flat_holding_chassis_drift_mm=drift)

    def test_actual_friction_free_spin_and_signed_slip(self):
        on=self.run_case(inputHeightMm=0,duration=.5,hipTorqueNm=-.027168833380,dt=.00025)
        request=self.payload(inputHeightMm=0,duration=.5,hipTorqueNm=-.027168833380,dt=.00025)
        request['contactConfig']['friction']=0;off=simulate_contact(request)
        expected=.1/.2/R
        self.assertEqual(on['diagnostics']['effectiveFriction'],.8);self.assertEqual(off['diagnostics']['effectiveFriction'],0)
        self.assertAlmostEqual(on['rows'][-1]['wheelAngularVelocityDegS'],expected,delta=.001)
        self.assertAlmostEqual(off['rows'][-1]['wheelAngularVelocityDegS'],0,delta=1e-12)
        self.assertLess(abs(on['rows'][-1]['slipMmS']),.001)
        self.assertAlmostEqual(abs(off['rows'][-1]['slipMmS']),100,delta=.001)
        self.assertGreater(on['rows'][1]['contactTangentialForceN'],0)
        self.assertLess(on['rows'][1]['slipMmS'],0)
        self.assertAlmostEqual(off['rows'][-1]['contactTangentialForceN'],0,delta=1e-12)
        # q remains held but the physical free wheel/drive shaft index rotates.
        self.assertGreater(on['frames'][-1]['theta4'],1)
        self.assertAlmostEqual(on['frames'][-1]['theta6'],on['frames'][-1]['wheelAngle']+on['params']['alpha'],delta=1e-12)
        self.report.update(friction_spin_deg_s=on['rows'][-1]['wheelAngularVelocityDegS'],frictionless_slip_mm_s=off['rows'][-1]['slipMmS'])

    def test_sharp_corner_delay_world_mesh_gap_bridge_and_no_driver(self):
        r=self.run_case(dt=.00025)
        self.assertEqual(r['diagnostics']['termination'],'duration')
        self.assertAlmostEqual(r['terrain']['firstContactClearanceMm'],math.sqrt(2*200*150-150**2),delta=1e-10)
        self.assertEqual(r['frames'][0]['penetrationMm'],0)
        self.assertGreaterEqual(r['diagnostics']['firstRaisedContactTimeS'],.5-.0003)
        self.assertLessEqual(r['diagnostics']['firstRaisedContactTimeS'],.5+.001)
        self.assertLess(r['diagnostics']['maxPenetrationMm'],.1)
        self.assertLess(r['diagnostics']['maxGuideResidualMm'],.05)
        for i in (0,50,200,-1):
            frame=r['frames'][i]
            self.assertAlmostEqual(frame['terrainOffsetMm'][0],-100*frame['t'],delta=1e-9)
            self.assertAlmostEqual(frame['terrainPolygonsMm'][0][0][0],r['terrain']['polygonsMm'][0][0][0]-100*frame['t'],delta=1e-9)
        # Nominal top gap is not a commanded wheel drop: R200 can bridge 150mm.
        gaprows=[row for row in r['rows'] if 4.1<row['t']<5.2]
        self.assertGreater(min(row['wheelZMm'] for row in gaprows),330)
        self.assertLess(min(row['wheelZMm'] for row in gaprows),340)
        self.assertTrue(all(row['requestedInputMm'] is None and row['inputReactionN'] is None for row in r['rows']))
        self.report.update(sharp_default=r['diagnostics'],gap_bridge_min_wheel_z_mm=min(row['wheelZMm'] for row in gaprows))

    def test_tall_wall_jam_stops_and_initial_delay_is_safe(self):
        r=self.run_case({'rw':100},dt=.00025,duration=2)
        self.assertEqual(r['diagnostics']['termination'],'contact-penetration-limit')
        self.assertLess(r['diagnostics']['elapsedSeconds'],1)
        self.assertAlmostEqual(r['terrain']['firstContactClearanceMm'],100,delta=1e-12)
        self.assertAlmostEqual(r['terrain']['upperCornerClearanceMm'],math.sqrt(7500),delta=1e-10)
        self.assertEqual(r['frames'][0]['penetrationMm'],0)
        self.assertGreaterEqual(r['diagnostics']['firstRaisedContactTimeS'],.5-.0003)
        self.assertGreater(r['rows'][-1]['penetrationMm'],1)
        self.assertLess(r['rows'][-1]['penetrationMm'],1.1)
        self.report['negative_tall_wall_jam']=r['diagnostics']

    def test_timestep_refinement(self):
        runs=[self.run_case(dt=dt,duration=3.5) for dt in (.001,.0005,.00025)]
        a,b,fine=runs
        errors=[]
        for r in (a,b):
            errors.append(max(abs(row['chassisZMm']-ref['chassisZMm']) for row,ref in zip(r['rows'],fine['rows'])))
        self.assertLess(errors[1],errors[0])
        self.assertLess(errors[1],.15)
        self.assertLess(fine['diagnostics']['maxPenetrationMm'],a['diagnostics']['maxPenetrationMm'])
        self.report['refinement_max_chassis_errors_mm_vs_dt_00025']=errors
        self.report['refinement_penetration_mm']=[r['diagnostics']['maxPenetrationMm'] for r in runs]

    def test_global_force_once_and_transmission_backdrive(self):
        r=self.run_case({'loadMode':'global','Fz':10,'Fx':0},inputHeightMm=0,duration=.6,hipTorqueNm=-.027168833380,dt=.00025)
        normal=sum(row['contactNormalForceN'] for row in r['rows'][-10:])/10
        self.assertAlmostEqual(normal,(8.75+1.5)*9.81-10,delta=.003)
        m=validate_contact_request(self.payload({'alpha':15,'phi0':10,'te':110,'rd':36,'rc':30,'rf':32,'re':25}))
        q=140*R;theta6=24.;theta4=m.dc*m.fe*(theta6-m.K*(q/R-m.p['te']))
        theta5=(1-1/m.dc)*(q/R-m.p['te'])+theta4/m.dc
        # Inverse of the exact three-stage ideal belt relation.
        recovered=theta4/(m.dc*m.fe)+m.K*(q/R-m.p['te'])
        self.assertAlmostEqual(recovered,theta6,delta=1e-12)
        self.assertTrue(math.isfinite(theta5))
        tilted=self.run_case({'alpha':15,'phi0':10,'te':110,'rd':36,'rc':30,'rf':32,'re':25},
                             inputHeightMm=0,duration=.1,dt=.00025)
        initial=tilted['frames'][0]
        self.assertEqual(initial['indexAnglesDeg']['a'],0)
        self.assertAlmostEqual(initial['theta4'],0,delta=1e-12)
        self.assertAlmostEqual(initial['theta6'],m.K*(m.p['theta2']-m.p['te']),delta=1e-12)
        self.assertAlmostEqual(initial['wheelAngle'],initial['theta6']-15,delta=1e-12)
        self.assertGreater(abs(tilted['frames'][-1]['C'][0]-initial['C'][0]),.001)
        # Additional global horizontal rim load generates its real wheel torque
        # once. With g=0, no spring and mu=0, spin is independently tau/I*t.
        request=self.payload({'g':0,'springEnabled':False,'loadMode':'global','Fx':1,'Fz':0},
                             inputHeightMm=0,duration=.1,dt=.00025)
        request['contactConfig']['friction']=0
        torque_case=simulate_contact(request)
        self.assertAlmostEqual(torque_case['rows'][-1]['wheelAngularVelocityDegS'],-.2/.03*.1/R,delta=1e-8)

    @classmethod
    def tearDownClass(cls):
        print(json.dumps(cls.report,indent=2,allow_nan=False))


if __name__=='__main__':
    unittest.main(verbosity=2)
