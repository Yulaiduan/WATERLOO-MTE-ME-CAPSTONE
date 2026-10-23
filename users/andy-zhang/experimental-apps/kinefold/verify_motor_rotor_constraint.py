"""Run isolated native rotor smoke, momentum and simultaneous-contact tests.

Invoke app Python verify_motor_rotor_constraint.py; SI-only analytic fixtures,
no profiles/server/assets. Outputs unittest results. Tests experimental pinned
private ABI mechanics, not hardware or canonical robot validation.
"""
import math
import unittest
from unittest.mock import patch
import pymunk
from motor_rotor_constraint import attach


class LinearGeometry:
    axis = (0., 1.)
    def jacobian(self, _q):return .4
    def inverse(self, s):return s/.4


class CosineGeometry:
    axis = (0., 1.)
    def jacobian(self, q):return -.5*math.sin(q)
    def inverse(self, s):return math.acos(max(-1.,min(1.,s/.5)))


class RotorTests(unittest.TestCase):
    def test_exact_native_engine_version_guard(self):
        space=pymunk.Space();a,b=pymunk.Body(2,math.inf),pymunk.Body(3,.06)
        space.add(a,b)
        for attribute,value in [('chipmunk_version','2.0.1-unknown'),('version','7.3.1')]:
            with patch.object(pymunk,attribute,value):
                with self.assertRaisesRegex(ValueError,'native ABI is verified only'):
                    attach(space,a,b,LinearGeometry(),1.,.6,0.)
        self.assertEqual(len(space.constraints),0)

    def fixture(self, geometry=None, q=.6, qd=0., inertia=2.):
        space = pymunk.Space();space.gravity=(0,0);space.iterations=100
        a,b=pymunk.Body(2,math.inf),pymunk.Body(3,.06)
        geometry=geometry or LinearGeometry()
        s=.4*q if isinstance(geometry,LinearGeometry) else .5*math.cos(q)
        a.position=(0,1);b.position=(0,1+s)
        b.velocity=(0,geometry.jacobian(q)*qd)
        space.add(a,b)
        guide=pymunk.GrooveJoint(space.static_body,a,(0,-10),(0,10),(0,0))
        space.add(guide)
        rotor=attach(space,a,b,geometry,inertia,q,qd)
        self.addCleanup(rotor.close)
        return space,a,b,rotor

    def test_force_reflected_mass_and_momentum(self):
        space,a,b,r=self.fixture()
        b.force=(0,30);dt=.01;r.prepare(dt,0);space.step(dt);r.check()
        rel=(30/3)*dt/(1+(2/.4**2)*(1/2+1/3))
        self.assertAlmostEqual(b.velocity.y-a.velocity.y,rel,places=12)
        self.assertAlmostEqual(r.omega,rel/.4,places=12)
        self.assertAlmostEqual(2*a.velocity.y+3*b.velocity.y,30*dt,places=12)
        self.assertAlmostEqual(r.velocity_residual,0,places=12)
        self.assertEqual(b.angular_velocity,0)
        self.assertEqual((a.mass,b.mass,b.moment),(2,3,.06))

    def test_joint_torque_acceleration(self):
        space,a,b,r=self.fixture()
        dt=.01;r.prepare(dt,10);space.step(dt);r.check()
        # Relative translation's reduced mass is mc*mw/(mc+mw).
        expected=10*dt/(2+(2*3/5)*.4**2)
        self.assertAlmostEqual(r.omega,expected,places=12)
        self.assertAlmostEqual(2*a.velocity.y+3*b.velocity.y,0,places=12)

    def test_contact_and_rotor_in_same_native_iterations(self):
        space,a,b,r=self.fixture(q=-2.)
        # Wheel at z=.2 on a static floor; both bodies have -1 m/s.
        a.position=(0,1);b.position=(0,.2);a.velocity=(0,-1);b.velocity=(0,-1)
        circle=pymunk.Circle(b,.2);floor=pymunk.Segment(space.static_body,(-10,0),(10,0),0)
        circle.elasticity=floor.elasticity=0;space.collision_slop=.01
        space.add(circle,floor)
        r.prepare(.00001,0);space.step(.00001);r.check()
        # Independent reduced-mass projection for u=(hip height, relative s).
        mt,mw,H=5.,3.,2/.4**2
        determinant=mt*(mw+H)-mw*mw
        inv=((mw+H)/determinant,-mw/determinant,mt/determinant)
        denominator=inv[0]+2*inv[1]+inv[2]
        impulse=1/denominator
        vh=-1+(inv[0]+inv[1])*impulse
        sd=(inv[1]+inv[2])*impulse
        self.assertAlmostEqual(a.velocity.y,vh,places=10)
        self.assertAlmostEqual(b.velocity.y,0,places=10)
        self.assertAlmostEqual(r.omega,sd/.4,places=10)
        self.assertAlmostEqual(r.velocity_residual,0,places=10)
        self.assertEqual(b.angular_velocity,0)

    def test_close_restores_native_class_and_repeat(self):
        from pymunk._chipmunk_cffi import lib
        space,a,b,r=self.fixture()
        self.assertFalse(lib.cpConstraintIsGearJoint(r.constraint._constraint))
        r.close();r.close()
        self.assertTrue(lib.cpConstraintIsGearJoint(r.constraint._constraint))
        self.assertNotIn(r.constraint,space.constraints)
        with self.assertRaisesRegex(ValueError,'live constraint'):r.prepare(.001,0)
        for _ in range(25):
            other=attach(space,a,b,LinearGeometry(),1.,.6,0.)
            other.prepare(.001,0);space.step(.001);other.check();other.close()

    def test_callback_error_is_reported(self):
        space,a,b,r=self.fixture()
        r.geometry.inverse=lambda _s:float('nan')
        r.geometry.jacobian=lambda _q:float('nan')
        r.prepare(.001,0);space.step(.001)
        with self.assertRaisesRegex(ValueError,'native callback failed'):r.check()

    def test_variable_jacobian_energy_refines(self):
        errors=[]
        for dt in (.001,.0005,.00025):
            space,a,b,r=self.fixture(CosineGeometry(),q=1.2,qd=.5,inertia=.02)
            initial=.5*a.mass*a.velocity.length_squared+.5*b.mass*b.velocity.length_squared+r.kinetic
            for _ in range(round(.2/dt)):
                r.prepare(dt,0);space.step(dt);r.check()
            final=.5*a.mass*a.velocity.length_squared+.5*b.mass*b.velocity.length_squared+r.kinetic
            errors.append(abs(final-initial))
            self.assertAlmostEqual(r.velocity_residual,r._target,places=10)
            self.assertLess(abs(r.position_residual),.001)
            r.close()
        self.assertLess(errors[1],errors[0]*.6)
        self.assertLess(errors[2],errors[1]*.6)


if __name__=='__main__':unittest.main(verbosity=2)
