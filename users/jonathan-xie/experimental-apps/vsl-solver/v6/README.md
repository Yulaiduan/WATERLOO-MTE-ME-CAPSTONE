# VSL Solver V6 — Spring lab

Open **Open VSL Solver v6.cmd** in this folder. The calculator runs at
http://127.0.0.1:8769/v6/v6-springlab.html and binds only to localhost.
V5 and the source catalogue remain separate and unchanged.

## Mass and existing analyses

Every total-mass input and configuration-library total is now **mT, whole-robot
mass**. The analytical engine receives **mL=mT/4**. A lab payload case uses
**mL=(mT+payload)/4**, assuming equal sharing by four legs. A 45 kg robot therefore
means 11.25 kg per leg; with a 70 kg payload it means 28.75 kg per leg.

The advanced mass-distribution inputs are per-leg component masses. Editing a
moving mass redistributes the fixed total by adjusting the driven chassis share.
V4/V5 configuration imports retain their original per-leg physics; their displayed
robot total becomes four times the old total. The copied V6 Excel library contains
the six original design points, including their names; names containing old masses
are retained verbatim. Its stored component parameters remain explicitly per-leg.

The ideal spring calculator, seven-variable fit, static/FBD/belt plots, 8×4 fall
study, analysis modes, range controls, pinned ribbon and configuration library are
retained. Fall dynamics still use a vertically translating point mass. Changing
the mass retains the current load in multiples of per-leg weight. Spring lab is
an independent **static gravity-compensation** study: it does not replace the ideal
spring in the other analyses or claim to select an impact-rated cartridge.

## Spring lab

The lab is immediately below the master controls. Enable `n` to use multiple
payloads (default 0 and 70 kg); disabling it evaluates the first case only. `m` is
the maximum number of installed spring slots, not a requirement to fill every slot.
Repeated catalogue parts are permitted. Bounds support 1–8 cases, 1–12 slots and
1–50 requested solutions. Search trials are editable, from 50 to 2000.

`r_h`, `r_s` and `nu` are held during Solve. `S_v` and `S_u` are searched within the
visible bounds. All can also be edited for a selected cartridge. `p0` is the sum
of reference forces of enabled springs in **case 1**; changing it manually adds a
common deflection adjustment to that subset, which also affects other cases using
those springs. Per-spring p0 and case enable checkboxes are editable in the table.
Manual changes are not written until **Save edits as new solution** is pressed.

Bulk piston preload is a **common deflection in mm**. Each installed spring has a
fixed additional, nonnegative individual preload deflection. Both are identical
across payload cases. The only case-dependent operation is enabling/disabling
spring slots. Disabling a spring assumes the proposed mechanical intervention can
isolate its force without changing the cable position or other springs' preloads.

## Equations and limits

Lengths are mm, rates N/mm, forces N, angles degrees, torques Nm, energy J.
The lab uses the same clockwise incoming tangent and retained-wrap route as V5.
For horn H(theta), pulley centre S and radius r_s:

```
d(theta) = |H(theta)-S|
psi(theta) = continuous polar angle(H-S) - acos(r_s/d)
c(theta) - c(90) = sqrt(d(theta)^2-r_s^2)
                  - sqrt(d(90)^2-r_s^2) + r_s[psi(theta)-psi(90)]
delta(theta) = c(theta)-c(90)
x_i(theta) = bulk_mm + individual_i_mm + delta(theta)
F_i(theta) = F_initial,i + k_i*x_i(theta)
F_case(theta) = sum(enabled_i * F_i(theta))
tauS = -F_case * dc/dtheta / 1000
tau2 = -tauG - tauS
```

`theta` derivatives in these equations use **radians**. Physical compression-spring
length is free length minus x; extension length is free length plus x. All springs
share a one-to-one cable/piston displacement. The assumed cartridge linkage makes
increasing cable payout increase spring deflection for either spring type.

For a chassis point mass, tauG=mL*g*Jz, where Jz=dz/dtheta in metres/radian.
For imported nonzero moving-link masses, the lab also includes their existing
static gravity moments, matching the old static model at beta=0 and Fy=0. This
moving-mass correction is separate from the massless-link fall assumption.

The system `l0` is the virtual span |S-H| at 90 degrees. **Delta-l is the maximum
minus minimum actual cable payout over working travel**, including finite-radius
wrap; it is the piston stroke. The spring table's l0 and le are **physical spring
lengths** at 90 degrees and theta2e. The system pe output lists each payload case's
total force at theta2e. The first-contact/hardstop angle remains theta2e.

Every installed spring is checked at the 90-degree preload reference and over
the entire working travel, even in cases where it is disabled. The allowed maximum
deflection is the minimum implied by catalogue travel, force, rated minimum/maximum
length and maximum energy. For initial force Fi and deflection x:

```
E(x) = (Fi*x + k*x*x/2)/1000
```

Unknown/missing essential limits, unrated initial tension, rubber, cut-to-length
and assortment entries are excluded. Rows flagged for nominal supplier-data
mismatches may be used only through the conservative intersection of all stated
limits. Their force law remains a nominal linear screening assumption. `l_min`
means the catalogue's rated minimum length, **not necessarily solid height**.

## Search and saved solutions

For each candidate geometry and enabled-subset matrix, the search estimates the
required aggregate stiffnesses, selects nearby feasible catalogue springs, then
solves a linear minimax problem for the fixed per-spring preloads. The objective is
the largest **absolute residual tau2 across all cases and working angles**.
Best candidates receive bounded geometry refinement and a denser preload fit.
The source book is read directly, not replaced by a stale exported catalogue.

Cable-displacement extrema and hard limit checks use analytic critical angles.
Residual-torque extrema are sampled at 1201+ poses for saved solutions (4001+ in
verification). This is a bounded mixed discrete/numerical search, **not a proof of
global optimality or exact compensation**. A feasible solution can still have a
large residual; compare the reported Nm values. Asking for more solutions can
return fewer distinct valid candidates. Larger bounds/trial budgets or more slots
can help, without guaranteeing an improvement.

Solve saves returned cartridges to
`../../springs/v6-spring-solutions.xlsx`. Stable SXXXX IDs increase monotonically,
including after deletion. Enter an ID or use the arrows to select one; the arrow
keys work in the solution ID box. Selection restores its leg/mass/angle context
and lab settings. Favorite and Delete persist immediately. Saves are atomic,
serialized, and retain one `v6-spring-solutions.backup.xlsx`; a locked Excel file
produces an error instead of discarding a valid browser result. Retry with
**Save edits as new solution** after closing Excel.

The workbook contains Solutions, Springs, Payloads, Readme and VSL state sheets.
The first three are human-readable reports; edit spring solutions in the lab.
VSL state contains the complete reload records, next ID and catalogue hash. Source
catalogue:
`../../springs/outputs/2026-10-28-mmc-springs/mmc-spring-catalogue.xlsx`.

Three verified compression examples are included. **S0001** uses r_h=62.22695 mm,
r_s=10 mm, nu=0, S_v=70.36357 mm and S_u=7.79904 mm. At mT=45 kg, payloads 0/70 kg,
L2=L3=300 mm, q_ab=2, alpha=phi0=0 and theta2=100–165 degrees, its peak residual is
about **0.2851 Nm**, with about **66.527 mm** piston stroke. It uses 96485K342 and
2006N469 for both cases and adds 96485K182 for the heavier case. This is a screening
example, not a selected production design.

## Runtime and checks

The local helper needs Python 3.10+ with `numpy` and `scipy` (requirements.txt).
Workbook saves use Node.js with the bundled public `@oai/artifact-tool` runtime.
The helper finds the user's bundled Node runtime first, then Node on PATH;
`VSL_NODE` can select another executable. The writer locates the library next to
that executable, or via `VSL_NODE_MODULES`.
It never installs dependencies or modifies the catalogue. The launcher uses the
locally installed Python, binds port 8769, and reuses an existing matching server.
The ideal calculator can open as HTML, but catalogue search and Excel persistence
require the launcher. Source-controlled scripts contain no machine-specific paths.

Read-only numerical checks:

```
python verify-spring-lab.py
python verify_excel.py
node verify-fall.cjs
node verify-analysis.cjs
node verify-belt.cjs
node verify-ui.cjs
```

Spring checks compare Python geometry with the retained JS model, verify the ideal
point-pulley identity, search both catalogue types and check force, travel, length
and energy limits on dense trajectories. Existing fall/belt/UI tests are retained.
Browser interaction, Excel roundtrips and preservation hashes are recorded in
v6-browser-verification.json. These are calculator checks, not fatigue, buckling,
hook, friction, packaging, dynamic spring or hardware qualification.
