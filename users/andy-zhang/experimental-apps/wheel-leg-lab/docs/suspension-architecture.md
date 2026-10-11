# Constant-lift replacement wheel-leg suspension

Owner: Andy Zhang. Updated: 2026-10-10. Status: editable member experiment.
The latest clarification replaces the original spring with **one upper-r1
spring/damper attached to the chassis massblock rigidly mounted at J1**.
The earlier two-stage factory is superseded; no canonical hardware is selected.

Start **Start Motion Lab.cmd** and open
[the replacement suspension](http://127.0.0.1:4186/?tab=physics&architecture=constant-lift).
The lever bridge and main/Physical menus load this profile before the first solve.

## One replacement unit

| Parameter | Editable factory value |
| --- | --- |
| Wheel radius / link length / original lower extension | 200 / 273 / 50 mm |
| Chassis mount below J1 / upper attachment radius | H=150 mm / R=136.5 mm |
| Topology / elastic law | `gravity_balance` / `zero_effective` |
| Effective / physical coil free length | 0 / 230 mm |
| Auto-calibrated rate / primary damping | about 2260.04367 N/m / 100 N s/m |
| Auxiliary / knee impedance | Disabled / kp=kd=0 |
| Guide hip / knee radii | 28 / 14 mm |

The primary force pair acts on the chassis/hip body and upper link. The old
hip-to-lower-extension strut is disabled. The chassis heaves freely with pitch
held; wheel height is prescribed. The drawn coil/damper uses actual primary
anchors. Positive physical coil length emulates the zero-effective law through
ideal routing/preload; the drawing does not establish real package fit.

For theta from horizontal, `h=2L sin(theta)` and
`d²=H²+R²-2HR sin(theta)`. Elastic tension `T=k*d` gives moment
`kHR cos(theta)` and equivalent support `kHR/(2L)`, about 84.751637708 N with
the demo masses. Tension and moment vary; elastic equivalent support is constant.
Damping adds velocity-dependent load. Exact compensation is **neutral**: it has
no positive elastic ride-height stiffness. Damping stops motion but does not
select a unique static height. No hidden spring or controller repairs that limit.

## Guide belt, solvers and records

The hip drum is fixed to chassis, knee drum to lower link, upper link the moving
carrier. Physical ratio 2:1 maps to Pymunk absolute ratio -1 and phase pi. Exact
tangent geometry and recorded angles drive belt marks/spokes. Guide torque gives
only `DeltaT=tau_K/r_K=-tau_H/r_H`. Unknown baseline does not determine absolute
spans or bearing loads. Optional N/kgf baseline assigns one assumed span and
the other baseline plus absolute difference. These viewer forces are not applied
to solver loads and remain independent of reference-sheet T₀.

Six sensor shapes are the two links, wheel, chassis and two guide circles; they
add no mass/contact. Point-force architecture has six constraints and twelve
Plotly charts. Both solvers accept the flat factory profile from
`GET /api/suspension-architecture/defaults`. SciPy integrates independently;
Pymunk applies real primary force pairs before stepping (`point_force`).

Saved profiles retain auxiliary off, chassis/guide sensors enabled and guide
hip radius .028 m. Viewer settings stay in `reference_inputs.guide_visualization`,
outside solver config. Native accepts flat wheel config or
`{model:'wheel_leg',config,guide_visualization}`. Reuse includes viewer options;
global launch uses the visible frame, explicit saved/child config takes precedence.
Live desktop GUI runs on the host; browser recorded playback is separate.
See [audit](mechanism-audit.md) and [validation](validation.md).

## Optional earlier two-stage variant (superseded factory, 2026-10-10)

The earlier factory added a captured hip-to-lower-tip strut, k8000 N/m and
c500 N s/m, zero initial elastic preload. It remains explicit via
`aux_spring_enabled=true`, never auto-enabled. Its actual forces and energy add
only when selected; extra channels expand the charts to fifteen.

```text
s(theta)=sqrt(L²+e²+2Le cos(2theta)); s_ref=s(theta_initial)
T_aux=k_aux (s-s_ref)+c_aux ds/dt; Q_aux=-T_aux ds/dtheta
K_vertical_at_reference=k_aux (ds/dtheta)²/(dh/dtheta)²
```

Captured behavior restores either side near reference; one-sided modes can slack.
Manual preload shifts equilibrium and is not silently removed by primary balance.
Historical evidence remains in validation.

The wheel-height fixture is bilateral; negative reaction implies ground may detach.
Tire/terrain contact, pitch/roll, spring implementation, routing/clearance, friction
and structural ratings remain unverified. MATLAB rejects gravity compensation
and enabled auxiliary mode; use SciPy/Pymunk.
