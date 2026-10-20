# Passive descent studies: sharing handoff

Yulai Duan with Codex, October 20, 2026. Publication base: `307aae0`.
Status: completed experimental studies and analytical checks, not accepted design
choices or physical measurements. The user requested publication for team sharing.

Start at the [study index](../../../docs/design/simulation/descent-studies.md),
then read the [study app context](../../../users/yulai-duan/experimental-apps/block-descent-study/context/README.md).
The batch retains 11 original fixture runs, ten original block-height runs,
analytical quintic/corner screening, and 22 new 8.75 kg/20° baseline runs.

Main finding: static grounded support does not cancel airborne extension.
At the initial pose, the spring and assumed moving-body gravity both extend the
held-hip leg; the quasi-static hold calculation is not a motor rating. New held-hip
100/150 mm landings occur at 275/299 ms. At 250/300 mm, chassis motion is necessary
to bridge the 93/143 mm gap after the remaining extension is used.

Hip held fixes vertical attachment position but permits joint rotation. Heave
free permits body vertical motion with pitch and horizontal speed constrained.
Recovering contact means bringing the wheel back to the floor, not restoring ride
height or guaranteeing a controlled touchdown. Finite moving masses, drift,
recoil and travel-stop hits limit the heave interpretation.

The portable code was rerun before publication and compared against retained
physical metrics. Raw trajectories and private screenshots are excluded from Git.
Next agree on masses, physical stops and braking objectives, then add drivetrain
dynamics and full-vehicle load sharing. No motor/gearbox is selected by this work.
