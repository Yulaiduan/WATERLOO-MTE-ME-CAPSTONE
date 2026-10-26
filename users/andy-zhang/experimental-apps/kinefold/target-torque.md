# Jump and landing target torque sizing

Andy Zhang / Codex, 2026-10-23. Experimental quarter-model calculation and
simulation evidence; no hardware rating or global torque optimum is claimed.

Both dynamic tabs now show **Case inputs & target torque** directly below the
case selector. Essential inputs no longer require expanding a disclosure.
Choose Jump or Landing, enter the target, and select **Solve torque for target**.
The current tab runs its own integrator. **Use tested torque** explicitly copies
the passing command to the saved case; a normal run then shows its complete
trajectory and allows the same command to be compared across engines.

## Height definitions and decisions

- Jump target is the chassis apex rise **above actual takeoff**, excluding stance
  extension. The leg starts fully compressed at rest and uses the existing
  constant extension command until the extension stop, then cuts off.
- Landing drop height is the initial wheel-bottom gap to the stationary floor.
  During the held fall the chassis falls by the same distance before contact.
  Initial opening remains editable, default two-thirds.
- Minimum chassis height means **underbody-to-ground clearance**, default50mm.
  This is separate from the editable underside offset, default50mm below hip A.
  First arrest must occur before mechanical bottom-out and without dropping
  below the entered clearance during contact through that arrest.
- The wheel remains free, chassis translation remains vertical, and the saved
  mechanism, spring, motor reduction/inertia/cogging/losses and contact material
  feed both engines. Target settings supply observation criteria, not forces.
- Results assess the first jump flight or first landing arrest. Later rebound,
  settling and chassis clearance still need a complete run/controller assessment.

## Energy estimate and simulation search

The ideal jump work estimate assumes full extension at takeoff, with locked
relative geometry during flight:

`tau_joint = max(0, [m1*g*stanceRise + (m1+m6)*g*targetRise - springRelease - coggingRelease]/deltaQ)`

Angles use radians and heights metres. Ideal shaft magnitude is `tau_joint/N`.
Stop/contact/friction losses and retained rotor kinetic energy are excluded;
this optimistic work estimate cannot guarantee takeoff or the target apex.
The existing conservative chassis-only landing estimate is evaluated for the
visible drop and clearance target and explicitly states its pre-stop reserve.
**Copy landing targets & open Energy** copies these two values into the
separate Energy tab and opens it. The standalone energy workspace also provides
jump-height and drop-height torque curves, a signed stroke-work ledger and full
equation tables without running either engine; see [energy calculations](energy-calculator.md).
The legacy energy-sized braking strategy remains available and explicitly says
it is not clearance-targeted; applying a tested result selects entered braking.

The simulation search runs five coarse commands from zero to the entered ceiling,
then at most five local probes below the lowest passing command. It returns
the lowest **tested** passing command and a lower known-failing value when one
exists. Unobserved events or numerical failures are indeterminate, never proven
failing torque bounds. Exploratory probes can continue above an indeterminate
sample without calling it a failure. Limited sampling and nonmonotone contact
outcomes prevent a global-minimum claim. Duration is never silently extended.

Every integration step observes positive wheel separation, upward takeoff,
first apex before recontact, and landing clearance through first arrest.
Observations freeze at their terminal event. Measurements do not use decimated
plot rows. Both integrators shorten steps at output boundaries, so changing
outputHz can slightly change trajectories; refine timestep near a boundary.
Force laws and existing controllers are unchanged.

## Storage and compatibility

Optional project-v3 `torqueTargetConfig` stores `jumpHeightMm`,
`landingClearanceMm` and `jumpTorqueLimitNm`. Legacy profiles retain absence
until edited. Targets mark a named design dirty but do not change physical
modelRevision or dynamic snapshot identity. Search identity includes both
physical snapshot and targets. Changing either disables **Use tested torque**,
including edits made while a search is running. Search commands/ceilings use
the selected joint or shaft command basis; applying preserves that basis.
Assessment JSON captures the full profile and all trials in app `exports/`.

## Reproducible checks

Run `node verify-energy.cjs`, `node verify-projects.cjs`, app-venv Python
`verify_profiles.py` and `verify_torque_targets.py` from this folder. The latter
tests actual independent engines, full/early observation agreement, sparse
output schedules, chatter/recontact guards, strict inputs and indeterminate
search trials. Initial test fixtures incorrectly demanded exact trajectories
across output schedules; they now test classification and bounded numerical
differences. A Node VM fixture was also corrected to deserialize into the
validation realm; physical tolerances and production schema guards were unchanged.

Independent current-baseline jump reference: stance rise435.593224746mm,
stance gravity37.390233429J, spring release37.395126825J, travel1.134464014rad.
The100mm above-takeoff work estimate is8.859123323Nm; spring off41.821937807Nm.
The200mm estimate is17.722560046Nm. Actual simulated passing commands include
contact/stop behavior and need not equal these ideal values.
