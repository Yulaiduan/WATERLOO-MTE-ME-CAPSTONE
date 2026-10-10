# Terrain Workbench validation

Prepared October 2, 2026. Numerical integration checks, production build and targeted production-browser review completed at `http://127.0.0.1:4175/workbench/`.

Required checks: run the meaningful engine/terrain tests together with existing atlas tests; build both production HTML entries; load `/workbench/` from production preview; inspect readable plots, case controls, worker results, graph selection and exports; review compact viewport behavior. Record actual outcomes here after checks complete.

`npm test` passes **25/25** (exit 0): 11 atlas model tests and 14 new workbench checks. A first run caught a JavaScript exponentiation/unary syntax error in the new analytical test; the engine worker corrected it and the complete suite then passed.

The workbench tests cover specified sine RMS/wavelength and layer separation; seeded master-realization cropping; accumulating Class 3 grade cycles; changed terrain values retaining source preset values while becoming assumptions; source-scale USGS import with unknown fine roughness; CSV units/invalid rows; analytic linkage derivative and virtual-work power; preloaded static equilibrium in all control modes; actuator limits changing forward dynamics; smooth-input timestep refinement; explicit travel-failure location; independent harmonic two-mass response; invalid/nonfinite inputs; and zero tire force across a geometric contact gap.

The final post-export-repair `npm test` passes 25/25. Root's last build after the graph-layout CSS fix also passes, exit 0, with Vite 7.3.6 and 19 modules. Output includes `dist/index.html`, `dist/workbench/index.html`, a local simulation worker (12.77 kB), a local MapLibre worker and both entry bundles. Workbench JavaScript is 182.50 kB before gzip (57.88 kB gzip); workbench CSS is 13.81 kB (3.68 kB gzip). This verifies the multi-entry build; a successful bundle does not alone verify browser interactions.

`npm audit --audit-level=high` passes, exit 0, reporting zero vulnerabilities in the installed dependency set at validation time.

Root's development-browser review observed a completed default 100 m run: ideal peak/RMS torque **26.013/8.629 N·m**, candidate achieved peak/RMS **11.827/7.358 N·m**. The generic continuous assumption is 4 N·m, so route completion coexists with continuous-load exceedance. Completion means the numerical run reached route end inside travel bounds; it does not approve the motor or hardware. The UI separately shows overload/saturation and unknown electrical/thermal/structural conditions.

The UI worker ran a VM regression for saved-result inputs surviving cancellation and errors and reported a pass. Root additionally verified cancellation in production: cancelling a 1 km request retained the prior 100 m run and its original input snapshot, with stale-state labeling. Run JSON export retained input length 100 m and completed distance 100 m.

Stable production-browser review observed Class 3 grade-cycle counts of 1 at 100 m and 10 at 1 km; the observed USGS line and a local-file import both retained 1,001 samples, 118.39 m net elevation change and unknown fine roughness. The local file chooser and export payload preview worked. Browser review identified a round-trip export bug: a no-layer measured profile incorrectly serialized zero fine columns, turning unknown fine roughness into zero on reimport. The engine now omits unresolved component columns; the measured-import test verifies unknown roughness survives CSV reimport. Metadata JSON retains the full source context.

At a compact viewport, client/scroll widths were 360/360 px and workbench charts used a 314 px viewBox matching their 314 px width, with unchanged font sizing and no horizontal overflow. Root selected the actuator graph node and verified its inputs/outputs panel. Console errors were absent during the completed run. The default case showed envelope saturation 6.748 s and separate response-limited time 85.544 s, with continuous-overload flags visible.

Actual production screenshots: [terrain workspace](../../evidence/workbench-ui/workbench-terrain.jpg), [calculation graph](../../evidence/workbench-ui/workbench-graph.jpg). Browser export review verified the measured CSV now has two core columns and metadata roughness is null. Serialized content and metadata are verified; **native blob download completion remains unverified** because the browser event wait timed out after 7 seconds. Do not infer saved-file completion from the button action.

Final graph layout review confirmed all nodes fit: the 1,199 px content viewport contains the 1,070 px canvas, with the node input/output contract beneath. The graph screenshot above was recaptured after this fix.

This is a targeted review, not a complete accessibility audit or exhaustive browser matrix.

These are software and reduced-model checks. They do not validate natural biome distributions, wheel contact on real obstacles, transmission reactions, manufacturer hardware, electrical/thermal performance or a physical prototype.
