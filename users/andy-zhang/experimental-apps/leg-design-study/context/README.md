# Design report handoff

Andy Zhang with Codex, 2026-10-14. Source base: `6c74cfd`; publication is the
commit adding this folder. Read [the context index](../context.md).

The initial implementation was checked inside a development Motion Lab study.
The owner then clarified that delivery must be an offline static HTML webpage
and PDF, without adding the study to Motion Lab tooling. The unshipped UI/API
integration was removed; equations, selected evidence, tests and design history
are retained here. Earlier browser/backend checks in validation are development
history, not claims about controls on the static page.

The compact bounded peak-search example is L2=180, L3=340 mm, qab=1.775 and
alpha=4.375 degrees. A 325 mm total capacity with 20 mm at each end gives 285 mm
usable travel. Both link bounds are active; a larger-link search lowers torque
at the cost of size and drift, so this is a conditional compromise, not a global
minimum. Peak and RMS objectives select different designs.

The physical example assumes m1=8.3, m2=m3=.35, m5=.10 and m6=.90 kg (10 kg
per leg), with 11.25 kg sensitivity for a 45 kg robot. The screenshot's zero
moving masses remain an analytical limit. The hip-bellcrank spring fit is
4.3698 N/mm and 213.95 N installed preload; its one-second 285 mm stroke needs
6.449 Nm peak / 3.641 Nm RMS direct hip-input torque, 1.605 rad/s and 6.573 rad/s².
The guide ratio and optional motor gearing are separate power mappings.

All nine spring topologies are generalized and checked against the existing
2D force laws and actual Pymunk stepping. Both movement directions are checked.
Three/four/five-g held-load sensitivities do not predict impact events; spring
packaging, drivetrain inertia, thermal duty, impact stroke and contact sharing
remain unresolved. No damping, hardware, canonical robot or GPU validation is
claimed. Historical dual-rope remains IMPOSSIBLE / rejected.
