# Link length, usable lift and torque sweep

Author: Andy Zhang with Codex. Date: 2026-10-12. Status: member analytical tool,
not a selected or hardware-validated design. Source: user's request to size links
from wheel dimensions, lift and configurable extension/compression reserves.

Open [Motion Lab's calculator](http://127.0.0.1:4186/?tab=studies&study=ratio), or
the [standalone page](http://127.0.0.1:4186/force-plots/). Restart with the app-local
**Start Motion Lab.cmd**. The original constant-torque force calculator remains
below the sizing study; its inputs/data/math are separate.

## Inputs and buffer meanings

The user confirmed on 2026-10-12 that the initial case is 200 mm **radius** and
200 mm usable lift. Diameter therefore starts at 400 mm. Both inputs
are editable and synchronized. Selecting diameter 200 mm produces radius and
nominal lift 100 mm. Nominal usable lift is radius; uncheck it to enter custom
ROM in mm or degrees. The tool shows diameter and radius explicitly.

Each link has length L. The displayed angle theta is measured upward from the
horizontal through the wheel centre toward the knee: theta=0 is folded flat,
theta=90° is upright. It decreases during upward wheel lift. Diagrams draw a
horizontal reference and upward angle arc at the wheel centre; table/cards and
plot hovers use the same convention. Height is h=2L sin(theta), and upward wheel
lift is h(start)−h(end). The retained internal fold coordinate q=90°−theta runs
from downward vertical; existing q fields in CSV/config metrics remain compatible.

- Start buffer is a **minimum** travel reserve from full extension. In mm it is
  2L−h(start); in degrees it is 90°−theta(start). This reserves geometry for preload;
  it does not calculate coil extension, stiffness, force or preload energy.
- End buffer is a **minimum** reserve from full compression. In mm it is h(end);
  in degrees it is theta(end). It is not itself the ground gap.
- Chassis depth is the underside's distance below the hip. Flat-ground gap is
  h(end)+wheel radius−chassis depth. Minimum air gap provides an independent
  constraint; the stricter of the end buffer and this clearance bound applies.
- A sweep can choose extra unused travel on either side. The selected readout
  shows actual reserves and actual gap, not only the specified minima.

Defaults other than the starting radius/lift are editable demo assumptions:
20 mm start/end reserves, 200 mm chassis depth, 20 mm air gap, 100 N net vertical
load per leg, L=100–600 mm in 5 mm increments, start placements every 1°.
These are not confirmed CAMEL dimensions, spring parameters or motor ratings.

## Conversions and enumeration

For a reference link length, start-mm converts to acos(1−buffer/(2L));
end-mm converts to asin(buffer/(2L)). Custom ROM-mm converts to
acos((h(start)−ROM)/(2L))−q(start), using the earliest allowed start pose at the
reference length. Inverse conversions evaluate the same cosine geometry.
Unit changes preserve geometry **at that reference link length**; the selected
unit is then held fixed for other sweep lengths. Changing L updates equivalents,
and Inspect reference link finds that length's best allowed window. The selected
candidate also reports its actual angular ROM and mm lift. Equal numeric degree
reserves do not correspond to equal height reserves near both endpoints.

For each sampled L, determine qMin from the start reserve and qMax from the
stricter end/clearance bound. Sweep start placements within that interval, solve
the end pose for the exact requested ROM, and reject impossible candidates.
Include both limiting start placements even when they fall between angle-grid
points, and include the maximum link endpoint even off the length grid. Limit
searches to 150,000 possible windows and reject invalid/nonfinite inputs.
Neither buffer travel nor surplus travel enters the usable-stroke statistics.

## Torque and objectives

Constant net vertical load F gives direct hip-actuator magnitude
tauHip=2FL cos(theta)=2FL sin(q), with L in metres. Relative-knee motion is twice
the hip link angle, so tauKnee=FL cos(theta)=tauHip/2. The 2:1 guide itself does
not halve the direct hip-actuator torque: work conservation gives
tauHip*dtheta=tauKnee*2*dtheta. The fixed guide pulley has its own reaction
torque; it is not the generalized actuator input. Additional motor gearing
would need a separate declared ratio/efficiency. This agrees with the existing linkage vertical Jacobian and
the [Jacobian-transpose / virtual-work force mapping in Modern Robotics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-2-statics-of-open-chains/).
No drivetrain reduction or efficiency is applied. F excludes distributed link
weight and spring assistance unless the user incorporates them into a constant
net-load approximation. Dynamic or angle-dependent residual motor torque is not
predicted here.

For a=qStart, b=qEnd and K=2FL (or FL for knee):

```text
peak = K sin(b); minimum = K sin(a)
uniform-angle mean = K (cos(a)−cos(b))/(b−a)
uniform-angle second moment = K² [1/2 − (sin(2b)−sin(2a))/(4(b−a))]
uniform-travel mean = K [(b−a)/2 − (sin(2b)−sin(2a))/4]/(cos(a)−cos(b))
uniform-travel second moment = K² [P(b)−P(a)]/(cos(a)−cos(b))
P(q) = −cos(q) + cos(q)³/3
RMS = sqrt(second moment)
CV = sqrt(second moment − mean²)/mean
```

These are exact integrals over the window, not averages of chart points.
Uniform-travel weighting corresponds to constant vertical speed; uniform-angle
weighting corresponds to constant fold speed. They are only time averages under
those specific motion assumptions. Peak does not depend on averaging choice.

Rank by lowest peak, lowest mean, lowest CV for torque flatness, or highest
usable lift / RMS torque. Winner cards show all four objectives for the same
feasible population. The length chart
shows the selected objective's best angle window at each feasible length; the
tradeoff chart compares its peak and CV. The table shows the best 30 windows,
and CSV contains all feasible windows. Click a row, card or plotted length to
inspect geometry/torque. Stale results are dimmed and export is disabled until
Run. JSON carries the versioned configuration and selected metrics and loads
through the calculator's own control; it is not a solver profile/run.

## Individual curves and travel-versus-torque score

The comparison plot draws the actual torque-versus-usable-lift curve of each
profile, rather than connecting aggregate statistics. By default it shows the
best window at every feasible link length (97 at the starting settings).
Choose the top 30 ranked windows or distinct objective winners for a smaller
comparison. The selected profile is highlighted and always included; clicking
a curve selects its geometry. Above 300 profiles, the length view explicitly
discloses 300 evenly spaced samples, plus the selection if needed, for rendering
performance. Hover values and the separate selected curve use theta from the
wheel-centre horizontal. Changing comparison view does not invalidate the sweep.

The additional score is `liftPerRms = usable_lift_mm / RMS_torque_Nm`, with
mm/(N m) units; higher is better for this dimensionful travel/torque comparison.
Compare the same load, actuator coordinate and motion weighting. At fixed
usable lift it is exactly equivalent to minimizing RMS torque. It does not
measure transmission or electrical energy efficiency, nor penalize motor speed.
The selected readout also shows actuator angular ROM and ideal work
`workJ = F * usable_lift_mm / 1000`. Relative-knee motion is doubled while its
torque is halved, so both actuator locations do the same work.

Mean describes typical demand under the selected weighting. Peak is the
largest instantaneous torque over the usable window; lower peak minimizes the
required maximum output in this static screen. RMS weights high torque more
strongly and is a better copper-heating proxy than mean for the same motor and
gearing when its time weighting is appropriate: current is proportional to
motor torque and winding losses scale as current squared. See
[maxon's motor heating explanation](https://support.maxongroup.com/hc/en-us/articles/360004427413-On-the-heating-of-motors-in-hand-held-tools).
The actual trajectory, duty cycle, speed losses, motor limits and spring loads
are still needed for thermal sizing. CV measures relative variation only.

Rank 1 is the best of all feasible sampled windows for the selected score:
lowest peak, lowest selected-weight mean, lowest CV, or highest lift/RMS.
Ties use lower peak, then shorter link, then smaller internal starting q.
With the starting mm reserves/clearance, `2L >= 20 + 200 + 20 = 240 mm`, so
the minimum feasible link is 120 mm. At each length the lowest-peak window uses
the earliest allowed start, leaving `hEnd=2L-20-200`. Its peak is
`2F * sqrt(L^2-(hEnd/2)^2)` with all lengths in metres; this increases with L
under those fixed mm settings. Thus 120 mm is the sampled minimum-peak winner.
Changing reserves, clearance, angular ROM or load assumptions can change this
argument; it does not select hardware or a dynamic optimum.

CSV appends named lift/RMS, work and actuator-ROM fields; prior q/theta and
torque columns remain present. Config JSON retains v1 and unchanged buffer/ROM
semantics; old configurations load and recalculate new metrics. The new `lift`
ranking value requires this version of the calculator.

## Initial sampled result and limits

At the initial demo settings and uniform-travel hip torque, 2,586 windows across
97 lengths are feasible. Both peak and mean objectives pick 120 mm links,
theta=66.4435°→4.7802°, 200 mm lift, 20 mm actual reserves and 20 mm end ground gap.
Mean torque is 19.5773 N m; peak 23.9165 N m; RMS 19.9666 N m; CV 20.0431%.
Flatness chooses the 600 mm search boundary, q=79.4360°–89.0450°; mean 119.2573,
peak 119.9833 N m and CV 0.4990%. It uses a much larger actual start reserve.
This demonstrates the magnitude/flatness tradeoff, not a recommended hardware
length. Expand/refine the search when a winner lies at a length boundary.
Lift/RMS is approximately 10.0167 mm/(N m) at 120 mm with hip torque; switching
to knee torque doubles the numerical score without improving energy efficiency.
Every 200 mm / 100 N case does the same ideal 20 J lifting work.

No measured spring law, link weight, acceleration, impacts, strength, motor
speed, tire deformation, slope or 3D collision is included. Full extension is
a singular kinematic pose; zero buffer allows it mathematically but does not
establish controllability. Clearance assumes level chassis and grounded wheel,
and does not validate obstacles, the rejected dual-rope design, or self-righting.
No canonical robot model is required for this isolated member workspace.

## Verification

`npm test` adds seven checks: existing Jacobian and independent height derivative;
work conservation and knee scaling; midpoint quadrature for both means/RMS/CV;
unit round trips; lift/buffer/air-gap constraints; exact boundary enumeration;
ranking/tradeoff; invalid/infeasible searches. `node scripts/verify_link_sweep.cjs`
checks actual browser controls, selection, JSON/CSV, memory, local-only assets,
Plotly zoom/theme and 360 px layout. Existing force-calculator verification is
retained. Current results and launcher lifecycle are recorded in validation.
