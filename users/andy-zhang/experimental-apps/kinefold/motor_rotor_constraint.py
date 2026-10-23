"""Experimental native-PGS scalar hip rotor with no translational mass.

Imported by contact_dynamics; attach(space,chassis,wheel,geometry,Jjoint,q0,qd0),
prepare(dt, joint_torque_Nm), space.step(dt), check(), and close() in finally.
Inputs SI kg/m/s/rad; Jjoint is motor inertia already reflected to hip kg m².
Outputs scalar angle/rate/kinetic energy, velocity residual and impulse work.
The virtual rotational degree of freedom participates in every native Pymunk
constraint iteration, alongside terrain and travel stops. Private ABI bridge is
strictly pinned to Pymunk 7.3.0, 64-bit pointers and double precision. There is no
fallback, epsilon body mass, wheel-spin inertia substitution or tire model.

ABI reference: Munk2D ade7ed72849e60289eefb7a41e79ae6322fefaf3,
https://github.com/viblo/Munk2D/blob/ade7ed72849e60289eefb7a41e79ae6322fefaf3/include/chipmunk/chipmunk_structs.h
cpConstraint/cpConstraintClass, and src/cpGearJoint.c at the same commit. Only the
first class pointer is replaced; allocation/free and body registration remain
Pymunk-owned. Callbacks are retained by the Python constraint for its lifetime.
"""
import ctypes
import math
import platform

_ENGINE_VERSION = '2.0.1-ade7ed72849e60289eefb7a41e79ae6322fefaf3'

_STEP = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_double)
_GET = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_void_p)


class _Class(ctypes.Structure):
    _fields_ = [('pre', _STEP), ('cached', _STEP), ('solve', _STEP), ('impulse', _GET)]


class NativeRotor:
    """Scalar q-rotor coupled by theta - q(s)=0 inside the native PGS solve."""

    def __init__(self, space, chassis, wheel, geometry, inertia, q0, qd0):
        import pymunk
        from pymunk._chipmunk_cffi import ffi, lib
        if (pymunk.version != '7.3.0' or pymunk.chipmunk_version != _ENGINE_VERSION
                or ctypes.sizeof(ctypes.c_void_p) != 8
                or platform.system() != 'Windows' or platform.machine().lower() not in ('amd64', 'x86_64')
                or ffi.sizeof('cpFloat') != 8 or ffi.sizeof('cpVect') != 16
                or ctypes.sizeof(_Class) != 32):
            raise ValueError('Virtual rotor native ABI is verified only for Windows AMD64, Pymunk 7.3.0, Munk2D '+_ENGINE_VERSION+', 64-bit pointers and double precision.')
        if not math.isfinite(inertia) or inertia <= 0:
            raise ValueError('Native rotor requires strictly positive reflected hip inertia; bypass it when inertia is zero.')
        if space.sleep_time_threshold != math.inf:
            raise ValueError('Virtual rotor requires sleeping disabled so its scalar degree of freedom is always solved.')
        if chassis.mass <= 0 or wheel.mass <= 0 or not math.isfinite(chassis.mass+wheel.mass):
            raise ValueError('Virtual rotor requires finite positive actual chassis and wheel masses.')
        self.space, self.chassis, self.wheel, self.geometry = space, chassis, wheel, geometry
        self.inertia, self.angle, self.omega = float(inertia), float(q0), float(qd0)
        self.axis = tuple(geometry.axis)
        if len(self.axis) != 2 or abs(sum(a*a for a in self.axis)-1) > 1e-10:
            raise ValueError('Virtual rotor requires a unit straight guide axis.')
        self.torque = self.dt = self.accumulated_impulse = self.constraint_work_j = 0.
        self.error = None
        self.closed = False
        self._a = self._denominator = self._target = 0.
        # Public native allocator establishes the complete, correctly sized base.
        ptr = lib.cpGearJointNew(chassis._body, wheel._body, 0., 1.)
        if ptr == ffi.NULL:
            raise ValueError('Virtual rotor native constraint allocation failed.')
        address = int(ffi.cast('uintptr_t', ptr))
        self._slot = ctypes.cast(address, ctypes.POINTER(ctypes.c_void_p))
        self._original = self._slot[0]
        if (address % 8 or not self._original or self._original % 8
                or not lib.cpConstraintIsGearJoint(ptr)):
            lib.cpConstraintFree(ptr)
            raise ValueError('Virtual rotor native constraint class layout guard failed.')
        old_class = ctypes.cast(self._original, ctypes.POINTER(_Class)).contents
        if not all(ctypes.cast(getattr(old_class, name), ctypes.c_void_p).value
                   for name in ('pre', 'cached', 'solve', 'impulse')):
            lib.cpConstraintFree(ptr)
            raise ValueError('Virtual rotor native class has an invalid callback table.')
        if old_class.impulse(address) != 0:
            lib.cpConstraintFree(ptr)
            raise ValueError('Virtual rotor native callback signature guard failed.')
        constraint = pymunk.Constraint.__new__(pymunk.Constraint)
        constraint._init(chassis, wheel, ptr)
        self.constraint = constraint
        self._callbacks = (_STEP(self._pre), _STEP(self._cached),
                           _STEP(self._solve), _GET(self._get))
        self._class = _Class(*self._callbacks)
        self._slot[0] = ctypes.addressof(self._class)
        # Retain bridge/callbacks until constraint removal, even if caller drops us.
        constraint._virtual_rotor_owner = self
        try:
            constraint.collide_bodies = False
            space.add(constraint)
        except BaseException:
            self._slot[0] = self._original
            constraint._virtual_rotor_owner = None
            raise

    def _failed(self, error):
        self.error = self.error or str(error)

    def _pre(self, _ptr, dt):
        try:
            relative = self.wheel.position-self.chassis.position
            distance = relative.x*self.axis[0]+relative.y*self.axis[1]
            q = self.geometry.inverse(distance)
            jacobian = self.geometry.jacobian(q)
            if not math.isfinite(jacobian) or abs(jacobian) < 1e-8:
                raise ValueError('Rotor guide Jacobian is singular.')
            self._a = 1/jacobian
            self._denominator = self._a**2*(1/self.chassis.mass+1/self.wheel.mass)+1/self.inertia
            # Native position-first integration advances angle before this solve.
            # Error correction is explicit and bounded; numerical work is exposed.
            coefficient = 1-(1-.2)**(60*dt)
            self._target = max(-10., min(10., -coefficient*(self.angle-q)/dt))
            self.omega += self.torque/self.inertia*dt
            self.accumulated_impulse = 0.
        except BaseException as error:
            self._failed(error)

    def _cached(self, _ptr, _dt_coefficient):
        # Cold starts avoid stale impulses across nonlinear geometry/contact changes.
        return

    def _solve(self, _ptr, _dt):
        if self.error:
            return
        try:
            a, b = self.chassis, self.wheel
            av, bv = a.velocity, b.velocity
            relative = (bv.x-av.x)*self.axis[0]+(bv.y-av.y)*self.axis[1]
            impulse = (self._target-(self.omega-self._a*relative))/self._denominator
            before = .5*a.mass*av.length_squared+.5*b.mass*bv.length_squared+self.kinetic
            dx, dz = self._a*self.axis[0]*impulse, self._a*self.axis[1]*impulse
            a.velocity = (av.x+dx/a.mass, av.y+dz/a.mass)
            b.velocity = (bv.x-dx/b.mass, bv.y-dz/b.mass)
            self.omega += impulse/self.inertia
            self.accumulated_impulse += impulse
            self.constraint_work_j += (.5*a.mass*a.velocity.length_squared
                +.5*b.mass*b.velocity.length_squared+self.kinetic-before)
        except BaseException as error:
            self._failed(error)

    def _get(self, _ptr):
        return abs(self.accumulated_impulse)

    def prepare(self, dt, torque):
        """Advance scalar angle at old rate, then schedule the native force kick."""
        self.check()
        if self.closed or not math.isfinite(dt) or dt <= 0 or not math.isfinite(torque):
            raise ValueError('Virtual rotor prepare requires a live constraint, positive dt and finite hip torque.')
        self.dt, self.torque = dt, torque
        self.angle += self.omega*dt

    def check(self):
        """Surface callback failures after space.step; exceptions cannot cross C."""
        if self.error:
            raise ValueError('Virtual rotor native callback failed: '+self.error)
        if not math.isfinite(self.angle+self.omega+self.constraint_work_j):
            raise ValueError('Virtual rotor state diverged.')

    @property
    def kinetic(self):
        return .5*self.inertia*self.omega**2

    @property
    def velocity_residual(self):
        relative = self.wheel.velocity-self.chassis.velocity
        return self.omega-self._a*(relative.x*self.axis[0]+relative.y*self.axis[1])

    @property
    def position_residual(self):
        relative = self.wheel.position-self.chassis.position
        distance = relative.x*self.axis[0]+relative.y*self.axis[1]
        return self.angle-self.geometry.inverse(distance)

    def close(self):
        """Remove native callback use before restoring/freeing the allocated joint."""
        if self.closed:
            return
        if self.constraint in self.space.constraints:
            self.space.remove(self.constraint)
        self._slot[0] = self._original
        self.constraint._virtual_rotor_owner = None
        self.closed = True


def attach(space, chassis, wheel, geometry, inertia, q0, qd0):
    """Attach a positive reflected hip inertia; caller owns close() in finally."""
    return NativeRotor(space, chassis, wheel, geometry, inertia, q0, qd0)
