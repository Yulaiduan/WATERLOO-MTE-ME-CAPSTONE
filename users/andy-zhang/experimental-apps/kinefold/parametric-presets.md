# Parametric components and comparison studies

Andy Zhang / Codex, 2026-10-25. Experimental app workflow; no selected hardware
or validated motor capability is implied. Existing project-v3 designs remain
complete runnable snapshots, while component presets are independently reusable.

## Compose a design

The Presets & studies workspace saves four kinds of record:

| Kind | Saved inputs | Purpose |
| --- | --- | --- |
| Suspension / mechanism | Complete builder geometry, masses, gravity, loading, spring law and stops | Reuse one physical leg with many actuators |
| Motor / gearbox | Reduction, physical motor inputs, explicit unknowns, independent peak/speed/gearbox ratings | Reuse an actuator combination with many mechanisms |
| Input / case | Run settings, interaction/material, terrain dimensions, jump/landing commands and optional energy/target settings | Compare candidates against one captured excitation |
| Study | Full versioned copies of one mechanism, one input and multiple actuator presets, plus sweep controls | Reproduce a comparison after component presets change |

Capturing or saving components, selecting a study, calculating plots and running
a batch do not edit the current Studio design. **Open in studio** materializes
one selected combination into a validated project-v3 in one operation. Use the
existing named-design controls to retain that complete design separately.

Studies store resolved component values as well as identifiers and versions.
Editing or removing an original component therefore does not silently change
an older study. Components may be recaptured from an edited Studio design.
The System flow tab exposes the selected inputs, calculations, equations and
outputs as selectable nodes; it describes the active study, not a new solver.

## Inertia, friction and gearing

Let q be hip angle in radians and N = motor speed / hip speed. The existing
rigid ideal transmission gives:

```text
omega_motor = N qdot
tau_joint,electromagnetic = N tau_shaft
J_rotor,joint = N² J_motor
J_leg,motor = J_leg,joint / N²
b_motor,joint = N² b_motor
cogging_amplitude,joint = N A_motor
```

These relations follow rotational kinetic energy and ideal power conservation;
see [Modern Robotics 8.9](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-9-actuation-gearing-and-friction/).
The legacy additional hip inertia and joint damping remain separate additive
terms. Link inertias already enter each dynamic engine through its constrained
kinematics; they must not be multiplied by reduction again.

The pose/rate screen uses fixed-hip mechanism inertia from COM Jacobians and
body angular ratios, the builder's prescribed static loading, a selected joint
acceleration and signed joint speeds. Its inertial demand includes
`J(q) qddot + 0.5 J'(q) qdot²`. Rotor inertia adds `N² J_motor qddot`.
This reference screen differs from actual floating-chassis inverse dynamics.

**Constant cogging** is interpreted as constant entered amplitude A, with
conservative angle-dependent detent torque `A sin(k N q + phase)`. A constant
resisting magnitude belongs to the separate regularized Coulomb-friction term.
Viscous friction is `-b omega_motor` in N·m, with b in N·m·s/rad; it is zero
at rest. The existing full laws and numerical guards remain in
[motor-model.md](motor-model.md). Neither motor nor gearbox electrical
efficiency, compliance, backlash, stiction or a measured loss map is invented.

## Three different calculation scopes

1. **Pose/rate/acceleration screen:** sampled torque bands, speed and inertia
   transformations. Computed contour lines/bands use the actual sampled grid
   and offline Plotly scatter traces. Static equilibrium uses zero speed and
   acceleration; inertia and viscous friction then contribute no holding torque.
2. **Energy screens:** reuse the existing jump and landing work equations.
   Rest-endpoint inertia contributes no endpoint kinetic-energy change, and
   friction is given no braking-energy credit. Unsupported geometry, loading or
   moving masses remain unavailable with the existing explanation.
   An input's older standalone catalog selection is excluded from these batch
   work estimates; they use the newly composed candidate's physical reduction
   and cogging inputs consistently.
3. **Actual ¼ dynamics:** each candidate captures the same selected mechanism
   and input, then runs the analytical and/or Pymunk engine sequentially. Its
   physical motor configuration enters the existing engine equations. Returned
   trajectory ranges and operating points are distinct from the reference grid.

Batch results retain component snapshots, engine, resolved project and failures.
Cancellation stops scheduling further jobs; it does not claim to interrupt the
currently running server calculation. Partial and failed comparisons stay
visible. Different command bases must be read explicitly: identical numeric
shaft torque commands produce different hip torques at different reductions.

Peak torque, shaft speed and gearbox output limits are independent screens.
They do not form a measured torque-speed curve or guarantee simultaneous peak
torque and speed. A plot point within both bounds is not certified available
power, continuous operation, braking/regeneration or survival. Dynamic commands
are not silently clipped to catalog limits; observed exceedances are reported.

The screen separates electromagnetic torque (including upstream rotor and motor
passive compensation) from gearbox output load. Gearbox limits use the latter.
Contact/impact output torque cannot be recovered reliably from the sampled
electromagnetic command alone; those actual gearbox-load comparisons remain
unassessed. Sampled finite smooth prescribed-height rows can support a separate
output-load estimate when acceleration and all required terms are available.

## Unknown data and persistence

The existing dated catalog supplies Flipsky peak torque and EG23 reductions and
output ratings; its provenance is in [energy-calculator.md](energy-calculator.md).
Rotor inertia, speed, cogging and friction have no inferred catalog values.
Unknown ratings remain null/unassessed. Unknown passive fields are separately
flagged and cannot be composed into a simulation unless the user explicitly
chooses ideal-zero unknown passives for that study. Such zeros are study
assumptions, not measurements. The example study identifies this assumption.

Component records live in `profiles/presets.json`, independently of the original
`profiles/library.json`. They use a separate optimistic revision and atomic
writes. A conflict or failed write retains committed data and requires reload
before further writes. Whole-bundle imports validate before persistence and
create new copies rather than replacing saved records. Portable bundle and
result JSON exports use the app's `exports/` directory, never Downloads.
These local files are ignored by Git; transfer a reviewed bundle between PCs or
include it in the private local-file backup. A normal source pull alone does
not synchronize live preset libraries.

The existing [Start Kinefold.cmd](Start%20Kinefold.cmd) retains
`http://127.0.0.1:4191/`; new workspace routes are `?tab=presets` and `?tab=flow`.
Conventions remains the last tab, with the front-left +x-left/+z-up preview.
