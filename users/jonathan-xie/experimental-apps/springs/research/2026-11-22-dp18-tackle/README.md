# DP18 2:1 moving-pulley spring search — 2026-11-22

Ten appended solutions: mixed S0101–S0105; single S0106–S0110. All21 prior V7
records including S0075 are retained. V6 results and DP18 design workbook remain
byte-identical. Refresh V7 on8770 and choose either 2:1 tackle group.

## Model and constraints

Ideal frictionless remote moving block, two parallel rope legs. A change in horn
cable payout dc gives spring displacement dx=dc/2. Physical spring force Fs=2T,
where T is horn-side rope tension. Thus cable-side stiffness is physical k/4,
and cable reference tension is physical spring preload/2. Energy is conserved:
Fs*dx=T*dc. Block friction, inertia, extra route length constants and varying leg
angles are not modelled. A real compression spring needs a suitable guide/seat
arrangement for that force direction. The larger horn, not the 2:1 ratio alone,
reduces rope force for a specified compensating torque.

DP18 remains alpha0, m6=0, working theta2=120–190 deg; payloads0/70 kg. Exactly
one compression spring active per case, swapped between cases. rh60–70 mm,
rs20 mm, nu0 deg, unloaded inversion to-50 deg, lmax<210 mm. The corrected rule
is the Euclidean edge-to-edge circle gap:

hypot(Su,Sv) - rh - rs >=15 mm.

This is not Sv-rh>=15 mm. The legacy vertical2rs rule remains unchanged for old
records. Search parameterization uses a center radius rh+rs+15+extra and angle,
so the actual circle gap is enforced by construction, then independently checked.
Position bounds: positive Sv<=300 mm, center angle +/-70 deg, extra<=205 mm.

## Results

| ID | Group | Unloaded part | Loaded part | Worst residual Nm | Unloaded rope peak kN | Loaded rope peak kN | Loaded spring peak kN | Working spring stroke mm |
|---|---|---|---|---:|---:|---:|---:|---:|
|S0101|mixed|803-04-239|B63-178|0.010755|2.125|3.807|7.615|34.855|
|S0102|mixed|080-250-300 B|B63-178|0.010775|2.125|3.807|7.614|34.861|
|S0103|mixed|060-250-300 B|B63-178|0.011045|2.124|3.804|7.607|34.932|
|S0104|mixed|080-250-300 B|SZ8020 63 x 178|0.011166|2.123|3.802|7.604|34.963|
|S0105|mixed|803-04-239|SZ8020 63 x 178|0.011166|2.123|3.802|7.604|34.963|
|S0106|single|803-04-239|803-04-305|0.029264|2.114|3.776|7.552|35.444|
|S0107|single|803-04-239|803-04-151|0.029264|2.114|3.776|7.552|35.444|
|S0108|single|803-04-239|803-04-164|0.029264|2.114|3.776|7.552|35.444|
|S0109|single|803-04-154|803-04-305|0.029330|2.113|3.775|7.550|35.468|
|S0110|single|803-04-154|803-04-151|0.029330|2.113|3.775|7.550|35.468|

Unloaded peak includes required inversion; loaded peak covers working travel.
The viewer's tension plot extends over all catalogue-valid displayed angles,
so its wide-angle maximum may exceed these required-range peak values.

S0101 is the lowest nominal error. S0102 uses Swift+Berger/Special Springs,
avoiding FOX-derived force ratings at practically the same residual. S0103 uses
a shorter152.4 mm Swift unloaded spring and178 mm loaded spring, with only
0.01105 Nm peak error. Top mixed loaded springs have essentially zero remaining
rated travel at peak load: analytical fits, not a hardware design margin.
S0106–S0110 are all FOX pairs and retain provisional force limits derived from
marked travel; they are not independently qualified maximum-force ratings.

For S0102: rh60.8299, rs20, Su17.4324, Sv99.0088 mm; circle gap19.7021 mm.
Physical spring rates52.5381 and114 N/mm; cable rates13.1345 and28.5 N/mm.
Working spring travel34.861 mm corresponds to69.721 mm cable payout. Larger
horns reduce loaded rope tension to about3.8 kN versus5.4 kN in the earlier
small-horn direct-drive S0091 case, while physical spring force increases.

## Search and validation

2556 distinct compression envelopes with lmax<210 mm were considered. Thirty
geometry seeds found422 viable unloaded springs.124 screened baseline springs
were refined,1968 pair candidates generated, and35 distinct pairs per supplier
group jointly refined. Rank minimizes the worst peak residual across both cases;
no one-per-supplier quota. Best found bounded search, not a global optimum.

All10 were canonicalized against catalogue data and checked at20001 angles,
with exact cable extrema for force/travel/length/energy and inversion limits.
The existing12806 backend regression assertions passed. A separate synthetic
check establishes exact equivalence between n=2 physical k,Fs and a direct-drive
k/4,Fs/2 model. The actual viewer calculate/shape/inversion/tensionCurve functions
passed22555 cross-checks on all10 records, including rope force division and
physical travel, with <0.001 Nm sampled-vs-dense peak error. All five workbook
sheets reimported/rendered, and the restarted V7 API reports31 records,10 tackle.

Reproduce: python -B scripts/search_dp18_tackle.py, then
python -B scripts/publish_dp18_tackle.py; node scripts/verify_tackle_viewer.cjs.
Publisher APPENDS fresh IDs: do not rerun publication merely to regenerate a
report. Dataset campaign.json, ranked-solutions.csv and validation.json retain
the selected designs/evidence. The prior DP18 direct-drive results remain intact.
All catalogue and mechanism results are nominal static screening; no cable
fatigue, moving-block bearing/shaft load, spring buckling or hardware test.
