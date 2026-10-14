# Compact labelled design GIFs

Andy Zhang with Codex, 2026-10-14. Source report `12e227c`.
These are curated illustrations rendered by Motion Lab's actual example
renderer, not raw simulation runs. Each loops 48 frames at 600x720 pixels over
an illustrative 4.8-second sinusoidal theta2 cycle. Playback is ideal kinematics,
without springs, motor dynamics, contact or collision solving.

| Example | Working stroke | Full ideal inversion |
| --- | --- | --- |
| 01: equal 350 mm, 7:4 | [GIF](simple-guide-working.gif) | [GIF](simple-guide-inversion.gif) |
| 02: equal 450 mm, 1.7925 | [GIF](longer-links-working.gif) | [GIF](longer-links-inversion.gif) |
| 03: 275/250 mm, 2:1, fixed phase -25 deg | [GIF](near-equal-indexed-working.gif) | [GIF](near-equal-indexed-inversion.gif) |
| 04: equal 250 mm, 2:1, fixed phase -25 deg | [GIF](exact-line-indexed-working.gif) | [GIF](exact-line-indexed-inversion.gif) |
| 05: screenshot equal 250 mm, 5:3 | [GIF](screenshot-reference-working.gif) | [GIF](screenshot-reference-inversion.gif) |

All examples have alpha=0 and wheel radius 200 mm. Phase alternatives are
explicitly labelled; no pulley is reindexed during a cycle. Full inversion
passes through projected wheel/hip overlap. Red outlines and the assumed 220 mm
wheel-centre exclusion mark that unresolved clearance; this is not a ground flip
or a hardware demonstration. A/C labels merge only when close on screen; a
literal A=C label is reserved for coincident centres.

[Manifest](manifest.json) records dimensions, source hashes, GIF hashes and sizes.
The [study record](../../../docs/design-examples.md) explains numerical/browsing
checks and reproduction. Raw PNG frame folders stay ignored in artifacts/.
