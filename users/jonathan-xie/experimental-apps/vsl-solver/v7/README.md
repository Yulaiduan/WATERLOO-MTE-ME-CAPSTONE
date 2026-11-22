# VSL Solver V7 — power-limited fall recovery

V6 is preserved separately. Start Open VSL Solver v7.cmd; the isolated helper
serves http://127.0.0.1:8770/v7/v7-springlab.html. V7 configs retain DP9–12 with
DP9 loaded at startup. V7 now uses springs/v7-spring-solutions.xlsx separately from V6. Startup does
not create or replace spring solutions.

The fall controller uses positive resisting magnitude T=min(Tmax,P/omega2) and
signed applied hip torque tau2=-T. A backward numerical energy integration solves
K'=tauG+tauS-T with K(theta2c)=0. Monotone shooting selects the minimum P reaching
the inherited touchdown energy at theta2e. Angular effective inertia H includes
rod translation/rotation when component masses are enabled. Existing omit and
transfer mass modes remain active. Contact lift and dead centres still reject
trajectories. Positive impact energy is required; h=0 is not an impact catch.
At first rest the capped resistance switches to the existing static holding law.

Motor and power supply are selected independently in a persistent input card
immediately above Fall Recovery. The card remains visible when the fall plots
are collapsed; Motor KV configs and Power supply configs expand independently. Motor
KV_LL profiles retain comments and optional KV_LN/Kt overrides. Supply profiles
store comment, informational bus voltage, switching kHz, Vmax_LN, mechanical
power ceiling, overheat duration, phase-peak current and continuous current.
Explicit library Save buttons persist motor-configs.json and
power-supply-configs.json through the local helper. Existing motor profiles are
preserved; their legacy stored freeSpeedRpm fields are no longer used by the new
supply-based UI. No configuration or shared spring workbook is rewritten.

KV_LN=sqrt(3)*KV_LL; Kt=1.5*60/(2*pi*KV_LN), in Nm/A phase peak.
Free speed=Vmax_LN*effective KV_LN, with an optional live rpm override.
Tmax=effective Kt*I_peak*GR; GR*SF=free speed/initial hip rpm.
Exactly one checked Driving field (torque, GR or SF) determines the other two.
Motor current uses I_peak, not I_cont. Bus voltage and switching frequency are
profile metadata; no additional voltage conversion or loss model is applied.
All selections, effective supply ratings, independent choice, overrides and power
ceiling persist in the complete design snapshot. Loading older snapshots loads
the first supply profile when no supply was specified.

The trajectory is deterministic for fixed inputs and this chosen control law.
Some inputs have no contact-feasible catch. Pure constant power to zero speed
would require unbounded torque; the finite cap is therefore part of the model.
The plateau is constant mechanical resisting power; low-speed capped-torque power
falls to zero. Hip power peaks are computed independently, rather than multiplying
separate torque and speed maxima. Belt power remains a distinct signal.

Numerical validation must cover endpoint rest, power plateau/cap, energy work,
resolution convergence, massless/distributed modes and UI/config persistence.
This experimental calculator does not establish hardware safety or drop survival.

## Validation — 2026-11-16

verify-power.cjs passes 6530 assertions across DP9–12, massless/distributed modes,
0.25/1m heights, positive contact, exact-rest endpoint, torque/power limits,
independent work closure within0.05J and grid refinement within0.3 percent.
Live Chrome checks verify four configs/defaultDP9, motor controls and config
roundtrip; launcher reuse on8770 passes. All V6 file hashes remain unchanged.
Spring library reads the original shared45 records. DP10 currently loads alpha0
despite its Alpha15 title; retained as stored. Historical v6-* verification JSON
files are copied references, not claims that V7 passes constant-torque tests.

## Motor configuration update — 2026-11-16

The exact relation is resolved from touchdown kinematics before power shooting;
no motor/fall iteration is needed because touchdown speed is independent of the
resisting torque cap. The three checkbox states always leave one independent
field. Profiles require positive finite KV/speed and unique IDs. Comments are
editable. Preset changes are shared across sessions via explicit JSON saves;
unsaved editor changes are not written by changing live solver parameters.

Validation: verify-motors.cjs passes54 exact-relation checks over3 motors,
3 independent choices and2 heights; fixed-ceiling numerical regressions still
pass6530 assertions. Live browser tests verify preset binding, two checked
Driven boxes, config roundtrip and explicit save/reload; invalid presets reject
before writing. V6 and existing Excel configuration/spring workbooks are untouched.

## Phase-KV correction — 2026-11-16

Motor KV is the line-to-line peak rating. Phase KV_LN=sqrt(3)*KV_LL;
Kt=(3/2)*60/(2*pi*KV_LN), in Nm per phase-peak ampere. The automatic
110/140/170 values are0.075181213/0.059070953/0.048646667 Nm/A. This corrects
previous Kt values by a factor of1/3, affecting driven torque ceilings and catch
feasibility. Imax is interpreted as phase-peak current, matching the supplied sheet.

Live phase-KV and Kt controls have explicit Override checkboxes. Phase override
changes calculated Kt; Kt override takes precedence. Clearing an override returns
to the formula. Motor Configs also supports optional phase/Kt override columns;
blank means automatic. Profile overrides persist with Save motor configs; live
overrides persist in design snapshots. Changing motors loads that profile's
saved overrides. Existing manually phase-converted preset KV edits were migrated
from kv into kvLNOverride with LL ratings retained, and the old JSON is backed up.

Checks cover screenshot values, all motor/independent-field equations, override
precedence, profile-save behavior and design config roundtrip. A low derived
ceiling remains an infeasible fall rather than being replaced by the old value.

## Two fall solve modes — 2026-11-16

Minimize power remains the default and solves the smallest constant mechanical
power budget (with the resolved torque ceiling) reaching first rest at theta2c.
Its prior behavior is retained; the maximum-mode ceiling does not constrain it.

Maximize power applies pointwise maximum resisting magnitude
T=min(Tmax,Pceiling/omega2), with Pceiling initially2000W. If the torque limit
binds, actual power is below the ceiling; constant Tmax throughout is recovered
when the power limit never binds. Forward energy integration locates the first
zero-speed event, then switches to holding at that angle. theta2c is the travel
limit. Reaching it with positive kinetic energy is infeasible; trajectories
requiring tensile ground contact are also rejected. This is a maximum-resistance
comparison, not a general optimal-control or hardware-safe recovery policy.

All dedicated fall curves end at actual first rest. Displacement peaks in alpha
and height sweeps use actual stopping travel in maximum mode. Fall Analysis Mode
rejects queries beyond the stop; headline sweeps only evaluate the caught stroke.
Solve-mode and power ceiling are saved in the complete parameter snapshot.

Numerical checks cover force/torque/power bounds, first-rest events, energy work,
mode ordering, mass modes, alpha sweeps, sampling limits and grid refinement.

## Recovery totals — 2026-11-16

The third fall-headline row reports hip-motor mechanical energy absorbed,
recovery duration and average absorbed power for the current fall. Energy is
trapezoidal integration of signed resisting power -tau2*omega2 against the
sampled time curve, from touchdown to first rest. Holding is excluded. The
belt/motor max-power-point selector does not change these hip-motor totals.
Duration is the actual caught stroke in both solve modes, and average power is
energy/duration. Infeasible catches show unavailable values. Totals are included
in the full design snapshot outputs without altering saved input workbooks.

## Supply capacity study — 2026-11-16

The six supplied 42V rows (15/20/30/40/48/60kHz) initialize Vmax_LN, power,
overheat and continuous current from the user's table. I_peak=120A for every
row, explicitly confirmed by the user. Profile comments are dropdown names.
Free speed, phase KV and Kt have live Override checkboxes; blank profile
KV_LN/Kt override cells use the calculated values shown as placeholders.

Calculate max fall height launches a cancellable background study (about10s
for the reference DP9 geometry on the verification machine), leaving the current
fall plots unchanged. The three independent rows enforce: torque only; torque
and specified power ceiling; torque, power and specified overheat duration.
All use the existing maximum-resistance law, stop at first rest at/before
 theta2c and choose GR anew at each trial height with SF=1. The reported rpm is
Link2 rpm, not geared rotor rpm. Full-stroke rotor speed, nonnegative ground
contact and valid spring geometry are required. Changing inputs marks old
results stale and cancels an active study. This is not the later motor/supply
permutation sweep.

For fixed geometry, touchdown energy=B*h and the SF=1 torque cap=A/sqrt(h).
The necessary work inequality B*h+C <= A*Q/sqrt(h), where C is full-stroke
 gravity work minus added spring energy and Q=(theta2c-theta2e) radians,
gives a finite upper search bound. The study scans linear and logarithmic
heights below that bound, refines the highest detected feasible boundary and
checks it with denser contact/time sampling. Feasible islands narrower than the
sampling may be missed: these are numerical maxima for this control law, not
proofs of globally optimal control or hardware survival. The arbitrary thermal
threshold means total recovery time <= overheat seconds; it does not implement
I-squared-t, temperature integration, cooling or continuous holding thermals.

Continuous payload is an independent static 1G calculation at the **current**
resolved GR. It removes the entered payload from the baseline, retains chassis,
active component gravity and the current ideal calculator spring, then uses
linearity in added per-leg payload to intersect |tau2(theta)|<=Kt*I_cont*GR
at1601 poses throughout the working range. Outputs are maximum total payload
per leg and four-leg robot payload, limiting angle and continuous geared torque.
Both torque signs count. An overcompensated baseline can imply a minimum payload
as well as a maximum; no feasible interval is reported explicitly. No independent
continuous-power or spring-catalogue/structure capacity constraint is inferred.

Validation: verify-supplies.cjs covers all18 KV/supply pairs, exact torque/speed
relations, independently checked static payload limits, the no-spring/massless
closed-form payload result, power/thermal height ordering and an active thermal
boundary. Browser checks exercise profile persistence through mocked explicit
saves, live overrides, single Driving selection, the background study and stale
state. Existing fall regression tests are rerun separately. These are isolated
analytical app checks, not canonical robot or measured motor validation.

The current minimum-power graph still reports the required budget even if it
exceeds the selected supply ceiling, and explicitly warns in that case. Maximum
mode and the restricted height rows enforce the ceiling.

UI placement correction: the complete live motor input card has been restored
to the main column above Fall Recovery, with both selectors visible and the
editable libraries below. Parameters, profile storage and calculations are unchanged.


## Frequency sweep

The new section below capacity runs all in-memory supply profiles against all
motor profiles. It leaves the current single-case section intact. The restriction
selector switches among the three rows without another solve. The compact2x4
grid contains seven graphs and one legend. GR and payload always show all motors;
the other curves share a reference when they overlap. If overrides break that
cancellation, the legend explicitly identifies the reference-only curves.

Each point uses SF=1, the supply's own power/time/current ratings and computed
free speed; live power and free-speed overrides are excluded. Payload is evaluated
at each maximum-height result's GR, as confirmed by the user. Thus Kt*Icont*GR
sets capacity. Under the automatic formulas, Kt*free cancels KV; equivalent cases
reuse one search. Overrides are checked by this product and solved separately.
The same finite height scan and its limitations apply. Inputs mark old results
stale; cancellation is supported. No libraries are written by the sweep.

Read-only verify-frequency.cjs checks reuse and agreement against an independent
solve. Browser verification covers all seven plots, restriction switching and
stale results. This is numerical, not hardware validation.

## DP18 catalogue campaign - 2026-11-22

S0075 retained; S0081-S0090 mixed suppliers and S0091-S0100 single supplier.
V6 workbook untouched. Added MD/RF/DM imports; FOX reserve0.5 mm below its
marked travel, with derived force ratings remaining provisional. See
[ranked evidence](../../springs/research/2026-11-22-dp18-search/README.md).
