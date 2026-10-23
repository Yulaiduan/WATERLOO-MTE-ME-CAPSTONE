"""Optional ideal geared motor laws shared by experimental dynamics engines.

Import Motor.resolve(optional_config), then joint_command(Nm) and
motor_state(q_rad, qdot_rad_s, joint_command_Nm). Outputs SI shaft/joint
torques, energies and nonnegative loss powers. Positive gear ratio is motor
speed/joint speed; motor angle is N*q with fixed zero reference. Cogging is
an ideal conservative sinusoid; regularized Coulomb drag is not stiction.
Zero defaults are compatibility settings, not measured hardware properties.
"""
import math


DEFAULTS = dict(enabled=False, gearRatio=1, rotorInertiaKgM2=0,
                coggingAmplitudeNm=0, coggingPeriodsPerRev=1, coggingPhaseDeg=0,
                coulombFrictionNm=0, viscousFrictionNms=0,
                frictionVelocityScaleRadS=.01, commandBasis='joint')
BOUNDS = dict(gearRatio=(1e-6, 1e4), rotorInertiaKgM2=(0, 1000),
              coggingAmplitudeNm=(0, 10000), coggingPeriodsPerRev=(1, 10000),
              coggingPhaseDeg=(-360, 360), coulombFrictionNm=(0, 10000),
              viscousFrictionNms=(0, 10000), frictionVelocityScaleRadS=(1e-6, 1000))


class Motor:
    @classmethod
    def resolve(cls, config=None):
        if config is not None and (not isinstance(config, dict) or set(config) != set(DEFAULTS)):
            raise ValueError('motorConfig must contain exactly the documented motor keys.')
        c = dict(DEFAULTS if config is None else config)
        if type(c['enabled']) is not bool or c['commandBasis'] not in ('joint', 'motor'):
            raise ValueError('Motor enabled must be boolean and commandBasis joint or motor.')
        for key, (lo, hi) in BOUNDS.items():
            x = c[key]
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or not lo <= x <= hi:
                raise ValueError(f'Motor {key} must be finite within [{lo}, {hi}].')
        if int(c['coggingPeriodsPerRev']) != c['coggingPeriodsPerRev']:
            raise ValueError('Motor coggingPeriodsPerRev must be an integer.')
        obj = cls()
        obj.config, obj.enabled = c, c['enabled']
        obj.reflected_inertia = c['gearRatio'] ** 2 * c['rotorInertiaKgM2'] if obj.enabled else 0
        return obj

    def joint_command(self, value):
        return value * self.config['gearRatio'] if self.enabled and self.config['commandBasis'] == 'motor' else value

    def check_step(self, qdot, dt):
        """Reject cogging phase advances above 0.25 rad per integration step."""
        c = self.config
        if self.enabled and c['coggingAmplitudeNm'] > 0:
            rate = abs(qdot) * c['gearRatio'] * c['coggingPeriodsPerRev']
            if rate * dt > .25:
                raise ValueError(f'Motor cogging is underresolved; reduce dt below {(.25 / rate):.8g} s (maximum cogging phase step 0.25 rad).')

    def check_friction_step(self, effective_joint_inertia, dt):
        """Bound explicit near-zero drag relaxation; this is not a stiction law."""
        c = self.config
        if not self.enabled:
            return
        slope = c['gearRatio'] ** 2 * (c['coulombFrictionNm'] / c['frictionVelocityScaleRadS'] + c['viscousFrictionNms'])
        if slope > 0 and slope * dt > .5 * effective_joint_inertia:
            limit = .5 * effective_joint_inertia / slope
            raise ValueError(f'Motor friction is underresolved; reduce dt below {limit:.8g} s or increase the smoothing speed/inertia (near-zero explicit drag stability guard).')

    def motor_state(self, q, qd, joint_command):
        c = self.config
        if not self.enabled:
            return dict(motorAngleRad=0, motorVelocityRadS=0, shaftCommandNm=joint_command,
                        jointElectromagneticNm=joint_command, jointCoggingNm=0, jointFrictionNm=0,
                        jointPassiveNm=0, rotorKineticJ=0, coggingPotentialJ=0,
                        coulombLossPowerW=0, viscousLossPowerW=0, motorLossPowerW=0)
        n, k = c['gearRatio'], c['coggingPeriodsPerRev']
        angle, speed = n * q, n * qd
        phase = k * angle + math.radians(c['coggingPhaseDeg'])
        cog = c['coggingAmplitudeNm'] * math.sin(phase)
        coulomb = -c['coulombFrictionNm'] * math.tanh(speed / c['frictionVelocityScaleRadS'])
        viscous = -c['viscousFrictionNms'] * speed
        return dict(motorAngleRad=angle, motorVelocityRadS=speed, shaftCommandNm=joint_command / n,
                    jointElectromagneticNm=joint_command, jointCoggingNm=n * cog,
                    jointFrictionNm=n * (coulomb + viscous), jointPassiveNm=n * (cog + coulomb + viscous),
                    rotorKineticJ=.5 * self.reflected_inertia * qd * qd,
                    coggingPotentialJ=c['coggingAmplitudeNm'] / k * math.cos(phase),
                    coulombLossPowerW=-coulomb * speed, viscousLossPowerW=-viscous * speed,
                    motorLossPowerW=-(coulomb + viscous) * speed)
