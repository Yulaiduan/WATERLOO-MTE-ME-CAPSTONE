# Small pulley screening for VSL v6

Jonathan Xie / Codex, 2026-11-11. Preliminary supplier research and analytical screening. No hardware selection or fatigue qualification. The supplied slide and 3800 N cable envelope are inputs, not independently validated VSL dynamic results.

## Recommendation

Reject SG20 for the proposed 5.37 kN radial load. The best compact lead found is Allen A3343-XHL (28.35 mm OD, 7.25 mm bore), but its 1250 kg figure is explicitly listed as **breaking load**; a suitable repeated radial working-load rating has not been established. Ronstan RF48000HL (40 mm OD) is the strongest clearly working-rated commercial option found in this search. A custom sheave with an appropriately sized needle bearing is another route if diameter dominates packaging.

There is no verified product from this search satisfying all three requirements simultaneously: under 30 mm OD, 6 mm Dyneema with acceptable cyclic bend life, and at least 5.37 kN repeated radial load. The rope-bending constraint can dominate even when the bearing is strong enough.

## Sync with the local v6 state

Read-only sources: ../../v6-spring-solutions.xlsx; ../../../vsl-solver/v6/README.md; ../../../vsl-solver/context/README.md; ../../../vsl-solver/v6/spring_lab.py; ../../../vsl-solver/v6/v6-springlab.html. Paths in this paragraph are relative to this research directory. The snapshot contains 30 saved solutions; most recent entries S0027-S0035 were saved November 3. Full selected geometry/parts are in screening-results.json.

The newer saved group uses L2=L3=280 mm, alpha=20 deg, working theta2=105-170 deg, r_s=14.2875 mm, and r_h about 82.80-120.00 mm. Representative stored results:

| Solution | r_h mm | S_v mm | S_u mm | Saved worst residual Nm | Spring parts |
|---|---:|---:|---:|---:|---|
| S0027 | 92.3953 | 131.1376 | 12.9895 | 0.4549 | 2006N511 + 96485K229 |
| S0033 | 93.9115 | 126.5983 | 33.5163 | 0.8649 | 9654K851 or 96485K315, case dependent |
| S0035 | 95.6949 | 183.9555 | 82.5372 | 1.6724 | 9654K851 + 96485K229 |

For S0027, compression spring 2006N511 has k=4.44822 N/mm, OD=45 mm, free length=300 mm, rated max force=800.68 N. Added payload spring 96485K229 has k=7.35533 N/mm, OD=73.8124 mm, free length=254 mm, rated max force=1089.81 N. The stored masks enable the first spring at zero payload and both at 70 kg total payload.

These saved residuals belong to their saved model/context. The November 5 v6 update introduces distributed leg masses and touchdown projection. Current fresh defaults are chassis 35 kg, payload 0, leg component inputs 2.5/2/1.5/2 kg and r_s=14.2875 mm. They are not the same as the user's 13.5 kg sprung mass per leg or the saved legacy m1=11.25 kg snapshots. Use these snapshots as geometry and preliminary spring references, not confirmation of the user's 1670 N or 3800 N peak. The distributed-mass fit includes individual component gravity moments; scaling sprung mass alone need not scale total cable force exactly.

V6 already accounts for tangent span plus finite-radius wrap, and checks spring travel, force, length and energy. Its saved 105-170 deg feasibility does not certify 240 deg. Extend the selected case's actual full travel, check internal extrema, all individual spring limits (including disabled cartridges), retained cable routing, slack and interference, and include self-righting dynamics before freezing hardware. The touchdown impulse has no resolved force peak in this model.

## Load and bearing interpretation

With equal span tensions T and cable turning angle beta, R=2*T*sin(beta/2). Thus 3800 N gives 5374.01 N at 90 deg and 7600 N at 180 deg. Equivalently, if alpha is the included angle between the two outgoing tension vectors, R=2*T*cos(alpha/2). State which angle is being used. The maximum tension and maximum angle need not occur at the same pose; check R(theta), not only separate extrema.

Exact sprung-mass scaling: (13.5+70/4)/13.5=2.296296; 1670 N times this is 3834.81 N. The user's rounded 3800 N is within 1%. No impact multiplier is assumed here.

[LILY SG20](https://www.lily-bearing.com/products/sg20/) lists 6x24x11 mm, dynamic C=3400 N, static C0=1700 N and an 8 mm guide-rail diameter. [KTAI's SG table](https://www.ktaiballbearing.com/product/sg-series-track-roller/) independently lists C=3.4 kN and C0=1.7 kN. No direct uxcell rating was established; these are similar-product benchmarks, not certification of the Amazon item. Amazon was inaccessible through the research tool. SG designations can differ by supplier, and these products are rail guides with a Gothic-arch profile rather than purpose-designed rope sheaves.

At 5374 N, C0/R=0.316 and R/C0=3.16. A dynamic rating is a fatigue-life reference, not a permissible instantaneous load. The static rating concerns contact stress/permanent indentation, not ultimate rupture. [JTEKT's bearing guidance](https://www.jtekt.co.jp/products/bearing/en/support/bearing-knowledge/5-5000.html) explains the 0.0001 rolling-element-diameter deformation convention and static safety factors. SG20 is unsuitable by this screen even if it does not fracture on first loading. No useful service-life prediction follows from ignoring the static overload.

As an explicitly proposed ball-bearing screening target, s0=2 at the supplied radial load requires C0>=10.75 kN. Shock/duty requirements can require more; JTEKT distinguishes ball and roller bearing factors. Do not transfer s0=2 blindly to an impact-loaded needle bearing.

## Product comparison

Supplier kg load entries below are interpreted as kgf and converted using 9.80665 N/kgf. Working, static bearing and breaking ratings have distinct meanings.

| Candidate | Diameter / bore / width mm | Published load | Assessment |
|---|---|---|---|
| SG20 equivalent | 24 / 6 / 11 | C=3.4 kN; C0=1.7 kN | Reject for 5.37 kN radial. |
| [Allen A3343-XHL](https://allenbrothers.co.uk/collections/sheaves/products/xhl-cassette-2) | 28.35 / 7.25 / 13 | 1250 kg breaking =12.26 kN | Best under-30 mm lead. Confirm repeated radial working limit, required pin/support/clamping, rope groove and 6 mm line fit. Manufacturer marketing also describes static-load survival up to 1250 kg; do not interpret it as a rated working load. |
| [Allen A4986-8](https://www.allenbrothers.co.uk/product/a3342-high-load-ss-sheave-with-double-row-ball-bearing/) | 25 / 8 / 8 | 750 kg breaking =7.35 kN | Only 1.37 times the applied radial load to published break. Reject for this duty. A4986-6 has 6 mm overall width, not a 6 mm rope specification. |
| [Allen A2030XHL complete block](https://allenbrothers.co.uk/collections/30mm-dynamic-blocks/products/a2030xhl-black-extreme-high-load-black) | marketed 30 mm sheave; complete housing larger; lashing attachment | 500 kg MWL=4.90 kN; 1250 kg break | Does not establish 5.37 kN working capability for the complete unit. Does not provide an exposed >=5 mm shaft bore. Do not transfer its rating to a bare cassette. |
| [Ronstan RF48000HL](https://www.ronstan.com/s40-bb-sheave-hhl-od40mm-x-id8-2mm-x-15-5mm.html?___store=row) | 40 / metric page says 6 / catalogue width15.5 | Current metric page 1000 kg MWL=9.81 kN | Best working-rated commercial lead found; needs larger package. Hub must be clamped between side plates against rotation/opening to achieve full MWL. |
| Custom sheave + IKO TAF121916 | Bearing only: 12 under rollers /19 OD /16 width | C=9.25 kN; C0=11.2 kN | Bearing architecture to investigate, not a rated finished pulley. C0/R=2.08. Requires hardened ground shaft raceway or appropriate inner ring, adequate housing support, lubrication, seals and axial retention. Impact factor may demand a larger bearing. |

Ronstan's US page gives 1/4 inch bore while its metric page says 6 mm; the URL and some dealers say 8.2 mm. Obtain the current drawing before sizing a shaft. Its older official Series40 update gives 1500 kg sheave MWL; this report conservatively uses the current product page's lower 1000 kg. Both are above 5.37 kN, but exact load application and installation still need confirmation. [Ronstan definitions](https://www.ronstan.com/us/supportoverview-us/policy-support/definitions) separate working and break loads. Match the supplier's radial load convention to the joint load; do not confuse line tension with sheave resultant.

IKO values come from its [dimension/interchange catalogue](https://ikont.com/download/dimension-and-interchange-table/?masterkey=606e1adc7e652&wpdmdl=4420), PDF page35, printed page66. This is not permission to cut a groove into the bearing outer ring. A separate supported sheave body needs enough material between its bore and groove root. The inner-ring version TAFI91916 has a 9 mm shaft bore and 19 mm OD in the same table; confirm its exact assembled rating and mounting drawing when selecting it.

## Rope radius and fatigue

For VSL's zero-thickness cable, use the effective rope-centreline radius. First approximation: r_s=groove_root_radius + loaded_rope_diameter/2. This ignores flattening/contact deformation and requires a suitable groove profile.

Using the user's SG20 groove depth 1.75 mm and 6 mm rope, groove-root diameter is 24-2*1.75=20.5 mm, pitch diameter is approximately26.5 mm, and effective r_s=13.25 mm. This is only about7.3% below the saved r_s14.2875 mm, not a move to r_s10 mm. The outside envelope including rope is larger than the metal wheel OD. A Gothic-arch rail groove can have inappropriate rope support even if its nominal width fits.

[Marlow's flex-fatigue FAQ](https://www.marlowropes.com/services/faqs/) recommends an8:1 sheave-to-rope diameter ratio for most ropes including Dyneema. That implies about48 mm for6 mm rope. SG20 is only3.42:1 based on groove-root diameter, or4.42:1 based on the approximate rope pitch diameter. Both are below8:1. The exact diameter convention should be agreed with the rope supplier. Marlow also reports static D12 samples can break at the sheave below5:1; that is not a quantitative derating curve for this specific rope.

A smaller pulley can improve geometric linearity while reducing rope strength and cyclic life. Larger rope can worsen bending severity at fixed wheel diameter. Use a specific rope/construction/termination rating and bend-over-sheave test conditions. The slide's2100 kg MBL and420 kg SWL imply20.59 kN and4.12 kN; the latter is only1.08 times3800 N before bend and termination effects. Premium constructions can differ substantially: [Samson AmSteel-Blue](https://www.samsonrope.com/mooring/amsteel--blue) lists7700 lb minimum strength for nominal1/4 inch, approximately34.25 kN. This does not make a tight bend automatically acceptable.

Steel wire also needs construction-specific minimum sheave ratio and fatigue screening; it is not a simple remedy for a small pulley. Refer to the actual cable manufacturer's guidance rather than relying only on straight breaking strength.

## Shaft and slide corrections

At5374 N, a smooth6 mm pin has nominal shear stress190 MPa in single shear or95 MPa in symmetric double shear. A5 mm pin has274 or137 MPa. Bending, threads in shear planes, bearing fit and cheek bearing stress can dominate. As an illustration only, a simply-supported6 mm pin with16 mm support span and a central point load would have about1014 MPa bending stress. A real distributed bearing load changes that result; a pure-shear calculation cannot qualify the joint. Use close double-sided support and verify actual load distribution, material yield/fatigue and clearances.

The slide uses800 MPa as a rupture-strength input;0.6 times this is not a demonstrated allowable cyclic design stress. The4 mm line's written diameter is also a typo (it shows5 mm). In the steel-rope line,7480/5=1496 N, approximately336 lb, not6580 lb. 3800 N is approximately854 lbf. Finally,240 deg is equivalent to-120 deg modulo360, not-60 deg; if the latter uses a different leg/knee reference, explicitly map that convention before changing the VSL travel limit.

## Design decision and validation

Prioritize (1) a rope-qualified bend radius, (2) measured/validated full-motion radial envelope, and (3) a working-rated sheave and supported shaft. Refit r_h,S_v,S_u and spring choices at the actual rope-centreline r_s. Keep A3343-XHL as the compact supplier-inquiry candidate; use RF48000HL as the documented higher-capacity size comparison; evaluate a custom needle-bearing sheave only if smaller packaging justifies its design and test work. A48 mm rope bend target is a sensible initial comparison case, not a claim that every6 mm rope must use that exact diameter.

Validation: the companion script reads the workbook with standard-library XML, records its SHA256, extracts all30 solutions and the latest9 geometry/spring snapshots, and checks the force/radius arithmetic. It does not run the SciPy optimizer; bundled Python lacked SciPy during an attempted read through spring_store, so standalone read-only extraction was used. No solver, catalogue, saved solution or existing workbook was changed. No physical or canonical robot test, commit or push was performed.
