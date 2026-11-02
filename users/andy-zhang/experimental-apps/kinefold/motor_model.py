"""Optional ideal geared motor laws shared by experimental dynamics engines.

Import Motor.resolve(optional_config), then joint_command(Nm) and
motor_state(q_rad, qdot_rad_s, joint_command_Nm). Outputs SI shaft/joint
torques, energies and nonnegative loss powers. Positive gear ratio is motor
speed/gearbox-output speed; optional hipBeltRatio (1..3) multiplies the
gearbox reduction through an ideal extra belt. Total motor angle is N*q with fixed zero reference. Cogging is
an ideal conservative sinusoid. The legacy coulombFrictionNm key is the shaft
static/breakaway threshold; the same magnitude is assumed during sliding.
Dry torque is solved by each engine's bounded constraint, never a smooth force.
Zero defaults are compatibility settings, not measured hardware properties.
"""
import math

FRICTION_CONVENTION = 'set-valued-static-breakaway-v1'


DEFAULTS = dict(enabled=False, gearRatio=1, hipBeltRatio=1, rotorInertiaKgM2=0, gearboxInputInertiaKgM2=0,
                coggingAmplitudeNm=0, coggingPeriodsPerRev=1, coggingPhaseDeg=0,
                coulombFrictionNm=0, viscousFrictionNms=0,
                frictionVelocityScaleRadS=.01, commandBasis='joint')
BOUNDS = dict(hipBeltRatio=(1, 3), gearRatio=(1e-6, 1e4), rotorInertiaKgM2=(0, 1000), gearboxInputInertiaKgM2=(0, 1000),
              coggingAmplitudeNm=(0, 10000), coggingPeriodsPerRev=(1, 10000),
              coggingPhaseDeg=(-360, 360), coulombFrictionNm=(0, 10000),
              viscousFrictionNms=(0, 10000), frictionVelocityScaleRadS=(1e-6, 1000))


class Motor:
    @classmethod
    def resolve(cls, config=None):
        allowed = set(DEFAULTS)
        required = allowed - {'gearboxInputInertiaKgM2', 'hipBeltRatio'}
        if config is not None and (not isinstance(config, dict) or not required <= set(config) <= allowed):
            raise ValueError('motorConfig must contain exactly the documented motor keys.')
        c = dict(DEFAULTS if config is None else config)
        if type(c['enabled']) is not bool or c['commandBasis'] not in ('joint', 'motor'):
            raise ValueError('Motor enabled must be boolean and commandBasis joint or motor.')
        for key, (lo, hi) in BOUNDS.items():
            x = c.get(key, DEFAULTS[key])
            if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or not lo <= x <= hi:
                raise ValueError(f'Motor {key} must be finite within [{lo}, {hi}].')
        if int(c['coggingPeriodsPerRev']) != c['coggingPeriodsPerRev']:
            raise ValueError('Motor coggingPeriodsPerRev must be an integer.')
        obj = cls()
        obj.config, obj.enabled = c, c['enabled']
        # Preserve a legacy capture's original keys; zero is compatibility, not data.
        obj.total_ratio = c['gearRatio'] * c.get('hipBeltRatio', 1)
        obj.reflected_inertia = obj.total_ratio ** 2 * (c['rotorInertiaKgM2'] + c.get('gearboxInputInertiaKgM2', 0)) if obj.enabled else 0
        obj.static_capacity = obj.total_ratio * c['coulombFrictionNm'] if obj.enabled else 0.
        return obj

    def joint_command(self, value):
        return value * self.total_ratio if self.enabled and self.config['commandBasis'] == 'motor' else value

    def check_step(self, qdot, dt):
        """Reject cogging phase advances above 0.25 rad per integration step."""
        c = self.config
        if self.enabled and c['coggingAmplitudeNm'] > 0:
            rate = abs(qdot) * self.total_ratio * c['coggingPeriodsPerRev']
            if rate * dt > .25:
                raise ValueError(f'Motor cogging is underresolved; reduce dt below {(.25 / rate):.8g} s (maximum cogging phase step 0.25 rad).')

    def check_friction_step(self, effective_joint_inertia, dt):
        """Bound explicit viscous relaxation; dry friction is an implicit constraint."""
        c = self.config
        if not self.enabled:
            return
        slope = self.total_ratio ** 2 * c['viscousFrictionNms']
        if slope > 0 and slope * dt > .5 * effective_joint_inertia:
            limit = .5 * effective_joint_inertia / slope
            raise ValueError(f'Motor viscous friction is underresolved; reduce dt below {limit:.8g} s (explicit viscous stability guard).')

    def dry_torque(self, velocity, drive, inertia=None, dt=None):
        """Resolve scalar inclusion; optional backward-Euler bounded impulse in SI.

        drive excludes dry friction. At rest any opposing torque up to capacity
        is admissible. A timestep solve includes momentum, so moving states may
        stop/re-stick without sign chatter or a velocity deadband.
        """
        cap = self.static_capacity
        if not cap:return 0.
        if dt is not None:
            demand = drive + inertia * velocity / dt
            return -max(-cap, min(cap, demand))
        if velocity:return -math.copysign(cap, velocity)
        return -max(-cap, min(cap, drive))

    def motor_state(self, q, qd, joint_command, dry_torque=0., friction_state=None):
        c = self.config
        if not self.enabled:
            return dict(motorAngleRad=0, motorVelocityRadS=0, shaftCommandNm=joint_command,
                        jointElectromagneticNm=joint_command, jointCoggingNm=0, jointFrictionNm=0,
                        jointPassiveNm=0, rotorKineticJ=0, coggingPotentialJ=0,
                        coulombLossPowerW=0, viscousLossPowerW=0, motorLossPowerW=0,
                        frictionConvention=FRICTION_CONVENTION,frictionState='disabled',
                        jointStaticFrictionCapacityNm=0.,jointDryFrictionNm=0.,jointStaticFrictionNm=0.,jointSlidingFrictionNm=0.,jointViscousFrictionNm=0.,dryFrictionConstraintSaturated=False)
        n, k = self.total_ratio, c['coggingPeriodsPerRev']
        angle, speed = n * q, n * qd
        phase = k * angle + math.radians(c['coggingPhaseDeg'])
        cog = c['coggingAmplitudeNm'] * math.sin(phase)
        viscous = -c['viscousFrictionNms'] * speed
        state=friction_state or ('off' if not self.static_capacity else 'sliding' if qd else 'sticking')
        # Forces/controllers call this with zero dry torque; engine solve owns it.
        dry=float(dry_torque);dry_power=0. if state=='sticking' else max(0.,-dry*qd)
        return dict(motorAngleRad=angle, motorVelocityRadS=speed, shaftCommandNm=joint_command / n,
                    jointElectromagneticNm=joint_command, jointCoggingNm=n * cog,
                    jointFrictionNm=dry+n*viscous, jointPassiveNm=n*cog+dry+n*viscous,
                    rotorKineticJ=.5 * self.reflected_inertia * qd * qd,
                    coggingPotentialJ=c['coggingAmplitudeNm'] / k * math.cos(phase),
                    coulombLossPowerW=dry_power, viscousLossPowerW=-viscous * speed,
                    motorLossPowerW=dry_power-viscous*speed,frictionConvention=FRICTION_CONVENTION,
                    frictionState=state,jointStaticFrictionCapacityNm=self.static_capacity,
                    dryFrictionConstraintSaturated=bool(self.static_capacity and abs(dry)>=self.static_capacity*(1-1e-10)),
                    jointDryFrictionNm=dry,jointStaticFrictionNm=dry if state=='sticking' else 0.,
                    jointSlidingFrictionNm=dry if state=='sliding' else 0.,jointViscousFrictionNm=n*viscous)
