# Equal versus unequal links and the next optimization brief

Andy Zhang with Codex, 2026-10-15. Source base `14f53f1`. Status: selected
analytical comparisons and a proposed next study, not a new large optimization
or approved hardware decision. This records the owner's request for benefits,
comparison with similar equal-link designs, and a summary of design requests,
variables and optimization ideas before another sweep.

Open [the offline brief](../design-sweep-brief.html),
[four-page PDF](design-sweep-brief.pdf), [comparison data](equal-link-comparison.json)
and [independent original-model checks](equal-link-comparison-checks.json).
Use [Open Sweep Brief.cmd](../Open%20Sweep%20Brief.cmd). Prior reports and GIFs
stay intact; this does not add controls to Motion Lab.

## What slightly different lengths buy

Unequal links add a geometry adjustment. They do **not** automatically improve
torque, energy efficiency, physical invertibility or suspension compliance.
Let upper `a=L2`, lower `b=L3`, total `S=a+b`, difference `D=a-b` and
`t=q-pi`. At guide ratio r=2 exactly:

```text
x = D cos(t)       z = S sin(t)
Jx = -D sin(t)     Jz = S cos(t)
```

At fixed S, changing D changes lateral movement and fold location while
preserving vertical motion, vertical-load holding torque and useful angular
ROM exactly. The unequal path is an ellipse; equal D=0 gives the vertical line.
This can add sideways motion while keeping a familiar 2:1 guide. It is not free
energy: a horizontal load adds its own Fx Jx generalized torque, and actual
rolling/scrub/contact determines how the lateral motion behaves.

The retained fully guide-spacing-feasible control is equal 190/190 versus
upper 205/175 mm, both S380 and r2. Both have 41.236 Nm peak at 110.3625 N
vertical load. Equal gives 0 mm sideways travel; unequal gives 24.538 mm.
Guide pitch-centre surplus increases from 10 to 25 mm because the upper link
has more room for the same hip/knee pitch radii. These margins are assumptions,
not actual outer hardware clearance. The earlier S370 control 185/185,r2 has
only 5 mm pitch surplus and fails the assumed 10 mm screen; it is retained only
as an analytical control against 200/170,r2.

At other guide ratios, length redistribution changes both horizontal and
vertical kinematics. With fixed S375 mm and guide 15:8, equal 187.5/187.5 gives
31.341 mm sideways travel and 38.361 Nm peak; upper 200/175 gives 49.772 mm and
38.523 Nm. Both meet the assumed 10 mm guide pitch surplus. That is more lateral
movement for about 0.42% more vertical-load peak in this specific comparison.

Other potential benefits are independently adjusting folded wheel-centre
offset D, upper-link space for guides, maximum reach and path curvature. An
actual manufacturing, mass, stiffness or chassis-envelope advantage requires
CAD and component data. Equal links also remain a useful baseline for common
parts and symmetric geometry; those manufacturing benefits are not quantified.

## Published rounded comparisons in similar lateral bands

All rows use alpha=phi0=0, normal start 100 degrees, end solved for 325 mm total
height with cap 175,20+20 mm assumed reserves and 285 mm useful height. Force is
110.3625 N vertical, representing 45 kg shared over four corners, massless
moving links and no spring/inertia. Endpoints/guide ratios differ by design;
lateral targets are bands, not exactly identical paths.

| Lateral target mm | Equal links mm; guide | Upper-long mm; guide | Hip peak equal /upper Nm | Link sum saved mm | Upper peak penalty |
| --- | --- | --- | ---: | ---: | ---: |
| 25 | 185/185;1.9 | 200/170;2 | 38.387 /40.305 | 0 | +5.00% |
| 50 | 190/190;1.8 | 200/175;1.875 | 37.363 /38.523 | 5 | +3.10% |
| 75 | 200/200;1.7 | 205/185;1.75 | 37.093 /37.504 | 10 | +1.11% |
| 100 | 205/205;1.6 | 215/175;1.7 | 35.888 /36.888 | 20 | +2.79% |

The current upper-long examples trade 0-4.9% less combined link length for
1.1-5.0% higher peak torque and slightly less useful angular ROM. The largest
individual link grows by 15/10/5/10 mm respectively. Therefore link sum alone
does not establish smaller packaging or lower mass. This is a comparison of
selected rounded examples, not independent family optima or a causal test of
length mismatch. A fair next search must retain exact equal controls and use
identical constraints/objectives for all orientations.

**Current interpretation:** use equal 190/190,r1.8 as the 50 mm force/travel
baseline. Upper200/175,15:8 is a geometry/guide-packaging alternative, not a
demonstrated force winner. The preceding recommendation to begin CAD with it
was an upper-long example responding to that request; equality should remain
eligible in the next optimization.

The equal 195/195,r1.7 fixed-S control misses 325 mm by just 0.200 mm at the
175-degree cap. Keep its actual 324.800 mm capacity rather than silently
clipping stroke. This tiny numerical rejection does not prove a meaningful
practical advantage for an unequal design; boundary margins and tolerances
must be part of the next comparison.

## Summary of the owner's design and optimization requests

### Current owner choices

- Wheel approximately 200 mm radius /400 mm diameter.
- Approximately325 mm total vertical travel including all buffers. Earlier
  discussion distinguished200 mm minimum and approximately 250 mm preferred
  usable travel; latest searches use325 total, not325 useful.
- Equal or slightly unequal links; either upper or lower may be longer;
  `max(L2,L3)/min(L2,L3)<=1.25`. The guide ratio is a separate variable.
- Preserve Jonathan's variable names and angle conventions. Inherit V1/V2
  equations and compare with Andy's independent 2D model and Pymunk.
- For the current strict path study, alpha=0 and original assembly phase=0.
  No hidden mounting tilt or pulley indexing to obtain the desired path.
- Curved paths with approximately25/50/75/100 mm horizontal movement,
  continuously invertible height through the fold. The fixed 15-degree line,
  bounding-box/R2 method was explicitly cancelled and is not an objective.
- Seek useful force/travel tradeoffs, compact links, average/peak torque,
  effective angular control range, individual torque curves and clear ranking.
- Robot approximately40-45 kg; typical10-11.25 kg per corner under equal
  four-leg sharing. Compare3g/4g total supported-load sensitivity, without
  treating that alone as a validated impact event.
- Subsequently refit springs across the established suspension topologies and
  size one example's motor torque, speed and acceleration. Use the new geometry
  and real mass/duty rather than transferring earlier spring/motor numbers.
- Present work in offline HTML and PDF, key plots/parameters/figures, labelled
  examples/GIFs when useful, and maintain app Markdown/context/revision history.
  Reports remain separate from Motion Lab tooling. Preserve historical
  dual-rope IMPOSSIBLE /rejected status and the established undamped models.

### Current study assumptions, not confirmed hardware requirements

- 20 mm reserved at each end gives285 mm useful. Degree buffers and mm buffers
  must be related through the actual nonlinear geometry, not interchanged.
- Normal start 100-140 degrees, cap 175, full ideal domain100-260 and
  minimum Jz 5 mm/rad are search choices. Screenshot normal bounds were100-165.
- At equal 190/190,r1.8,100-165 supplies only 269.206 mm total. A fixed guide 1.8
  needs approximately229.379 mm per equal link to get 325 mm within 100-165;
  this is a capacity-only estimate, not a matched-sideways optimum. The much
  shorter recent examples rely on extension to almost175 degrees.
- rb60 mm and assumed 10 mm guide pitch-centre surplus come from retained
  studies. Actual tooth counts, pitch, flanges, housings and strengths are open.
- Lateral target bands are +/-2.5 mm with monotone normal horizontal movement.
- Height-RMS corresponds to constant vertical speed without dwell; speed
  comparison 0.25 m/s and robust either-sign |Fx/Fz|<=0.3 are assumptions.
- The pure vertical force screen is massless-link quasi-static mechanics.
  Earlier physical examples use positive moving masses and a different geometry.

## What the next sweep should vary

Use total length and signed imbalance rather than requiring every pair to be
unequal:

```text
S = L2+L3
d = (L2-L3)/S
L2 = S(1+d)/2; L3 = S(1-d)/2
|d| <= 1/9  <=>  max(L2,L3)/min(L2,L3) <= 1.25
```

Equivalent signed length ratio L2/L3 ranges from 0.8 to1.25, **not 0.75 to1.25**.
Include d=0 exactly, plus both signs. Suggested initial study ranges below are
proposals to review/play with, not new accepted design constraints:

| Variable | Proposed initial range/scenarios | Why it matters |
| --- | --- | --- |
| Total length S | 350-600 mm; extend if winners touch bounds | Reach, stroke, torque and size scale |
| Signed imbalance d | -1/9 to+1/9, including 0 and endpoints | Equal /upper-long /lower-long; fold offset and path shape |
| Guide r=ra/rb | 1.2-2.6; later compare realizable rational ratios | Path shape, vertical Jacobian and knee/hip power mapping |
| Normal q start | 100-140 baseline; optional95 sensitivity | Mechanical advantage and available stroke |
| Normal q cap | Separate165/170/175 scenarios | Actual stop/guard tradeoff, rather than silently extending ROM |
| Height /lateral | 325 total; lateral25/50/75/100 bands | Preserve common tasks for fair comparisons |
| Buffers | Start with20+20 mm, then labelled alternatives | Useful control range and endpoint margin |
| Physical stage | Axial stack, actual pulley sizes, mass/inertia, springs and motor gearing | Converts a kinematic candidate into a buildable driven system |

This S/d range implies individual lengths about155.6-333.3 mm. Record those
actual bounds rather than claiming to have independently covered150-400 mm.
If start95 is allowed, expand full inversion to at least95-265 consistently;
do not validate only 100-260. At guide2:1, a90-degree endpoint has Jz0 and fails
the current height-inverse conditioning requirement.

Also choose a nominal ride position and bump/rebound allocation. Total stroke
does not fix static ride height or available compression stroke. For a rigid
wheel on level ground with alpha=0, hip height is R-z_C; chassis depth, tire
deflection and the actual envelope then set body clearance. Keep these inputs
explicit. The20 mm geometric end reserves are not validated impact stopping
distances or automatically spring compression travel.

### Hard constraints before scoring

Require the owner length limit, total height and all reserves, continuous
height inverse over the declared full domain, stated minimum Jz, normal path
direction/no reversal, target lateral band and actual applicable guide/geometry
clearance. Keep angular fold guard and height reserves distinct. Missing axial,
wheel/hub/tire/chassis or outer-pulley dimensions stay unknown; do not fill them
with zero or accept a collision-disabled run as clearance evidence.

For upper-long folds C is inside upper AB; equal folds have C=A. Compact near-
equal coplanar wheel paths overlap the mechanism. A measured axial/forked layout
is necessary before certifying physical inversion. Small |L2-L3| offsets may
help layout but do not clear a 200 mm wheel by themselves.

### Objectives and metrics

Keep separate leaders or a Pareto set (no arbitrary blended weights):

1. Peak direct-hip torque for a common task/load, plus side-load robustness.
2. Time-weighted RMS actuator/motor torque for a common trajectory and dwell.
3. Maximum link length and actual swept/packed envelope, with link sum labelled
   as a proxy. Mass/inertia require geometry and material/component inputs.
4. Useful angular ROM, peak speed and acceleration, with control conditioning.
5. Buffer/stop/clearance tolerance margin and ease of guide realization.

At fixed H, H/peak torque gives the same ordering as minimizing peak torque;
do not weight them twice. For constant vertical force, angle-mean hip holding
torque is Fz H/delta_q. A larger ROM can lower this mean without saving energy.
Ideal work is Fz H=31.4533125 J for the common useful task. True efficiency needs
friction, motor/gear electrical losses, inertia and duty. CV/flatness can help
controller/spring fitting but does not replace peak/RMS/loss metrics.

For a common commanded height trajectory, with SI Jacobians:

```text
qdot = zdot/Jz
qddot = zddot/Jz - (dJz/dq)*zdot^2/Jz^3
tau_hold = -(Fx Jx+Fz Jz)  # massless quasi-static limit only
tau_knee = -tau_hip/r;  knee_speed = -r*hip_speed
```

Half knee torque applies only at r2. Gearbox mapping is separate from the guide.
Dynamic motor sizing must then add body/link inertia, actual spring force law,
friction and transmission losses. Proposed common lift-time sensitivity is
0.5/1/2 s, labelled assumptions; do not equate3g/4g static loading with this
motion or a suspension impact. Absolute compliance also requires stable
effective spring/controller/geometric stiffness and contact conditions.
Later spring optimization should vary topology, installed preload, spring
rate and attachment/drum/bellcrank geometry subject to real stroke, package
and force limits. Motor reduction is another variable, with both torque and
speed/acceleration limits checked rather than rewarding reduction alone.

### Proposed search and validation sequence

Broad coarse S/d/r/window sweep with exact equal controls in every scenario;
separate upper/equal/lower families and lateral bins. Retain non-dominated
force/size/ROM/speed/margin tradeoffs, refine finalists continuously and round
guide hardware. Repeat checks at rounded values and perturbed tolerances,
report active bounds and rejected cases, then compare originalV2/Andy2D and
actual positive-mass constrained Pymunk geometry. Finally add measured physical
packaging/mass, refit spring topologies and evaluate common dynamic duty before
selecting motor/spring parameters. No new large grid is run by this brief.

## Copyable next-sweep request

> Compare equal, upper-long and lower-long coupled legs using Jonathan's
> conventions, alpha=phi0=0, R200 mm, max/min length<=1.25 and325 mm total
> vertical travel including explicitly labelled20+20 mm reserves. Parameterize
> S350-600 mm and d in[-1/9,+1/9], include equal controls, vary guide1.2-2.6 and
> start 100-140, and compare normal caps165/170/175 separately. Optionally add
> start95 while expanding the full inversion domain. Match25/50/75/100 mm
> lateral bands without R2/straight-line ranking. Keep force, RMS duty, size,
> control ROM/speed/acceleration and tolerance margins as separate objectives.
> Report Pareto choices, active bounds, infeasible cases and fixed-size/guide
> controls. Preserve unknown axial hardware dimensions rather than certifying
> collision-free inversion. Validate finalist equations against originalV2,
> Andy2D and actual Pymunk; only then refit springs/motors with declared mass,
> gearing and common lift duty. Deliver offline HTML/PDF, figures and app MD
> context/revision updates, preserving prior reports and IMPOSSIBLE decisions.

## Reproduction and actual verification

From this app with the existing Python 3.13/Node 22 environment:

```sh
.venv/Scripts/python.exe scripts/compare_link_lengths.py
node scripts/verify_sweep_brief.cjs --math-only
.venv/Scripts/python.exe scripts/build_sweep_brief.py
node scripts/verify_sweep_brief.cjs
```

13 retained analytical cases include the eight published examples, three
height-feasible fixed-S/r controls, and two additional r2 controls meeting the
assumed 10 mm guide surplus. The fourth fixed-S control's0.200 mm capacity
failure remains explicit. 32 retained metric comparisons reproduce exactly;
501 independent r2 identity samples agree within 5.69e-14 mm/rad-unit quantities.
4,838 independent originalV2/Andy2D scalar checks pass, maximum 1.71e-13 mm/Nm.
Independent read-only review confirms the selected tradeoffs, parameterization
and next-sweep interpretation. Rendering/printing/hash/link checks are recorded
in [validation](validation.md). No new Pymunk or loaded/spring/impact/hardware
test is claimed for this comparison; prior evidence retains its original scope.
