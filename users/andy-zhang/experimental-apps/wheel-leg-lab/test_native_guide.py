"""Verify native signed guide-torque display against measured solver rows.

Run: .venv/Scripts/python.exe -m unittest test_native_guide. Inputs: SI floating
wheel profiles and prescribed height; outputs: torque/impulse parity assertions.
Requires Pymunk/pygame; does not create windows or validate belt bearing loads.
"""
import unittest
from physics import config,build,drive,simulate
from suspension_architecture import constant_lift_profile
from native_guide_belt import capture_torque

class NativeGuideTests(unittest.TestCase):
    def test_signed_torque_matches_live_body_balance(self):
        for raw in ({},constant_lift_profile(),dict(constant_lift_profile(),wheel_drive_locked=True)):
            c=config(dict(raw,duration=.4,start=.05,rise=.15,position_amplitude=.005))
            reference=simulate(c);m=build(c)
            for i,row in enumerate(reference['rows']):
                velocities={key:m[key].velocity for key in ('upper','lower','hip','wheel')}
                spins={key:m[key].angular_velocity for key in ('upper','lower','wheel')}
                _,torque,*_=drive(m,c,i*c['dt'],c['dt']);m['live_actuator']=torque
                m['space'].step(c['dt'])
                measured=capture_torque(m,c,velocities,spins,c['dt'])
                self.assertAlmostEqual(measured,row['guide_link_torque'],places=9)
                self.assertAlmostEqual(abs(measured),m['guide'].impulse/c['dt'],places=8)

if __name__=='__main__':unittest.main()
