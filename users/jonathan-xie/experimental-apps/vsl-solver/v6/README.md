# VSL Solver V6 — Spring lab

## Expanded supplier comparison, 2026-11-11

Twenty additional records cover ST, BT, MI, SW and mixed, each in parallel and
swap mode. Categories require at least one new-supplier spring; supplier-specific
cases permit only that source plus MMC. The source adapter reads the dated
additional-springs.json beside the original catalogue and preserves supplier URLs
and unknown dimensions. Catalogue rated l_max (free length for compression) is
compared with a 210 mm preference. Longer results and large residuals remain
explicit compromises; length is not silently redefined as installed length.

Parallel records require published outer ID and inner OD for a verified nominal
nest. Unknowns do not use installation-hole/rod dimensions as coil diameters;
those candidates show NESTING UNVERIFIED. The search screens force, energy and
travel, uses multistart geometry/preload fits and checks dense trajectories and
continuous payout limits. Results are best found, not exhaustive catalogue optima.

## Payload tension plots

Spring Lab ends with separate 0 kg / 70 kg total cable-tension plots. The x-axis
is fixed at -90 to 270 degrees; enabled springs determine force and catalogue
validity independently for each payload. Curves stop at the first invalid pose
in each direction from the working-stroke midpoint, avoiding disconnected valid
islands beyond an unreachable limit. Dotted lines mark theta2e, theta2c and the
theta2f target. Headline maxima use only the valid displayed component and include
analytical payout extrema. A full-sweep cable exit is used where geometrically
possible, consistent with the inversion study's redirectable outgoing cable.

## Nested compression comparison, 2026-11-11

The additional **Compression · nested parallel** group contains S0056–S0060.
The previous twenty solutions are preserved. Slot 1 alone compensates 0 kg;
slots 1 and 2 together compensate 70 kg. The outer spring need not be slot 1.
All retain DP9's 120–180 degree working stroke, -50 degree unloaded inversion,
r_s=12.7 mm, r_h=50–95 mm, S_v<=150 mm and |S_u|<=30 mm.

The catalogue's **catalogued ID**, rather than ID inferred from wire diameter,
is compared with the other spring's OD. This campaign requires at least 1 mm
nominal diametral clearance; the five saved pairs have 6.35–25.4 mm clearance.
The viewer shows ID per spring, identifies outer/inner slots and reports both
diametral and radial clearance. The writer includes these dimensions and the
nominal nesting result. Canonical saves recompute them from catalogue data.

The bounded multistart search minimizes unloaded peak residual subject to a
70 kg peak residual below 5 Nm, then verifies exact cable extrema and dense
signed torque/force/travel/energy trajectories. These are best-found results,
not an exhaustive optimum. The extra search is a curated group, not a new
exhaustive policy for the existing Solve button. Run `python verify-nested.py`
for read-only numerical/catalogue checks on the installed five records.

Nesting is a **nominal diameter screen**, not a manufacturing fit approval.
Catalogue winding direction and diameter-growth/tolerance guarantees are not
established for these parts. Confirm alternate winding hands or a suitable
separating guide, loaded diameters and adequate clearance. Different physical
spring lengths/preloads can need independently stepped annular seats; the
existing enabling/disabling mechanism is still assumed. Supplier guidance:
[Newcomb / Spring Manufacturers Institute](https://www.newcombspring.com/resources/compression-springs-nested).

## DP9 inversion search, 2026-11-11

The solution viewer has four groups of five cartridges based on DP9, “11/11 POR”.
The base chassis is 54 kg, the links are 296.3 mm, and gravity compensation is
evaluated over 120–180 degrees at alpha=0. Cases use 0 and 70 kg payload.
Parallel groups activate spring 1 at 0 kg and both springs at 70 kg. Swap groups
use spring 1 at 0 kg and spring 2 at 70 kg, with one spring installed at a time.

New lab defaults use r_s=12.7 mm, r_h bounds 50–95 mm and theta2f target=-50 deg.
The unloaded spring must stay taut and satisfy all catalogue limits continuously
from theta2f through theta2c. The payload spring is checked only over the working
theta2e–theta2c stroke. A 90-degree reference outside that spring's range is
marked as extrapolated. r_clear=S_v-r_h must be at least 2r_s. The viewer reports
the first clockwise spring/cable limit and checks a full revolution when no
earlier limit is found. This is a travel check, not a self-righting motor-torque
qualification or a collision/packaging model.

The campaign uses the final requested S_v<=150 mm and -30<=S_u<=30 mm bounds. The search
screens all eligible catalogue parts by force and energy bounds, optimizes the
unloaded geometry with multiple starts and exact inversion travel extrema, then
tests every same-type payload spring at the frozen geometry. Compression swap
candidates allow a small unloaded compromise to achieve <=5 Nm payload residual.
Other groups prioritize unloaded residual, then payload residual. Rankings are
best found in this bounded search. Extension results have substantial residuals
and remain comparisons rather than near-perfect gravity compensation.

Use the group selector and arrows to browse the results. The spring summary
includes rated l_min, rated l_max and OD. All data is saved in the solution
workbook, including inversion targets and verification results. Catalogue and
DP9 configuration workbooks are source data.

Open **Open VSL Solver v6.cmd** in this folder. The calculator runs at
http://127.0.0.1:8769/v6/v6-springlab.html and binds only to localhost.
V5 and the source catalogue remain separate and unchanged.

## Mass and existing analyses

`m_c` and `m_p` are whole-robot chassis and payload masses. The four legs share
`m_s=(m_c+m_p)/4`. The per-leg masses sum to `m_u`; the total is
`m_T=m_c+m_p+4m_u`. Gravity is fixed at 9.81 m/s². The master mass slider adjusts
payload. Editing a component changes the total and preserves the chassis input
and the current contact load in multiples of per-leg weight.

The sidebar uses the requested m₂ (tibia) and m₃ (femur) labels. Older saved
parameters and the Excel format keep their existing internal keys m2 (femur)
and m3 (tibia). Legacy configurations convert the stored sprung share to chassis
mass and start with zero payload. Spring lab uses the chassis, components and
each case's total payload. The ideal fit uses vertical 1g with zero payload.

The fall model holds chassis pitch and horizontal position fixed and uses a
vertical wheel reaction. The rods have midpoint centres of mass and centroidal
inertia mL²/12. The knee and wheel are translating point masses; wheel spin inertia
is excluded. At touchdown the model projects the common free-fall velocity onto
the ground-constrained motion, with no rebound or motor impulse. The motor then
resists the fall at constant torque. Both fall forces and fall-mode FBDs include the
components' accelerations. The acceleration plot describes the chassis; the
separate ground-force trace sums the vertical contributions of all bodies.
The fall calculation rejects trajectories that stop early or lose wheel contact.

## Spring lab

The lab is immediately below the master controls. Enable `n` to use multiple
payloads (default 0 and 70 kg); disabling it evaluates the first case only. `m` is
the maximum number of installed spring slots, not a requirement to fill every slot.
Repeated catalogue parts are permitted. Bounds support 1–8 cases, 1–12 slots and
1–50 requested solutions. Search trials are editable, from 50 to 2000.

`r_h` is a solved output constrained by `r_h min/max` (fresh defaults 50–95 mm).
`r_s` and `nu` are held during Solve; fresh r_s defaults to 12.7 mm. `S_v` and
`S_u` are searched within their visible bounds. Any searches both catalogues and
can select mixed compression/extension cartridges. Existing saved configurations
keep their radii; legacy snapshots without horn bounds migrate to min=max=their
saved r_h, preserving the old fixed-horn behaviour. `p0` is the sum
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

The 1g ground force is (m_s + m_u)g. Its moment is corrected by the individual
component weight moments. For equal links with q_ab=2, alpha=phi0=0, the
equivalent vertical support mass for the ideal fit is
m_c/4 + 0.75 m_femur + 0.25 m_tibia + 0.5 m_knee.
The wheel weight cancels its own contribution to static 1g ground force.

The system `l0` is the virtual span |S-H| at 90 degrees. **Delta-l is the maximum
minus minimum actual cable payout over working travel**, including finite-radius
wrap; it is the piston stroke. The spring table's l0 and le are **physical spring
lengths** at 90 degrees and theta2e. The system pe output lists each payload case's
total force at theta2e. The first-contact/hardstop angle remains theta2e.

Legacy cartridges are checked at the 90-degree preload reference and over
the working travel. Inversion cartridges use the case-specific ranges described
above. The allowed maximum
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

## Search selection clarification — 2026-11-03

Requesting five runs the full chosen trial budget, retains the best sampled
geometry for each distinct part/mask signature, refines the ten best preliminary
candidates, verifies them densely, and returns up to five sorted by worst absolute
residual torque. There is no good-enough threshold or first-five early exit. It is
not exhaustive: rate-based shortlisting and sampled membership/geometry candidates
leave many permutations unevaluated. This update changes the geometry/type search
domains only; no new permutation-enumeration strategy was introduced.
