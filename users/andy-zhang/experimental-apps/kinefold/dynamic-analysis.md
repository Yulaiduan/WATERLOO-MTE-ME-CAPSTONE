# Native dynamic analysis and comparison

The matched comparison below describes the original prescribed-height bench.
The separate [actual terrain-contact mode](terrain-contact.md) uses two real
Pymunk bodies, frictional collision, a backdrivable wheel and actual world mesh;
its analytical comparison is unavailable. No existing bench is relabelled as contact.

Both dynamic tabs use the same categorized Kinefold presentation and saved
builder mechanism/input profile. They retain the existing floating quarter-model
equations: A translates vertically, horizontal position and pitch are constrained,
and wheel height is prescribed. Pymunk integrates the actual chassis body with
ideal transmission/inertia condensed into its force law. It is not an all-body
linkage or collision/tire-contact simulation. No guide rods are drawn.

## Matched plot categories

| Category | Matching plots in both engine tabs |
| --- | --- |
| Motion & wheel input | requested/applied input; relative chassis heave; world A/C heights; chassis speed; chassis acceleration |
| Angles & kinematics | θ₂/θ₃/θ₅/θ₆; angular rates; angular acceleration; horizontal wheel-centre displacement |
| Forces & actuation | cable tension; signed vertical input reaction; motor command, damping, net actuation and balance-reference torque |
| Energy & numerical checks | kinetic/effective-potential/total energy; cumulative actuation/input work; work–energy residual; sampled chassis horizontal and pitch constraint errors |

The 17-plot manifest lives in `dynamic-analysis.js`. Categories render lazily;
series toggles, exact-sample hover, readable units and a shared playback-time
cursor support inspection. Input/angle/source-work jumps retain before/after
samples. Angular rates and reaction curves break across exact discontinuities:
one-sided samples do not define finite jump speed or force. The balance-reference
torque is `−generalized(q)` at zero rate/input acceleration, not complete dynamic
inverse dynamics. Pin/belt forces are not solved by this reduced dynamic model.
Analytical constraint errors are zero by construction; Pymunk errors come from
sampled actual chassis transforms. Missing diagnostics remain unavailable.

## Compare one captured case

**Run both & compare** captures the complete project once, then runs analytical
and Pymunk sequentially with identical params/config. The shared profile remains
the source of truth; changes mark old results stale and block their comparison.
Backend mechanism hashes, complete parameter objects and complete run configs
must match. View/name changes alone do not change the physical comparison.

Alignment pairs only equal sampled time (within 1e-8 s) and the same explicit
event side. There is no interpolation across jumps or extrapolation beyond
early termination. Matched count, both sample counts, overlap interval and both
termination reasons expose partial common coverage. Overlay and Pymunk-minus-
analytical error plots share a variable selector; statistics are sampled maximum
absolute and RMS errors with units. Comparison JSON includes both complete
captured project snapshots, raw results, matched rows and statistics.

Switching engine tabs retains playback time and before/after side where available.
The preview camera uses one world-frame bound for the entire result, preserving
visible chassis heave and +x left/+z up. It never recentres each pose.

## Moving spatial floor

The square profile translates toward −x (screen right) at the saved study speed.
At world x, its coordinate is
`speed*(time − delay) + x − currentWheelCx`. Its height under the instantaneous
wheel position equals the engine's requested/applied input, including delay,
left/right exact-square states and finite C2-quintic transitions. The applied
curve is solid and the requested sharp square dashed. Very dense browser floor
geometry is explicitly marked sampled, while wheel input remains exact.

Anchoring under C_x is a prescribed wheel-height driver; it does not add horizontal
rolling or collision physics. The grid and chassis remain in the world frame.

## Native desktop Pymunk results playback

**Open desktop Pymunk** captures the current design/profile and launches an actual
Tk desktop window. It computes the existing Pymunk engine once, then plays its
actual chassis frames with ideal linkage reconstruction. The window is explicitly
labelled results playback, with pause, scrub, replay and a moving spatial floor.
It does not embed a web page or claim live collision integration.

Same-origin POST `/api/viewer` accepts only `open` (params, runConfig, optional
display name), `status` or `close`. The fixed app-local script and `.venv` runtime
are the only executable targets. One owned process, bounded request/startup,
token-scoped status and readable `.preview/viewer.log` provide lifecycle/error
feedback. Closing the app server also closes its viewer; no unrelated process
is searched for or terminated. Setup uses the existing Python/Tk environment,
with no new package dependency.

Run `node verify-dynamic-analysis.cjs --real` for actual baseline engine comparison,
event-side/partial-coverage safety and independent Python input-law parity.
Run app `.venv` Python `verify_viewer.py --gui` for actual native lifecycle/control
checks. These validate this experimental presentation, not hardware or terrain.
