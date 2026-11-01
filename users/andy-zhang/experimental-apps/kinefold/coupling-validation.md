# 1:6 drive-train coupling validation

Andy Zhang with Codex,2026-11-01. Experimental member-app evidence at source
7ea04c5; no hardware/canonical acceptance. Exact named profile:
`test 1:6 drive train coupling test`; saved and working physical settings matched
when frozen. Its [portable snapshot](saved-configurations/test-1-6-drive-train-coupling.json)
has SHA256 `66435f092ccccdbb5bcfaea8350ea65db4201dbc515a331665003af2d12fe4e6`.
The original live library was not overwritten or retuned.

## Outcome

The 2:1 leg coupling and wheel/carrier kinematics agree with independent open-belt
equations. Both dynamic engines implement the profile's free,unforced wheel-drive
input consistently. This does not validate a loaded/locked wheel-drive motor or
physical belt-span,radial or bearing loads. Ideal AB equivalent reactions agree
closely in a bounded flat-floor diagnostic; their reconstruction limits follow.

## Exact profile and independent kinematics

L2=L3=300mm,rw=200mm,ra/rb=50/25=2,rc/rd=25/150=1/6,re/rf=25/150=1/6.
Alpha=phi0=0,hip limits100–165deg,initial149.4deg. Quarter masses:m1=8.75kg,
m2=m3=1kg,m5=0,m6=.5kg. V4 spring K8N/mm,p0=330.869282809N; damping1Nms/rad,
entered hip torque0. Contact friction.8,zero bounce,free drive; no motorConfig.
The two wheel-drive stages give36:1 input/wheel reduction when the leg is held.

Every ideal open belt obeys `r1*(w1-wCarrier)=r2*(w2-wCarrier)`. Therefore:

```text
w3 = -w2
w5 = (5/6)*w2 + (1/6)*w4
w6 = -(25/36)*w2 + (1/36)*w4
theta6 = -(25/36)*(theta2-100deg) + theta4/36
C_x = 0; C_z = -600*sin(theta2) mm
```

Theta4 is the wheel-drive input,distinct from the leg coordinate theta2. The
2:1 belt gives a straight spatial path; height is sinusoidal in hip angle.
Full compression raises the wheel435.593225mm relative to the hip. Holding
theta4=0 gives wheel rotation−45.138889deg,clockwise in the +x-left/+z-up view.
Its−157.564446mm signed rim arc is not ground displacement.

A free input does not impose that wheel rotation. Rearranging the same equation:
`theta4=36*theta6+25*(theta2-100deg)`. If wheel angle stays constant,a full leg
sweep instead backdrives the input1625deg=4.513889turns. Actual terrain contact
determines wheel spin. At the saved149.4deg pose,builder and both actual engines
start at wheel−34.30555556deg,input0deg,compound41.16666667deg: phase matches.

An independent1001-pose audit gives horizontal straightness error<=1.14e-13mm.
Actual studio/contact drawing APIs pass240belt-wrap velocity checks at drive
rates0,1,25; worst finite-difference discrepancy2.87e-7mm/rad.252index checks
pass. Independent finite-rod static virtual work agrees<=1.67e-8Nm.

## Force coupling and what the free input removes

For an external +y wheel moment M,its ideal static holding contributions are
`tau2=+25*M/36`, `tau4=-M/36`; these satisfy power balance. Equivalently,if a
wheel-drive input torque T4 were applied,its generalized contributions would be
`Q2=25*T4`, `Q6=36*T4`. Carrier terms matter; multiplying only by36 misses the
leg reaction. These are ideal virtual-work relations,not a loaded-drive rollout.

This saved profile has T4=0,no wheel-drive input inertia,and massless compound
pulley m5=0. Eliminating those unforced coordinates leaves independent wheel
spin; CD/EF torque differences vanish and input motion is reconstructed. Native
does not instantiate CD/EF carrier constraints; analytical uses reduced wheel
spin. This is consistent for this exact case. A loaded,locked or inertial
wheel-drive input needs additional generalized torque/inertia terms or native
carrier constraints and is unsupported by the current contact assumptions.

AB is active. Native GearJoint applies equal ideal rod torques G and enforces
the 2:1 velocity relation with fixed chassis pitch. The physical chassis couple
is−2G; it is inferred rather than explicitly applied/logged on the infinite-
pitch-inertia chassis. Its zero pitch rate removes it from this reduced model's
power balance; this is not full-vehicle chassis-reaction validation.

## Six actual bounded diagnostics

Preserve every physical profile value and all constraints/guards. Explicitly
replace the saved100mm-RMS,20%-grade talus terrain with a stationary flat floor
for.25s,at dt1ms/.5ms,in both engines; add a gentle20mm/s flat-floor pair at.5ms.
No wheel pinning,chassis-height pinning,substituted masses,controller or retune.

| Refined .25s endpoint | Analytical | Pymunk |
| --- | ---: | ---: |
| Stationary chassis downward motion |31.175061mm|31.123333mm|
| Stationary wheel angle change |0deg|0.000000296deg|
| Stationary drive-input backrotation |85.024070deg|84.866006deg|
|20mm/s floor wheel angle change |1.429530deg|1.426665deg|
|20mm/s floor drive-input backrotation |136.487139deg|136.225942deg|

Both satisfy `w4=25*w2+36*w6` within approximately1.2e-13rad/s. Native observed
per-body momentum agrees with native pivot/AB impulse magnitudes within about
4.5e-15Nms for angular reactions; ideal AB virtual-power residual<=5.4e-13W.
On step halving,native pivot power residual.02510→.006018W and maximum positional
constraint error.04170→.01001mm.

For the same final0.24–0.25s stationary interval:

| Ideal AB equivalent | Analytical reconstructed | Native impulse mean |
| --- | ---: | ---: |
| Per-rod G,+y |+24.37739869Nm|+24.37566556Nm|
| Signed U−L=G/rb |+975.09594749N|+975.02662259N|
| Inferred chassis couple−2G |−48.75479737Nm|−48.75133113Nm|

The torque difference is.00173312Nm,about.0071%. Analytical reconstruction uses
exact interval-end momenta,midpoint lever arms and interval mean contact force;
it is approximate,not an explicit analytical reaction output or exact tension
equality. Native G is impulse/dt,not a continuous shock peak. Its last.5ms step
G=24.40641293Nm differs from the10ms mean; do not mix their averaging windows.

Signs follow the front-left right-hand rule. Native coordinates export
`x=-X,z=Z`,so `M_y=r_z*F_x-r_x*F_z=r_X*F_Z-r_Z*F_X`: native CCW scalar torque
has the same +y sign. For AB side+1,G/rb is the signed upper-minus-lower tension
difference. Individual span tensions,radial loads,bearing-force splits,slack,
elasticity and allowable strengths are not solved. All entered belt preloads
are0; bilateral ideal constraints do not prove physical belts remain taut.

The saved spring remains under-supported at149.4deg: grounded gravity torque
−49.3966938Nm versus spring−44.3582290Nm,requiring another−5.0384648Nm to hold.
This explains the flat sag; the free1:6 ratios are not its cause. No calibration
was applied. Energy residual on halving dt is.004896→.002472J analytical and
1.04961→.524816J native. Positional agreement does not validate the native energy
ledger; its residual is numerical,not physical energy absorption.

## Concurrent-source recheck

The live D checkout received separate,uncommitted spring-law/UI/Energy edits
during this audit. They were preserved and are not published by this contribution.
The primary evidence stays tied to7ea04c5. Its retained V4 branch was also checked
against the current snapshot:1001-pose/240-wrap/index/static-work checks retain
the same results. Two extra stationary.25s/.5ms actual backend runs,using exactly
the prior requests,compare6251analytical and6181native numeric fields with maximum
difference0,finite26-row/frame outputs and duration completion. Current backend
source hashes remained stable before/after that check.

The verification subprocess cwd was one directory above Capstone; explicit
absolute script paths selected the intended audited source and the outputs were
identical. The future helper's cwd was corrected without rerunning physics;
both helper hashes and this qualification are retained. Published evidence
includes hashes/comparison metadata,not the concurrent uncommitted source diffs.
Publication uses an isolated worktree so the live checkout's other work stays local.

## Reproduction and UI cleanup

Three GPT-6.1 Sol workers handled the duplicate-editor removal,independent
kinematics and bounded force audit. Source hashes,versions,exact frozen inputs,
compact summaries,selected refined raw captures/native trace and runnable helpers
remain ignored app-local/native Notion attachments. Two Plotly PNGs show the
ideal boundary conditions and actual free-drive response; superseded clipped
first renders are excluded. No physics source or tolerance changed.

00's duplicate Dynamic settings card/editor is removed; it edited the same
solverConfig as02/03. Saving/exporting still retains those settings,and the
read-only archived fixed-hip disclosure moved into the existing portability
card. Stale V4.5 template wording now acknowledges its finite-link contact
  support. Headless isolated profile checks
confirm02 edits reach03 and saved geometry/case fields persist. Concurrent live
saves during early checks were preserved; final isolated checks block every
unexpected POST and leave the live file hash unchanged. No Computer skill,
live-tab interaction,extra server or broad design search was used.
