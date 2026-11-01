# Fixed chassis spring mounting

Andy Zhang / Codex, 2026-11-01. Experimental model convention `chassis-fixed-v1`.
Owner requested that α rotate the leg without rotating the spring assembly and
acknowledged that new gravity-compensation constants may be required.

## Coordinates and force law

The idler and horizontal spring body are fixed relative to hip A on the chassis.
The horn pin remains rigidly phased to the upper link. In Kinefold coordinates,
`S−A=[−Su,0,Sv]` mm, independent of α. With θ and ν in degrees,
`D−A=[−rh*cos(θ+ν−α),0,rh*sin(θ+ν−α)]` mm. Thus the fixed mount stays put while
the horn and leg move. ν remains link-relative; α is leg mounting pitch.

For the retained source equations, the adapter uses
`Su_ref=cos(α)*Su−sin(α)*Sv` and
`Sv_ref=sin(α)*Su+cos(α)*Sv`.
The original source force/geometry/FBD equations and their hashes are unchanged.
Spring-only world drawing instead uses α=0, raw chassis Su/Sv and ν−α. Both
representations give the same cable-length changes, force, torque and energy.
Routes that require rotating the fixed horizontal outlet are explicitly invalid.

The spring remains `Fs=max(0,p0+k*(c(θ)−c(90°)))`, with p0 referenced to the
stored leg coordinate **θ2=90°**, not absolute world horn angle90°. Work is
`ΔUs=integral(Fs dc)/1000` J for cable length in mm, and
`τs=−dUs/dθ_rad` Nm. Changing α changes the relative horn/mount geometry and
therefore spring work. No cos(α) shortcut or automatic preload/stiffness/geometry
retuning is applied. Use Suspension Lock/Solve when a new compensation fit is wanted.

At α0° the physical reference is unchanged. For tilted fits, free chassis
geometry uses a bounded multistart search with bounds fixed from the captured
input, while preserving exact locks. Fixed-geometry coefficient fits retain the
V4 fitter. The result is densely checked at6,501poses; it is not a global optimum.

## Saved designs and captures

Raw saved parameters are preserved. Current calculations use this convention;
tilted designs show a concise fixed-mount/no-retune notice. The seven current
saved designs and working copy were validated read-only without changing them.
An older tilted design with an impossible fixed-outlet route is rejected
explicitly rather than silently rotating its mount or changing its constants.

New engine scope, frames, design hashes and comparison keys carry the mounting
convention. Old captures without the token are `legacy-leg-v1`: playback retains
their original leg-mounted spring and displays a legacy/rerun notice. Mixed
conventions cannot be compared as the same model. Source-hashed historical
reports remain evidence for their recorded version, not new fixed-mount results.

## Checks and presentation

Independent JavaScript/Python checks cover fixed mount/housing, moving horn,
conservative work, finite masses, exact locks and legacy captures atα0/20/45°.
Cross-language spring-force difference is at most3.41e−13N in the retained test;
finite-difference work/torque error is at most1.62e−8Nm. Short actual analytical
and Pymunk α20° runs check the new pipeline, not hardware or impact fidelity.

Most explanatory UI prose now uses native click/keyboard **i** disclosures.
Numbers, labels, actions, errors, run warnings and legacy model notices remain
visible. Detailed equations/tables and Conventions stay available below. This
changes presentation only; opening help never edits a design or runs a solver.
