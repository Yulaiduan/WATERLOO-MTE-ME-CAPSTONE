# DP18 spring search — 2026-11-22

The operational V7 library is `../../v7-spring-solutions.xlsx`: S0075 reference,
S0081–S0090 mixed supplier and S0091–S0100 single supplier. V6's workbook and
V7's design/config library remain byte-identical. V7 storage is now separate.

DP18 is read from v7-configs.xlsx using its supported library reader. Its saved
m6=0, alpha=0 deg and theta2=120–190 deg are used. Payloads are 0 and70 kg total.
All candidates have exactly one compression spring enabled per payload case,
swapped between cases, common geometry, fixed per-spring installed preload,
r_h40–42 mm, r_s25.4 mm, nu0 deg, free/rated max length strictly below210 mm.
Unloaded spring limits are checked through -50 deg inversion; loaded spring
limits cover120–190 deg. The previous clearance rule is Sv-r_h>=2rs=50.8 mm,
not a fixed10 mm gap. Su bounds +/-120 mm; Sv<=300 mm. No nesting requirement.

## Ranking and evidence

Minimize the worst peak absolute residual across both payload cases. Mixed means
two different suppliers; single means both springs from the same supplier. Every
single-supplier top-ten result found is Swift; one result per supplier is not
forced. Distinct purchase pairs may share rates and residual curves but differ
in length or dimensions. These are best found in a bounded search, not proven
global optima.

The search screened2556 distinct catalogue envelopes from MC/MD/ME-excluded,
ST, BT, MI, SW, RF and DM data; only compression entries were eligible. Thirty
geometry seeds screened245 viable unloaded springs.106 screened baseline
springs were refined,1596 pair candidates recorded, and35 distinct pairs per
group jointly refined. Final20 canonical records passed20001-angle torque
verification, continuous cable-travel extrema, rated force/travel/length/energy,
payload masks and inversion/clearance tests. Existing backend verification also
passed12806 numerical/catalogue assertions. All five exported workbook sheets
were imported and rendered for review. No physical or fatigue test is claimed.

FOX entries remain provisional: their force ceiling is k times marked travel,
not an independently published force rating. V7 now imports MD/RF/DM as well as
the prior sources. RF has0.5 mm reserve below marked travel, including preload;
this is a screening assumption, not a manufacturer qualification.

## Top 10 per group

| ID | Group | Rank | Unloaded part | Loaded part | Unloaded peak Nm | Loaded peak Nm | Loaded rope peak kN |
|---|---|---:|---|---|---:|---:|---:|
|S0081|mixed|1|060-250-175 B|803-04-242|0.9217|1.1723|5.785|
|S0082|mixed|2|080-250-175 B|803-04-242|0.9217|1.1723|5.785|
|S0083|mixed|3|060-250-150 B|803-04-173|1.3459|1.3459|5.684|
|S0084|mixed|4|060-250-175 B|803-04-243|1.5354|1.6319|5.892|
|S0085|mixed|5|060-250-175 B|803-04-174|1.5354|1.6319|5.892|
|S0086|mixed|6|080-250-175 B|803-04-243|1.5354|1.6319|5.892|
|S0087|mixed|7|080-250-175 B|803-04-174|1.5354|1.6319|5.892|
|S0088|mixed|8|96485K249|080-250-325 B|1.8051|1.8051|5.540|
|S0089|mixed|9|803-04-166|080-250-325 B|1.9302|1.9302|5.526|
|S0090|mixed|10|96485K249|080-250-350 B|2.0495|2.0495|5.682|
|S0091|single|1|080-250-125 B|080-250-275 B|0.1591|0.1591|5.396|
|S0092|single|2|060-250-150 B|080-250-325 B|0.6142|0.6142|5.584|
|S0093|single|3|080-250-125 B|080-250-250 B|0.8426|0.8427|5.308|
|S0094|single|4|060-250-175 B|080-250-375 B|0.9217|1.1723|5.785|
|S0095|single|5|080-250-175 B|080-250-375 B|0.9217|1.1723|5.785|
|S0096|single|6|060-250-150 B|080-250-300 B|1.2005|1.2005|5.412|
|S0097|single|7|080-250-125 B|080-250-300 B|1.2272|1.2272|5.488|
|S0098|single|8|060-250-150 B|060-250-350 B|1.3459|1.3459|5.684|
|S0099|single|9|060-250-150 B|070-250-350 B|1.3459|1.3459|5.684|
|S0100|single|10|060-250-150 B|080-250-350 B|1.3459|1.3459|5.684|

S0091 retains S0075's Swift080-250-125 B /080-250-275 B pair. New geometry is
rh40, rs25.4, Su24.2792, Sv90.8 mm. Both springs have free length203.2 mm;
rates21.89085 /48.15988 N/mm. Reference90-deg preload forces1299.015 /2797.956 N.
The peak rope tensions are2.910 kN unloaded including inversion and5.396 kN
loaded over the working range. All20 loaded peaks span5.308–5.892 kN. These
numbers are rope tension, not pulley bearing radial load or qualified cable WLL.

Reproduce with `python -B scripts/search_dp18.py`, then
`python -B scripts/publish_dp18.py` (requires numpy/scipy and bundled artifact
writer). The publisher remaps catalogue entries, verifies limits, preserves V6
and DP18 hashes, retains S0075, and assigns the same fresh V7 ID range from the
V6 nextId. It intentionally replaces this V7 campaign; later manually added V7
solutions should be backed up before rerunning. Dataset: campaign.json;
compact review: ranked-solutions.csv; checks: validation.json. No commit or push.
