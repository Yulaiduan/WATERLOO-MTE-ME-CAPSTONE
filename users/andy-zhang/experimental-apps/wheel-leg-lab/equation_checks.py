"""Cross-check the user reference equations and actual link momentum balances.

Invocation: imported by physics.py; call screenshot_reference with explicit dimensions.
Inputs: SI lengths/forces/moments, reference angles in degrees, distinct T0/T forces.
Outputs: reference algebra values and per-step residual dictionaries; no files.
Requires Pymunk vectors; ideal gear reactions are not explicit belt bearing loads.
Screenshot y/z map to engine x/y; numerical T0 and pulley definitions remain unresolved.
"""
import math
from pymunk import Vec2d

SCREENSHOT = {
    'load_vertical_N':111.58875,
    'load_horizontal_N':27.590625,
    'reported_Mact_0_Nm':83.752875,
    'reported_Mact_42_Nm':60.8231567152,
    'status':'Reported torques reproduced conditionally with inferred equal 400 mm links and a 200 mm wheel. Bearing-load match pending r_B/T0 values.',
    'torque_reproduction':{'assumptions':'L1 = L2 = 0.4 m inferred from the two reported moments, r_w = 0.2 m, Fy = 27.590625 N, Fz = 111.58875 N; dimensions are not independently confirmed.',
                          'samples':[{'theta_deg':0.,'reported_Nm':83.752875,'reproduced_Nm':.8*111.58875-.2*27.590625},
                                     {'theta_deg':42.,'reported_Nm':60.8231567152,'reproduced_Nm':.8*111.58875*math.cos(math.radians(42))-.2*27.590625}]},
    'mapping':{'reference_y':'engine x, horizontal right','reference_z':'engine y, vertical up',
               'reference_theta':'link angle from horizontal; separate upper/lower angles when solver drift exists',
               'F':'force from wheel on lower link = minus J3; prescribed hub force differs with wheel gravity/inertia',
               'B':'force from lower link on upper link = minus J2, before any explicit belt-span bearing correction',
               'T':'reference belt tension / tension difference; not the physical suspension spring tension',
               'T0':'user-confirmed belt tension in the fixed-direction span term; numerical value and tight/slack-span interpretation not supplied',
               'r_w':'wheel radius; reference wheel-contact torque is F_y * r_w',
               'beta':'reference belt-span angle; not the engine lower-link absolute angle',
               'q':'reference moment sign, not the fold coordinate used in older linkage tools',
               'f1':'absolute moment in N m, not the J1 joint force'},
    'visible_equations':[
        'F_z = g_z * (35 * 1.3 / 4) * 9.81',
        'F_y = g_y * (45 / 4) * 9.81',
        'M_in = L2 * (-F_z cos(theta) + F_y sin(theta)) + F_y r_w',
        'f1 = abs(M_in); q = sign(M_in)',
        'T = M_in / (q r_B) = abs(M_in) / r_B (for nonzero M_in)',
        'beta = theta - q asin(r_B / L1)',
        'B_y = F_y - T0 cos(theta) - T cos(beta)',
        'B_z = F_z + T0 sin(theta) + T sin(beta)',
        'M_act_visible = L1 * (B_z cos(theta) + B_y sin(theta))',
        'B_r = sqrt(B_y^2 + B_z^2)',
        'g2 = 50 + F_z - B_z + T sin(beta) = 50 - T0 sin(theta)',
        'g1 = 67 + F_y - B_y - T cos(beta) = 67 + T0 cos(theta)',
        'r_s = 0.04 [definition and units not confirmed]'],
    'derived_identity':'M_act_visible = L1 * (F_z cos(theta) + F_y sin(theta)) - M_in',
    'limitations':['Screenshot B includes explicit belt-span forces; ideal GearJoint pin loads are not an automatic bearing-load match.',
                   'Contact moment F_y r_w requires tire-bottom force and a wheel drive that transmits its reaction to the leg; free wheel / hub loading is a different case.',
                   'T0 is confirmed as belt tension; its value and the tight/slack-span relationship to T still require definition.',
                   'The 50/67 offsets and r_s are retained as reference inputs, not mapped to the 50 mm spring extension.']}

def screenshot_reference(theta_deg,L1,L2,F_y,F_z,r_B,*,r_w,T0,extra_min=0.,extra_mact=0.,offset_g1=67.,offset_g2=50.):
    """Evaluate the complete visible reference with distinct T0 and T forces.

    Angles enter in degrees; trig is radians. Lengths m, forces N, moments N m.
    This is a reference calculator, not a replacement for Pymunk dynamics.
    """
    numbers=(theta_deg,L1,L2,F_y,F_z,r_B,r_w,T0,extra_min,extra_mact,offset_g1,offset_g2)
    if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in numbers):raise ValueError('Reference inputs must be finite.')
    if L1<=0 or L2<=0 or r_B<=0 or r_B>L1:raise ValueError('Require positive lengths and 0 < r_B <= L1 for asin.')
    if r_w<0 or T0<0:raise ValueError('Wheel radius and T0 must be nonnegative.')
    theta=math.radians(theta_deg)
    Min=L2*(-F_z*math.cos(theta)+F_y*math.sin(theta))+F_y*r_w+extra_min
    q=1 if Min>0 else -1 if Min<0 else 0
    T=abs(Min)/r_B
    beta=theta-q*math.asin(r_B/L1)
    By=F_y-T0*math.cos(theta)-T*math.cos(beta)
    Bz=F_z+T0*math.sin(theta)+T*math.sin(beta)
    visible=L1*(Bz*math.cos(theta)+By*math.sin(theta))
    compact=L1*(F_z*math.cos(theta)+F_y*math.sin(theta))-Min
    return {'M_in':Min,'wheel_contact_moment':F_y*r_w,'abs_M_in':abs(Min),'q':q,'T':T,'T0':T0,'beta_deg':math.degrees(beta) if q else None,
            'B_y':By,'B_z':Bz,'B_r':math.hypot(By,Bz),'M_act_visible':visible,'M_act':visible+extra_mact,
            'g1':offset_g1+F_y-By-T*math.cos(beta),'g2':offset_g2+F_z-Bz+T*math.sin(beta),
            'identity_error_Nm':visible-compact,'g1_identity_error_N':offset_g1+T0*math.cos(theta)-(offset_g1+F_y-By-T*math.cos(beta)),
            'g2_identity_error_N':offset_g2-T0*math.sin(theta)-(offset_g2+F_z-Bz+T*math.sin(beta)),
            'belt_span_direction_defined':bool(q),
            'scope':'Complete visible screenshot algebra; this does not independently validate the physical interpretation of T0/T.'}

def moment_checks(model,c,f1,f2,f3,fs,au,al,angular_u,angular_l,torque,guide,stop,wheel_drive=0.):
    """Map visible r x F identities and full Newton-Euler balance to engine rows."""
    u,l=model['upper'],model['lower'];L=c['length']
    A=u.local_to_world(model['j1'].anchor_b);Bu=u.local_to_world(model['j2'].anchor_a)
    Bl=l.local_to_world(model['j2'].anchor_b);C=l.local_to_world(model['j3'].anchor_a)
    E=l.local_to_world(model['spring'].anchor_b)
    F=-f3;B=-f2
    tl=l.angle+math.pi;tu=-u.angle
    Min=L*(-F.y*math.cos(tl)+F.x*math.sin(tl))
    Mact=L*(B.y*math.cos(tu)+B.x*math.sin(tu))
    lower_cross=(C-Bl).cross(F);upper_cross=(Bu-A).cross(B)
    gravity_u=Vec2d(0,-u.mass*c['gravity']);gravity_l=Vec2d(0,-l.mass*c['gravity'])
    contact_ref=Min+F.x*c['radius']
    contact_cross=(C-Bl+Vec2d(0,-c['radius'])).cross(F)
    lower_total=lower_cross+(E-Bl).cross(fs)+(l.position-Bl).cross(gravity_l)+torque+guide+stop+wheel_drive
    lower_inertia=l.moment*angular_l+(l.position-Bl).cross(l.mass*al)
    upper_total=upper_cross+(u.position-A).cross(gravity_u)-torque+guide-stop
    upper_inertia=u.moment*angular_u+(u.position-A).cross(u.mass*au)
    return {'ref_Fy_horizontal':F.x,'ref_Fz_vertical':F.y,'ref_By_horizontal':B.x,'ref_Bz_vertical':B.y,
            'ref_Min_wheel_moment':Min,'ref_Mact_knee_moment':Mact,'ref_Br':math.hypot(B.x,B.y),
            'ref_Min_contact_moment':contact_ref,'ref_wheel_radius_moment':F.x*c['radius'],
            'check_contact_moment_Nm':contact_ref-contact_cross,
            'check_lower_moment_Nm':Min-lower_cross,'check_upper_moment_Nm':Mact-upper_cross,
            'check_lower_balance_Nm':lower_total-lower_inertia,'check_upper_balance_Nm':upper_total-upper_inertia}
