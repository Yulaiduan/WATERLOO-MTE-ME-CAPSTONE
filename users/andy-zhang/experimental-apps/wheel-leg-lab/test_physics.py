"""Validate experimental linkage mechanics and reference equations.

Run: python -m unittest -v test_physics test_equation_checks from app root.
Inputs: explicit SI test fixtures; degree reference angles are converted to radians.
Outputs: unittest diagnostics; no files. Requires pinned Pymunk.
Limitations: numerical/analytical checks, not canonical robot or hardware validation.
"""
import math
import unittest
from physics import config as actual_config, build, simulate as actual_simulate, excitation_area, input_average

def config(values=None): return actual_config({"target":"force",**(values or {})})
def simulate(values=None): return actual_simulate({"target":"force",**(values or {})})


def reference(values):
    """Independent 1-DOF reference from rigid-body kinetic/potential energy, RK4."""
    c=config(values); rest=build(c)['rest'];L,e=c['length'],c['extension']
    q=math.radians(c['theta']);v=0.;h=.00005
    inertia=c['upper_mass']*L*L/12+c['lower_mass']*(L+e)**2/12
    if c['wheel_drive_locked']:inertia+=.5*c['wheel_mass']*c['radius']**2
    a=(L+e)**2/4;b=(3*L-e)**2/4
    gravity=c['gravity']*(c['upper_mass']*L/2+c['lower_mass']*(3*L-e)/2+c['wheel_mass']*2*L)
    def rhs(t,q,v):
        M=inertia+c['upper_mass']*L*L/4+c['lower_mass']*(a*math.sin(q)**2+b*math.cos(q)**2)+4*c['wheel_mass']*L*L*math.cos(q)**2
        Mp=(c['lower_mass']*(a-b)-4*c['wheel_mass']*L*L)*math.sin(2*q)
        length=math.sqrt(L*L+e*e+2*L*e*math.cos(2*q))
        J=-2*L*e*math.sin(2*q)/length
        spring=-c['stiffness']*(length-rest)*J-c['damping']*J*J*v
        force=c['bias_force']+input_average(t,h,c)
        Q=gravity*math.cos(q)-2*L*math.cos(q)*force+spring
        if c['wheel_drive_locked'] and c['load_point']=='contact':Q+=c['bias_force_x']*c['radius']
        return v,(Q-.5*Mp*v*v)/M
    for i in range(round(c['duration']/h)):
        t=i*h;k1=rhs(t,q,v);k2=rhs(t+h/2,q+h*k1[0]/2,v+h*k1[1]/2)
        k3=rhs(t+h/2,q+h*k2[0]/2,v+h*k2[1]/2);k4=rhs(t+h,q+h*k3[0],v+h*k3[1])
        q+=h*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6
        v+=h*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6
    return math.degrees(q),v


class PhysicsTests(unittest.TestCase):
    def test_engine_debug_draw_and_shapes(self):
        import pymunk
        from debug_view import capture,describe
        m=build(config());p=capture(m['space']);info=describe(m)
        self.assertEqual(len(m['space'].shapes),3)
        self.assertTrue(all(s.sensor for s in m['space'].shapes))
        self.assertEqual([x['class'] for x in info['constraints']].count('PivotJoint'),3)
        self.assertEqual(len(info['constraints']),6)
        self.assertEqual(sum(x['kind']=='capsule' for x in p),2)
        circle=next(x for x in p if x['kind']=='circle')
        self.assertAlmostEqual(circle['radius']/info['debug_scale'],.2)
        self.assertTrue(any(x['kind']=='segment' for x in p))
        query=m['space'].point_query_nearest(m['lower'].local_to_world((.1,0)),1.,pymunk.ShapeFilter())
        self.assertIsNotNone(query)

    def test_impulse_area_and_edges(self):
        for rise,fall in [(0,0),(.017,.023),(.05,.05)]:
            c=config({'wave':'impulse','impulse':2.7,'pulse_width':.12,'rise':rise,'fall':fall,'start':.031})
            for dt in [.002,.001,.0005]:
                total=sum(input_average(i*dt,dt,c)*dt for i in range(1000))
                self.assertAlmostEqual(total,2.7,places=10)
            self.assertEqual(excitation_area(.03,c),0)

    def test_square_area_with_slopes(self):
        c=config({'start':0.,'amplitude':10.,'period':1.,'duty':.5,'rise':.1,'fall':.2})
        self.assertAlmostEqual(excitation_area(3,c),3*10*(.5-.15))
        self.assertAlmostEqual(input_average(.02,.001,c),2.05)

    def test_geometry_and_spring_tip(self):
        c=config();m=build(c)
        A=m['hip'].local_to_world(m['j1'].anchor_a)
        B=m['upper'].local_to_world(m['j2'].anchor_a)
        C=m['wheel'].local_to_world(m['j3'].anchor_b)
        E=m['lower'].local_to_world(m['spring'].anchor_b)
        self.assertAlmostEqual((E-B).length,.05)
        self.assertLess((E-B).dot(C-B),0)
        self.assertAlmostEqual(C.x,A.x)
        self.assertAlmostEqual(A.y-C.y,2*c['length']*math.sin(math.radians(c['theta'])))
        self.assertEqual(m['guide'].ratio,-1)

    def test_static_balance_both_fixtures(self):
        for fixture in ['hip','wheel']:
            r=simulate({'fixture':fixture,'bias_force':80. if fixture=='hip' else 0.,'amplitude':0.,'duration':1.})
            self.assertLess(max(abs(x['theta_deg']-45) for x in r['rows']),.002)
            self.assertEqual(r['diagnostics']['stop_steps'],0)

    def test_momentum_reactions_and_guide(self):
        r=simulate({'duration':1.5})
        self.assertLess(r['diagnostics']['max_force_check_N'],1e-7)
        self.assertLess(r['diagnostics']['max_torque_check_Nm'],1e-7)
        self.assertLess(r['diagnostics']['max_pin_error_m'],1e-5)
        self.assertLess(r['diagnostics']['max_guide_error_rad'],1e-5)
        for row in r['rows'][::100]:
            self.assertAlmostEqual(row['knee_speed'],row['lower_speed']-row['upper_speed'])
            self.assertAlmostEqual(row['upper_speed'],-row['lower_speed'],places=4)
            self.assertAlmostEqual(row['guide_hip_reaction'],-2*row['guide_link_torque'])

    def test_independent_energy_model_and_refinement(self):
        values={'wave':'impulse','impulse':.15,'pulse_width':.12,'start':.15,'duration':.8}
        angle,speed=reference(values)
        errors=[]
        for dt in [.002,.001,.0005,.00025]:
            r=simulate({**values,'dt':dt});last=r['rows'][-1]
            errors.append(abs(last['theta_deg']-angle))
        print('RK4 reference angle:',angle,'Pymunk angle errors:',errors)
        self.assertLess(errors[-1],.025)
        self.assertLess(errors[-1],errors[0])

    def test_limit_and_actuator_channels(self):
        r=simulate({'amplitude':50.,'target':'knee','torque_limit':2.,'duration':1.2})
        self.assertGreater(r['diagnostics']['clipped_steps'],0)
        self.assertTrue(all(abs(x['actuator_torque'])<=2. for x in r['rows']))
        r=simulate({'amplitude':30.,'duration':1.5})
        self.assertGreater(r['diagnostics']['stop_steps'],0)
        self.assertGreater(abs(r['peaks']['stop_knee_torque']['value']),0)
        self.assertTrue(r['warnings'])

    def test_invalid_waveform_is_rejected(self):
        with self.assertRaises(ValueError): config({'wave':'impulse','pulse_width':.01})
        with self.assertRaises(ValueError): config({'theta':90})

if __name__=='__main__': unittest.main(verbosity=2)
