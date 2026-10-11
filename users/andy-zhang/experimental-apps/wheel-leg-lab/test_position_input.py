"""Validate prescribed position and independently derived chassis response.

Run: python -m unittest -v test_position_input from app root.
Inputs: metres/seconds/radians, explicit fixture and smooth trajectories.
Outputs: test diagnostics, no files. Requires pinned Pymunk.
Limitations: ideal bilateral support, no real tire contact or hardware validation.
"""
import math
import unittest
from physics import config,build,simulate
from motion_input import position_state

def floating_reference(values):
    """One shape coordinate with prescribed base height, from scalar energy."""
    c=config(values);L,e=c['length'],c['extension'];rest=build(c)['rest']
    q=math.radians(c['theta']);v=0.;dt=.00005
    S=1.5*L*c['upper_mass']+.5*(L+e)*c['lower_mass']+2*L*c['chassis_mass']
    inertia=c['upper_mass']*L*L/12+c['lower_mass']*(L+e)**2/12
    if c['wheel_drive_locked']:inertia+=.5*c['wheel_mass']*c['radius']**2
    def rhs(t,q,v):
        sn,cs=math.sin(q),math.cos(q)
        M=inertia+c['upper_mass']*((L/2)**2*sn*sn+(1.5*L)**2*cs*cs)+c['lower_mass']*((L+e)/2)**2+4*c['chassis_mass']*L*L*cs*cs
        Mp=(c['upper_mass']*((L/2)**2-(1.5*L)**2)-4*c['chassis_mass']*L*L)*math.sin(2*q)
        length=math.sqrt(L*L+e*e+2*L*e*math.cos(2*q));J=-2*L*e*math.sin(2*q)/length
        spring=-c['stiffness']*(length-rest)*J-c['damping']*J*J*v
        _,_,base_a=position_state(t,c)
        return v,(spring-S*cs*(c['gravity']+base_a)-.5*Mp*v*v)/M
    for i in range(round(c['duration']/dt)):
        t=i*dt;k1=rhs(t,q,v);k2=rhs(t+dt/2,q+dt*k1[0]/2,v+dt*k1[1]/2)
        k3=rhs(t+dt/2,q+dt*k2[0]/2,v+dt*k2[1]/2);k4=rhs(t+dt,q+dt*k3[0],v+dt*k3[1])
        q+=dt*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6;v+=dt*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6
    return q,v

class PositionInputTests(unittest.TestCase):
    def test_smooth_ramp_derivatives_and_plateau(self):
        c=config();eps=1e-6
        for t in [.52,.58,.65,.73]:
            z,v,a=position_state(t,c)
            zp,vp,_=position_state(t+eps,c);zm,vm,_=position_state(t-eps,c)
            self.assertAlmostEqual(v,(zp-zm)/(2*eps),places=7)
            self.assertAlmostEqual(a,(vp-vm)/(2*eps),places=6)
        self.assertEqual(position_state(.4,c),(0.,0.,0.))
        self.assertEqual(position_state(2.,c),(.03,0.,0.))

    def test_square_and_position_pulse(self):
        c=config({'wave':'square'})
        self.assertAlmostEqual(position_state(.9,c)[0],.03)
        self.assertEqual(position_state(1.4,c),(0.,0.,0.))
        pulse=config({'wave':'pulse'})
        self.assertEqual(position_state(2.,pulse),(0.,0.,0.))

    def test_default_is_position_and_driver_is_kinematic(self):
        c=config();m=build(c)
        self.assertEqual(c['target'],'position');self.assertEqual(c['fixture'],'floating')
        self.assertEqual(type(m['driver']).__name__,'PivotJoint')
        self.assertEqual(len(m['space'].constraints),6)  # Point-force coil adds no constraint.
        self.assertEqual(m['carriage'].body_type,m['carriage'].KINEMATIC)

    def test_actual_motion_tracking_and_reaction_checks(self):
        r=simulate({'duration':1.2})
        self.assertEqual(r['diagnostics']['input_unit'],'m')
        self.assertLess(r['diagnostics']['max_position_error_m'],.0002)
        self.assertTrue(all(v<1e-7 for v in r['equation_check_errors'].values()))
        self.assertAlmostEqual(r['rows'][-1]['position_command'],.03)
        self.assertGreater(abs(r['rows'][-1]['chassis_displacement']),.001)
        self.assertGreater(r['rows'][-1]['driver_force'],50)

    def test_force_amplitude_is_not_position_input(self):
        a=simulate({'duration':1.,'amplitude':0.})
        b=simulate({'duration':1.,'amplitude':900.})
        self.assertEqual(a['rows'][-1]['position_actual'],b['rows'][-1]['position_actual'])
        self.assertEqual(a['rows'][-1]['chassis_displacement'],b['rows'][-1]['chassis_displacement'])
        biased=simulate({'duration':1.,'bias_force':10.})
        self.assertEqual(a['actual_rest_length'],biased['actual_rest_length'])
        self.assertAlmostEqual(a['rows'][-1]['chassis_displacement'],biased['rows'][-1]['chassis_displacement'],delta=1e-7)
        self.assertAlmostEqual(a['rows'][-1]['driver_force']-10.,biased['rows'][-1]['driver_force'],delta=1e-5)

    def test_spring_changes_chassis_not_prescribed_height(self):
        a=simulate({'duration':1.2})
        b=simulate({'duration':1.2,'stiffness':16000.})
        self.assertAlmostEqual(a['rows'][-1]['position_actual'],b['rows'][-1]['position_actual'],delta=.00005)
        self.assertGreater(abs(a['rows'][-1]['chassis_displacement']-b['rows'][-1]['chassis_displacement']),.001)

    def test_refinement_and_independent_energy_response(self):
        values={'duration':1.2};q,_=floating_reference(values)
        errors=[];tracking=[]
        for dt in [.001,.0005,.00025]:
            r=simulate({**values,'dt':dt})
            errors.append(abs(r['rows'][-1]['theta_deg']-math.degrees(q)))
            tracking.append(r['diagnostics']['max_position_error_m'])
        print('Position RK4 reference:',math.degrees(q),'angle errors:',errors,'tracking:',tracking)
        self.assertLess(errors[-1],.05)
        self.assertLess(errors[-1],errors[0])
        self.assertLess(tracking[-1],tracking[0]/2)

    def test_fixed_hip_position_fixture_and_invalid_steps(self):
        r=simulate({'fixture':'hip','duration':1.})
        self.assertEqual(r['rows'][-1]['chassis_displacement'],0)
        self.assertLess(r['diagnostics']['max_position_error_m'],.0002)
        self.assertTrue(all(v<1e-7 for v in r['equation_check_errors'].values()))
        for values in [{'rise':0.},{'wave':'impulse'},{'fixture':'hip','position_amplitude':.4}]:
            with self.assertRaises(ValueError):config(values)

if __name__=='__main__':unittest.main(verbosity=2)
