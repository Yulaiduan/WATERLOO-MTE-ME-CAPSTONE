"""Build the editable replacement constant-lift wheel suspension demo profile.

Invocation: constant_lift_profile(), served by /api/suspension-architecture/defaults.
Inputs: existing SI experimental defaults; outputs: validated flat solver config.
The 200 mm wheel and 2:1 folding leg use one upper-link-to-chassis gravity
compensating spring/damper, replacing the original hip-to-lower-tip strut.
Exact compensation has neutral elastic ride stiffness; no restoring strut is
silently added. The separate auxiliary variant remains an explicit option.
Dimensions/rates are editable demos. Bilateral height fixture, fixed pitch;
guide sensors add no mass/contact/belt bearing loads or hardware validation.
"""
from physics import DEFAULTS, config, build
from spring_mechanisms import apply_preset


def constant_lift_profile():
    c=apply_preset(DEFAULTS,'gravity_balance')
    c.update(fixture='floating',target='position',radius=.2,damping=100.,
             aux_spring_enabled=False,chassis_shape_enabled=True,
             guide_pulleys_visible=True,guide_hip_radius=.028,
             knee_kp=0.,knee_kd=0.)
    c=config(c)
    build(c)  # Resolve gravity rate and validate real architecture geometry.
    return c
