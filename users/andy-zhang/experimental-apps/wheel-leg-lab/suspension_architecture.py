"""Build the editable two-stage constant-lift wheel suspension demo profile.

Invocation: constant_lift_profile(), served by /api/suspension-architecture/defaults.
Inputs: existing SI experimental defaults; outputs: validated flat solver config.
The 200 mm wheel and 2:1 folding leg have gravity compensation plus an independent
original-tip captured ride spring/damper. All dimensions/rates are editable demo
values. Bilateral wheel-height fixture, pitch held; no tire or hardware validation.
"""
from physics import DEFAULTS, config, build
from spring_mechanisms import apply_preset


def constant_lift_profile():
    c=apply_preset(DEFAULTS,'gravity_balance')
    c.update(fixture='floating',target='position',radius=.2,damping=0.,
             aux_spring_enabled=True,aux_stiffness=8000.,aux_damping=500.,
             aux_mode='captured',aux_auto_rest=True,knee_kp=0.,knee_kd=0.)
    c=config(c)
    build(c)  # Resolve gravity rate and validate real architecture geometry.
    return c
