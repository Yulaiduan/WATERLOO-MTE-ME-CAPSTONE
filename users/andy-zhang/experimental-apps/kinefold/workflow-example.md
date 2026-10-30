# A small comparison workflow

Andy Zhang with Codex, 2026-10-30. Three worked choices, not a catalogue-wide
search or verified hardware selection. The owner requested a simple example and
limited saved data after asking for terrain animations and candidate comparisons.

## The workflow

1. Save one mechanism: geometry, masses, alpha, spring and physical travel stops.
2. Pick a few independent motor/gearbox presets.
3. Use the same jump/drop/clearance and terrain inputs for every choice.
4. Run analytical and Pymunk from the same captured settings.
5. Compare jump height, first-arrest landing outcome and terrain tracking error.
6. Replay one useful example; keep its settings and a compact results summary.

The existing app tabs provide the mechanism, preset, automatic-comparison and
paired-replay workflow. This bounded CLI example illustrates those steps without
adding another UI or writing the live design library. Tab06 can use the current
saved mechanism explicitly; its default V4.5 profile has different chassis mass.
The example runner's files are not automatically installed as a tab06 job.

## One setup, three choices

The setup continues the previous study:45kg chassis, 1 kg each rod and 0.5 kg wheel
per corner, 55 kg gross equivalent, alpha 20 deg, full 100–165 deg hip travel,
2 m jump/drop targets, 50 mm minimum underside clearance and a 50 mm underside offset.
The original V4.5 profile remains 35 kg chassis /45 kg gross.

Constant cogging is lumped into shaft Coulomb 0.05 N m; shaft viscous coefficient
is 0.0008 N m s/rad. Assumed gear-input inertia is 0.0001 kg m², motor inertia uses
the source sheet's nominal geometry estimate, and no-load speed is assumed
6000 rpm. The existing finite-link model, approximate V4 gravity support and
noiseless finite-gain controller are unchanged. Gear ratio, listed torque/speed
caps and forward efficiency come from the selected catalogue entry; reverse
efficiency 0.9 and 5 kW/5 kJ power/regen limits are assumptions. Listed efficiency
plus explicit drag may overlap; neither is a measured combined loss map.

| Choice | Motor | Gearbox | Reflected motor + gear J (kg m²) |
| --- | --- | --- | ---: |
|A |Flipsky 6384 170KV, 9 N m peak |AB90-G10-D19,10:1 |0.03453 |
|B |Flipsky 80100 130KV, 17 N m peak |AB90-G10-D19,10:1 |0.09250 |
|C |Flipsky 80100 130KV, 17 N m peak |AEP90-G20-D19,20:1 |0.37001 |

The manufacturer pages checked on 2026-10-30 agree with the sheet's selected
[6384 peak rating](https://flipsky.net/products/flipsky-bldc-belt-motor-battle-hardened-6384-140kv-170kv-190kv-4000w-for-electric-skateboard),
[80100 peak rating](https://flipsky.net/products/brushless-dc-motor-80100-130kv-7000w-for-electric-bike-electric-skateboard-go-cart),
[AB90 10:1 limits](https://www.omc-stepperonline.com/ab-series-90mm-10-1-helical-planetary-gearbox-backlash-5arcmin-for-servo-motors-ip65-ab90-g10-d19)
and [AEP90 20:1 limits](https://www.omc-stepperonline.com/aep-series-90mm-20-1-helical-planetary-gearbox-backlash-7arcmin-for-servo-motors-ip65-aep90-g20-d19).
AB90 is listed 100 N m nominal /300 N m momentary; AEP90 is 75/250 N m. Both list6000 rpm
maximum input and 19 mm input bores. The motors have different shaft sizes, so
these numerical pairings need adapters/mounting review. The80100 page lists a
mechanical maximum speed; that does not supply the missing torque-speed curve.
No price/availability or broad product search was performed.

## Actual example results

Exactly 18 executions cover 3 choices × 3 cases × 2 engines. Both engines use identical
captured inputs and finite-link dynamics. dt 0.25 ms, output 200 Hz. Terrain is
15 mm RMS seeded roughness,600 mm nominal period,25% variation, seed 481,
400 mm/s; the common 1.5–4.5 s evaluation contains 601 samples.

| Choice | Jump COM rise A / P (m) |2 m landing |Terrain RMS A / P (mm) |
| --- | ---: | --- | ---: |
|A |0.444 /0.443 |Both compression-bottom-out before arrest |1.676 /1.676 |
|B |0.789 /0.786 |Both arrest; minimum clearance 545 /556 mm |1.679 /1.679 |
|C |0.902 /0.898 |Both arrest; minimum clearance 667 /669 mm |1.698 /1.698 |

C leads jumping and first-arrest clearance **among these three choices**.
None meets the 2 m jump target. Terrain tracking is a practical tie within the
editable 0.1 mm comparison band; the full spread is 0.0224 mm and saturation is 0.
That band is an engineering comparison choice, not a statistical confidence
interval. Rankings use the lower engine value for jump/clearance and higher
engine RMS. Failed, incomplete or numerically unresolved pairs cannot win.

Landing includes substantial rigid-impact energy removal. Greater clearance
does not establish acceptable tire/gear shock loads or guaranteed hardware
survival. Continuous motor ratings, thermal duty, actual speed/torque maps,
measured inertia/drag and mounting compatibility remain unverified. The same
controller gains are used for each choice; this is heave tracking, not full-body
roll/pitch stability or individually optimized control.

## Saved terrain animations and storage

Three previous actual N20 illustrative runs are exported: 50 mm smooth bumps,
seeded roughness and roughness plus 5% grade. A fourth animation shows the
worked B combination on the seeded terrain. Each GIF places analytical/native
Pymunk side by side with one clock/camera, actual moving ground, wheel/pulley
indices, belts and spring geometry. Coordinates remain +x left/+z up.

Each contains 91 selected actual frames, 4.5 physical seconds at 20 fps and a labelled
0.5 s final reading pause, 5 s total playback. No trajectory interpolation or
physics rerun occurs during export. The loop resets the saved replay rather
than pretending the random/graded terrain is a seamless periodic state.
Package sizes are schematic; physical link/wheel geometry is scaled uniformly.

Only the four GIFs, PNG posters and small playback manifests remain from media
export; temporary frame/input caches are removed. The comparison retains a
96 KB summary with exact requests, a CSV/settings file and raw rows/frames for
one worked combination only. Its single compressed data archive is 3.13 MB;
there is no exhaustive catalogue result dump. Artifacts remain in ignored app
folders and are attached natively in Andy's Codex Studies in Notion.

## Reproduce the small example

```text
python workflow_example.py --write-config .preview/my-example-settings.json
python workflow_example.py --config .preview/my-example-settings.json --output .preview/my-new-example
python verify_workflow_example.py
node verify-terrain-animation.cjs
```

Use the app's physics environment for the example. The fixed candidate list is
bounded to three; changing settings requires a new output folder. Optional GIF
export uses `encode_terrain_animation.py` with the two captured terrain JSONs
and an app-local output prefix. It requires installed Node.js, Sharp and Python
Pillow; use `--sharp-module` or Node's module resolution for Sharp. No runtime
packages are downloaded by the exporter. `--help` lists the exact CLI options.

Six focused comparison tests and 15 clock/snapshot/selection assertions pass;
all 9 actual pairs, source fingerprints and six retained worked captures were
checked. GIF dimensions/count/duration/loop, posters and cache cleanup were
verified. No live browser pointer review, new UI, physics-law change or live
profile write was performed. Restart the app using
[Start Kinefold.cmd](Start%20Kinefold.cmd) at 4191.
