# Static analytical plot coverage

Kinefold presents the current builder design in its own interface. The unchanged
V4 analytical core is the reference; the original UI is neither copied nor
embedded. Source anchors below refer to
[v4-pulley.html](../../../jonathan-xie/experimental-apps/vsl-solver/v4/v4-pulley.html).
Charts use the offline Plotly runtime beneath the studio mechanism preview.
The executable 17-entry manifest is `KinefoldEquilibriumData.coverage`.

| Native category | Source chart / series | Original lines |
| --- | --- | --- |
| Suspension & support | `springTorque`: signed hip motor τ₂ vs θ₂ | 45, 546–569 |
| Suspension & support | `springSupport`: Δkg = F_eq/g − total mass; Δ% = 100(F_eq/(mg) − 1), two scales | 45, 546–569 |
| Geometry & kinematics | `anglePlot`: θ₃, θ₅, θ₆, γ_uv, γ_xz vs θ₂ | 45, 510–516 |
| Geometry & kinematics | `angleDzPlot`: the same five series vs signed vertical travel d_z | 714–724 |
| Geometry & kinematics | `dispPlot`: d_u, d_v, d_x, d_z vs θ₂ | 45, 510–516 |
| Loading sweeps: θ₂ | τ_G, τ_S, τ₂, τ₄; three tight-span tensions; five force magnitudes (three plots) | 650, 698–711 |
| Loading sweeps: d_z | The same three plots, preserving θ₂ order through travel reversals | 650, 698–711 |
| Loading sweeps: β | The same three plots at current θ₂, α and other builder inputs | 650, 698–711 |
| Loading sweeps: α | The same three plots at current θ₂, β and other builder inputs | 650, 698–711 |

All tension plots show max(U,L) for ab/cd/ef, including preload. Solid curves
mean upper-active and dashed curves lower-active; hover reports both strands.
Force series are |F₁₂|, |F₁₄|, |F₂₅|, |F₃₂| and |F_w|. Torque signs are retained
in data and indicated by solid positive/dashed negative curves even when the
loading-sweep magnitude option is selected. Suspension plots always stay signed.

Current-pose diagrams include all five source free bodies (2, 3, 4, 5, 6),
individual applied forces/couples and residuals (source 649–667). A separate
finite-idler spring detail shows the horn, tangent, wrap, exit, payout and
reference preload (526–544). The whole mechanism remains in the builder.
Original optimizer/master playback and global-bound metric cards are outside
this plot task; there are no original 3D or heatmap plots to port.

## Frame and scientific meaning

World points and force vectors map source y/z to x/z using x = −source y and
z = source z. Positive axial torque is +y, counterclockwise with +x left and +z
up. Source travel d_y becomes −d_x. γ_uv = atan2(d_u,d_v) and γ_xz =
atan2(d_x,d_z) are travel inclinations, separate from physical joint angles.
They are undefined at zero displacement, and angular wrap jumps break curves.
Support compensation is undefined at zero total weight, zero gravity or zero
vertical Jacobian; singular branches and unavailable poses have gaps, never
invented zero values. Travel charts retain parameter order, and hover recovers
every source root at that travel rather than connecting unrelated branches.

Diagnostic windows never change geometry, current pose or physical stops. Window
clamping takes priority; without it the source domains are θ₂ 90–180° (expanded
90–270°), β 0–90°, α 0–45°. Equal bounds receive display padding. Initial windows
use current physical θ₂ stops, β 0–90° and α 0–30°. Physical working stops and
the current builder pose are marked separately. The overview peak is sampled
over the physical θ₂ range at current α/β; it is not a certified global θ₂×β bound.

Categories and loading axes render lazily. Rows are cached per physical parameter
snapshot and diagnostic windows, so series changes do not rerun equilibrium.
Shared-design updates invalidate all relevant data, including imports while the
Mechanism studio is visible. Plot preferences are local UI state, separate from
portable project-v3 physical parameters and run profiles.

Exports are saved in the app’s exports/ folder, with a relative path shown in
the UI; the browser Downloads folder is not used. JSON export contains all 17 chart datasets, the current portable project,
diagnostic options and source manifest. Selected-axis CSV begins with one
`# ` JSON metadata line (design, ranges and axis), followed by ordinary CSV;
skip that first line in CSV software. Null/undefined data stays empty in CSV.

## Reproduce numerical checks

Run `node verify-equilibrium.cjs` for independent hash-verified original-source
series parity, support gaps, independent domains and multibranch travel.
Run `node verify-equilibrium-diagrams.cjs` for independently transformed world
forces, moments and finite-idler tangent/arc geometry. These verify analytical
presentation, not physical hardware, strength, friction or terrain feasibility.
