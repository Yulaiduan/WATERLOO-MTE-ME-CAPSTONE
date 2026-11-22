# S0075 pulley-radius quick check — 2026-11-22

Source: saved S0075 in springs/v6-spring-solutions.xlsx, evaluated read-only with
vsl-solver/v7/spring_lab.py. Use the record geometry, not the older duplicate
spring fields inside parameters. Saved alpha=0 deg and working theta2=120–180 deg.
Both existing Swift springs, r_h=50 mm, nu=0 and payload swap masks remain fixed.
All original workbooks and solver files remain unchanged.

## Results (peak absolute residual hip torque, N m)

| Case | Su mm | Sv mm | unloaded | +70 kg |
|---|---:|---:|---:|---:|
| Original rs12.7 |12.601|75.4|0.0631|0.6817|
| rs38.1; only Su/Sv changed |70.886|126.2|4.0884|9.5300|
| rs38.1; also reset preloads (diagnostic) |78.431|126.2|1.5502|1.5502|

Original preload forces are 640.264 and 1365.461 N at theta2=90 deg. Diagnostic
forces are 581.520 and 1189.855 N. Spring rates remain21.89085 and48.15988 N/mm.
Normal working stroke remains about49.9–50.0 mm. All three variants pass the
backend's rated spring envelopes and unloaded -50 deg inversion check, including
its Sv-r_h>=2rs clearance condition. The larger radius forces Sv>=126.2 mm, 50.8 mm
above the original. Su also increases materially; packaging is an important cost.
The original Su bound +/-30 mm gives much worse17.20/37.94 Nm; moving beyond
that original bound is necessary for the reported useful fit.

The fit minimizes the worst absolute residual over both payload cases. Primary
fit uses12 deterministic starting points with Sv126.2–400 and Su+/-150 mm, fixed
preloads; preload diagnostic uses4 starts and the same position bounds. This is
a bounded quick search, not a proof of the global optimum. Selection used401
uniform angles; validation used6001 uniform angles plus exact profile critical
points. The initial attempt failed because the backend adds variable critical
points to the grid; optimization now selects a fixed grid from that profile.

This comparison holds the original spring rates and mass/angle assumptions.
Preload adjustment is explicitly a diagnostic beyond the requested Su/Sv-only
change. It shows that much of the error is installation bias rather than an
unmanageable increase in nonlinearity. Static spring-envelope checks do not
certify rope fatigue, sheave bearings, guides or physical collision geometry.
A1.5-inch radius is a cable-bending design input, not a verified4kN cable WLL.

Reproduce: python -B scripts/pulley_radius_s0075.py from springs root with numpy
and scipy; then python -B scripts/plot_pulley_radius_s0075.py (matplotlib). Numeric evidence is results.json; residual-curves.csv and the rendered
PNG/SVG compare the three useful variants. No saved S0075 overwrite, commit or
remote publication is part of this task.
