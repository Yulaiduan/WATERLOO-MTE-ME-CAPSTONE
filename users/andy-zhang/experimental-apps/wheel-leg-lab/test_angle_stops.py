"""Check impact energy, held stops and release in the independent angular solver.

Run .venv/Scripts/python.exe -m unittest test_angle_stops in this app.
Inputs radians, seconds, unit inertia and piecewise torque (N m).
Outputs assertions on stop motion/energy. No floor or hardware validation.
"""
import unittest
import numpy as np
from angle_stops import integrate


class StopTests(unittest.TestCase):
    def test_impact_hold_release_and_energy(self):
        def evaluate(t,y):
            force=1 if t<1.5 else -1
            return [y[1],force,force*y[1],0.]
        times=np.linspace(0,2.5,251)
        states,losses,impacts=integrate(evaluate,lambda q:1.,times,(0.,0.,0.,0.),(-.5,.5))
        self.assertAlmostEqual(impacts[0],1.,places=6)
        self.assertAlmostEqual(states[0,-1],0.,places=6)
        self.assertTrue(np.allclose(states[0,110:140],.5))
        self.assertTrue(np.allclose(states[1,110:140],0.))
        self.assertLess(np.max(np.abs(.5*states[1]**2-states[2]+losses)),1e-5)

    def test_zero_acceleration_at_bound_does_not_chatter(self):
        def evaluate(t,y):
            force=0 if t<.2 else -1
            return [y[1],force,force*y[1],0.]
        times=np.linspace(0,.5,51)
        states,losses,impacts=integrate(evaluate,lambda q:1.,times,(.5,0.,0.,0.),(-.5,.5))
        self.assertEqual(impacts,[]);self.assertEqual(losses[-1],0)
        self.assertAlmostEqual(states[0,-1],.455,places=6)


if __name__=='__main__':unittest.main()
