# VSL Solver V7 — power-limited fall recovery

V6 is preserved separately. Start Open VSL Solver v7.cmd; the isolated helper
serves http://127.0.0.1:8770/v7/v7-springlab.html. V7 configs retain DP9–12 with
DP9 loaded at startup. The existing shared springs/v6-spring-solutions.xlsx
pointer remains; V7 does not create or replace spring solutions during startup.

The fall controller uses positive resisting magnitude T=min(Tmax,P/omega2) and
signed applied hip torque tau2=-T. A backward numerical energy integration solves
K'=tauG+tauS-T with K(theta2c)=0. Monotone shooting selects the minimum P reaching
the inherited touchdown energy at theta2e. Angular effective inertia H includes
rod translation/rotation when component masses are enabled. Existing omit and
transfer mass modes remain active. Contact lift and dead centres still reject
trajectories. Positive impact energy is required; h=0 is not an impact catch.
At first rest the capped resistance switches to the existing static holding law.

Motor presets start at KV/free-rpm 110/2830, 140/3601 and 170/4373, with
7070 comments. Imax starts at50A and remains a user input. motor-configs.json
stores editable motor presets through the local helper's explicit Save button.
Free speed follows the selected profile, including after loading old configs.

Two equations are enforced exactly: Tmax=Kt*Imax*GR and
GR*speed_SF=free_speed_rpm/initial_hip_rpm, where
KV_LN=sqrt(3)*KV_LL; Kt=(3/2)*(60/(2*pi))/KV_LN. One field is independent and two are driven.
The default independent field is speed_SF=1. Unchecking another field's Driven
box makes it independent and preserves the current resolved operating point.
Derived SF below1 or later speed above the initial allowance produces a warning.
The independent choice and all motor inputs persist in design snapshots. The derived GR is fall-specific,
not one fixed gearbox proven for every sweep. A later speed above the initial
allowance produces a warning. Electrical/regenerative power, motor/belt losses,
rotor inertia, voltage/current dynamics and a measured motor envelope are excluded.

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
