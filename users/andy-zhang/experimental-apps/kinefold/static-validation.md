# Dynamic static-limit comparison with Jon's VSL v4

Andy Zhang with Codex, 2026-10-22. Experimental numerical consistency check
against Kinefold runtime revision `2acd7c5`; no runtime, UI or profile changes.

Both floating-chassis engines match the original V4 static solution when the
loads and boundary conditions match. The check holds wheel height constant,
starts at rest with zero damping, applies V4's required constant hip torque,
and actually integrates each engine for one second. It does not replace the
dynamic rollout with a static answer. Every rollout must finish its full
duration; reaching a travel stop cannot count as a pass.

## Reproduce

From this app directory, after its existing setup:

```powershell
.venv/Scripts/python.exe validate_static.py --output .preview/static-validation.json
```

[validate_static.py](validate_static.py) extracts only the analytical blocks
directly from [Jon's original HTML](../../../jonathan-xie/experimental-apps/vsl-solver/v4/v4-pulley.html),
checks the original source and retained-block SHA-256 values in
[reference.json](reference.json), then evaluates that independent JavaScript
oracle with Node. It does not use the Python dynamics or Kinefold's adapter to
generate expected static values. The optional JSON output is an ignored raw run.

There are 63 directly matched β=0 cases and nine offset cases matched with the
explicit support-moment correction below: 72 cases and 144 one-second equilibrium runs,
plus four 0.2-second runs that deliberately violate equilibrium. Nine interior
poses span 100.1–164.9°; endpoints are avoided to prevent travel-stop ambiguity.
Eight designs cover the unmodified V4 baseline, unequal links and pulley ratios,
nonzero moving masses, mounting angle, both spring laws, point idler,
disabled spring, additional global/contact loads and the offset support case below.

## Baseline result

The original design retains m1=8.75kg, zero other masses, 300mm links,
200mm wheel radius, finite-idler coil and θ₂=132.5°. With flat input:

| Quantity | Original V4 | Analytical | Pymunk |
| --- | ---: | ---: | ---: |
| Required hip torque (Nm) | −0.027168833380 | −0.027168833380 | −0.027168833380 |
| Spring tension (N) | 570.491044815 | 570.491044815 | 570.491044815 |
| Vertical support reaction (N) | 85.8375 required | 85.8375 derived | 85.8375 derived |
| Maximum chassis drift over 1s (mm) | Static reference | 0 | 0 |

The V4 spring provides approximately constant support. Flat input with **zero
hip torque** therefore does not give exact equilibrium: initial chassis
acceleration is −7.659992438mm/s². After 0.2s the chassis moves −0.153141546mm
analytically and −0.152377279mm in Pymunk. This is the expected residual of the
V4 fit, not a solver mismatch.

Across all 72 matched cases, maximum holding-torque error is 5.69e−14Nm and
spring-force error is 3.42e−13N. All 144 runs finish their requested duration.

| Maximum error/drift | Analytical | Pymunk | Required tolerance |
| --- | ---: | ---: | ---: |
| Hip angle drift (deg) | 3.13e−13 | 2.85e−13 | 1e−8 |
| Chassis height drift (mm) | 7.96e−13 | 0 | 1e−8 |
| Derived support reaction error (N) | 2.28e−13 | 2.28e−13 | 1e−8 |
| Chassis acceleration magnitude (mm/s²) | 2.36e−11 | 2.36e−11 | 1e−7 |

Torque tolerance is 2e−10Nm, spring-force tolerance is 2e−9N and geometric
centre-position tolerance is 2e−9mm. Tolerances are declared in the script;
reported errors are actual floating-point residuals, not physical accuracy.
The run used Python3.13.12, NumPy2.5.3, SciPy1.18.1, Pymunk7.3.0 and Node22.20.0.

## Load and boundary mapping

The chassis is vertically free with horizontal position/pitch locked. The wheel
height actuator supplies a vertical reaction **at centre C**. Gravity acts once
on every builder mass. In weight-reference mode, the displayed static weight
load is replaced by that reaction rather than applied again dynamically.

Let M be total builder mass and Fz,extra an additional explicit wheel load.
At equilibrium, R = Mg − Fz,extra. For comparison, Jon's static solver receives
the same horizontal force and **total vertical force Mg**. At β=0 the support
line through the bottom patch P also passes through C, so the hip torques agree
directly, including for nonzero wheel coefficient K.

At β≠0, putting all of that force at Jon's rim point P adds a moment absent
from centre-applied dynamic support. With rw in metres and source-positive
torque signs, the required correction is:

```text
tau2_Jon − tau2_floating = rw × R × sin(beta) × K
```

Explicit additional loads retain their existing rim moment. The correction
removes only the moment introduced by moving support R from C to P.
It does not alter either model or silently treat those boundary conditions as equal.

The deliberate offset case uses β=25°, K=−0.0231849887022 and R=93.4195N.
Its uncorrected Jon torque is 5.602012962057Nm; the floating torque is
5.785085280789Nm, a difference of −0.183072318731Nm in the equation above.
Both engines hold with the corrected torque. Using the uncorrected torque
causes +1.115481045mm / +1.110100288mm chassis movement after 0.2s,
respectively, so the test detects that intentional boundary mismatch.

## Scope

The held chassis pose is observed from the actual engine rollout. Spring force
and vertical support reaction are derived ideal-model quantities; Pymunk's
reaction readout is not an independently measured tire/contact constraint force.
Pymunk integrates one actual chassis body with ideal linkage inertia condensed
into its force law. This validates static-limit consistency of hip torque,
spring law, support and pose; it does not validate individual belt tensions,
pin forces, drive-shaft reaction torque, contact, impacts, hardware or a
four-leg robot. The 150mm square profile and saved designs remain unchanged.
