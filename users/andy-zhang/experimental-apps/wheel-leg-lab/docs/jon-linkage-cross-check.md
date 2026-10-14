# Jonathan v2 and Motion Lab feature cross-check

Author: Andy Zhang with Codex. Updated: 2026-10-14. Base: `93fed9f`.
Status: experimental analytical integration, requested by the owner.

The user referenced Jonathan's v1 file and requested the newer v2 features in
Motion Lab's Math/2D Physical tabs as a separate linkage design. The supplied
screenshot is the v2 geometry/loading editor. The implementation builds from
the repository's current [original source](../../../../jonathan-xie/experimental-apps/leg-solver/v2-quasi-static.html),
using its [documented equations](../../../../jonathan-xie/experimental-apps/leg-solver/v2-model.md).
Instructions recorded in historical handoffs are source evidence; the current
user request defines this integration's scope.

| Feature | Integrated behavior |
| --- | --- |
| Separate linkage | Jonathan v2 button in both Math/Physical; one shared mounted editor; existing wheel-height and inversion fixtures keep their own inputs/backends |
| Geometry | L2/L3 ratio and unequal lengths; each triplet has one driven value, sliders and swaps |
| Link/drive systems | Independent open a/b guide, c/d hip-to-knee drive, e/f knee-to-wheel drive; six editable pitch radii and all three ratios |
| Poses | Alpha mounting, phi0 assembly phase, extension/compression/current theta2; wheel radius; complete live angles and C/P paths |
| Loads | Signed Fn/Ft or Fy/Fz; one driving convention; beta contact angle; switching preserves the current physical force vector |
| Masses/gravity | m1 at A, m2/m3 at rod midpoints, m5 at B, m6 at C, g and effective compound rim radius; total mass and unused inertias |
| Preloads | Independent Tab0/Tcd0/Tef0 using source slack-side allocation; torque difference and total tension remain distinct |
| Outputs | Signed leg/drive torque, belt spans/tight-side labels, pin reactions, five FBDs and equilibrium/virtual-work residuals |
| Sweeps | Twelve original load plots over theta2, signed dz, beta and alpha; three geometry plots, envelope, curve toggles and collapsed sections |
| Peaks/playback | Original bounded simultaneous theta2/beta search, fixed current alpha/driving loads; attained peak poses and convergence gaps; one master plays at a time |
| Data | Original parameter JSON/CSV; v1/v2 JSON import through either editor or library; full profile library and four analytical sweep tables with units/source hashes |
| Workspace | Shared Math/Physical state, session refresh memory, dark/mobile UI; inactive editor playback pauses; profile reevaluation leaves current controls intact |

## Model boundaries and coordinate cross-check

Jonathan measures theta2 along B→A and theta3 along C→B, CCW from local +u.
Its source equations use `theta3 = phi0 + (180-theta2)*(qab-1)`,
`B = -L2*[cos(theta2),sin(theta2)]`, and `C = B-L3*[cos(theta3),sin(theta3)]`.
The source wheel coupling is `K = 1-qab+qef*(qab-qcd)`. Alpha rotates the local
frame clockwise into global y/right and z/up. Beta locates the prescribed contact
patch P about C, and global gravity is −z. V1's P denotes the wheel centre;
v2's C denotes the wheel centre and P the contact patch. Travel/direction plots
track C relative to extension, with gamma=atan2(horizontal,vertical).

The existing suspension uses a specific guided folding leg, a spring law and
dynamic wheel-height/chassis fixture. Its fold/from-vertical and engine angles,
metres and timestep are different interfaces. No settings are silently converted
between these designs. General ratios, arbitrary loading, holding torque and
ideal span preload do not determine the spring, acceleration, compliance or
contact dynamics needed to extend that Pymunk model.

The new physical-tab model solves quasi-static equilibrium, preserving all
original FBDs and checks. Inertias are reported but unused. A is fixed; masses
do not automatically prescribe contact force. Negative normal input remains an
explicit prescribed load. No unilateral tire contact, no-slip rolling, dynamic
motor rating, spring/damping response, packaging/strength or hardware feasibility
is inferred. Pymunk-native and recorded-Pymunk buttons explain the fixture boundary.
Analytical cycles are parameter playback; sweep records omit t/time. Comparison
overlays use sample indices; existing time-delta checks reject them.

## Source preservation and validation

[The builder](../scripts/build_jon_linkage.py) preserves the three original model
scripts byte for byte and records source/model SHA-256 hashes. It adds an API
inside the browser UI closure plus shell messaging/CSS. The sibling source must
exist and the insertion marker must match, otherwise the build fails explicitly.
Generated pages/assets stay ignored; the original v1/v2 files are unchanged.

Original numerical verifiers, new source/library tests, actual integrated Edge
controls/data/theme/mobile checks, existing Motion Lab integration and actual
app-root launcher lifecycle are recorded in [validation](validation.md).
No canonical robot, GPU or hardware physics validation is claimed.
