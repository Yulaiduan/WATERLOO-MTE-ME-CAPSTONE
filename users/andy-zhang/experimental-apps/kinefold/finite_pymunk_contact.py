"""Native finite uniform-rod VSL linkage for the experimental contact engine.

Imported by contact_dynamics; SI kg/metres/radians/seconds. Builds actual upper
and lower dynamic rods, three pivots, an absolute-angle belt GearJoint and hip
limits. Chassis/wheel are supplied native bodies. Returns native energy and
constraint diagnostics. No contact integration, GUI or hardware claim here.
Pymunk GearJoint: ratio*angle_b-angle_a=phase (Chipmunk cpGearJoint.c).
"""
import math


class FiniteLinkage:
    def __init__(self,space,m,chassis,wheel,q,h,vh,qd):
        import pymunk
        self.m,self.chassis,self.wheel=m,chassis,wheel
        p=m.p;self.upper=pymunk.Body(p['m2'],m.I['2']+m.Jref)
        self.lower=pymunk.Body(p['m3'],m.I['3'])
        for body,key,angle,rate in ((self.upper,'2',q-math.pi-p['alpha']*math.pi/180,1.),
                (self.lower,'3',p['phi0']*math.pi/180+(math.pi-q)*(m.ab-1)-math.pi-p['alpha']*math.pi/180,m.k3)):
            pos,vel,_=m.sites(q)[key]
            body.position=(pos[0],h+pos[1]);body.angle=angle
            body.velocity=(vel[0]*qd,vh+vel[1]*qd);body.angular_velocity=rate*qd
        space.add(self.upper,self.lower)
        L=p['L2']/1000;l=p['L3']/1000
        self.pivots=[pymunk.PivotJoint(chassis,self.upper,(0,0),(-L/2,0)),
            pymunk.PivotJoint(self.upper,self.lower,(L/2,0),(-l/2,0)),
            pymunk.PivotJoint(self.lower,wheel,(l/2,0),(0,0))]
        ratio=1/m.k3
        self.gear=pymunk.GearJoint(self.upper,self.lower,ratio*self.lower.angle-self.upper.angle,ratio)
        offset=math.pi+p['alpha']*math.pi/180
        self.stop=pymunk.RotaryLimitJoint(chassis,self.upper,m.lo-offset,m.hi-offset)
        for con in self.pivots+[self.gear,self.stop]:con.collide_bodies=False
        space.add(*self.pivots,self.gear,self.stop)

    def state(self):
        m=self.m;q=self.upper.angle+math.pi+m.p['alpha']*math.pi/180
        qd=self.upper.angular_velocity
        residual=max((a.a.local_to_world(a.anchor_a)-a.b.local_to_world(a.anchor_b)).length for a in self.pivots)*1000
        expected=m.sites(q)['6'][0];actual=self.wheel.position-self.chassis.position
        return q,qd,max(residual,math.hypot(actual.x-expected[0],actual.y-expected[1])*1000)

    def angle_residual(self):
        return abs(self.gear.ratio*self.lower.angle-self.upper.angle-self.gear.phase)*180/math.pi

    def apply(self,torque):
        self.upper.torque=torque;self.lower.torque=0.;self.chassis.torque=-torque

    def energies(self):
        m=self.m;u,l=self.upper,self.lower
        upper=.5*u.mass*u.velocity.length_squared+.5*m.I['2']*u.angular_velocity**2
        lower=.5*l.mass*l.velocity.length_squared+.5*m.I['3']*l.angular_velocity**2
        gravity=m.p['g']*sum(b.mass*b.position.y for b in (self.chassis,u,l,self.wheel))
        return dict(linkKineticJ=upper+lower,upperLinkKineticJ=upper,lowerLinkKineticJ=lower,
            rotorKineticJ=.5*m.motor.reflected_inertia*u.angular_velocity**2,
            legacyJointRotorKineticJ=.5*m.c['hipRotorInertiaKgM2']*u.angular_velocity**2,gravityEnergyJ=gravity)

    def free_kinetic(self,dt):
        g=self.m.p['g'];total=0.
        for b in (self.chassis,self.upper,self.lower,self.wheel):
            vx=b.velocity.x+b.force.x/b.mass*dt;vy=b.velocity.y+(b.force.y/b.mass-g)*dt
            omega=b.angular_velocity+(b.torque/b.moment*dt if math.isfinite(b.moment) else 0.)
            total+=.5*b.mass*(vx*vx+vy*vy)
            if math.isfinite(b.moment):total+=.5*b.moment*omega*omega
        return total

    def kinetic(self):
        return sum(.5*b.mass*b.velocity.length_squared+(.5*b.moment*b.angular_velocity**2 if math.isfinite(b.moment) else 0.) for b in (self.chassis,self.upper,self.lower,self.wheel))
