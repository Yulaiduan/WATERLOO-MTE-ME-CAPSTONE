# VSL v4: Poly Chain belt and sprocket geometry

Prepared for Jonathan Xie, 2026-10-22. Status: verified catalogue dimensions and calculated nominal geometry; proposed hardware combinations.

## Findings and suggested starting points

- Original design: 5 mm pitch, 600 mm pitch-length Poly Chain GT belts on all three stages. The stated L=205.3 mm is a good rounded geometry value. The nominal AB and drive centre distances differ by 0.016692 mm, so they are not mathematically identical.
- Part a near 250: L=249.588860 mm, 36/18 teeth, three 635 mm 5M belts. The alternative L=251.648966 mm uses 52/26 teeth and three 700 mm belts, with more teeth in mesh.
- Part a near 300: L=301.676768 mm, 56/28 teeth, three 815 mm 5M belts.
- Part b near 250: an exact nominal all-catalogued-teeth layout at L=247.954036 mm uses an 8M 50/25 leg pair and two 5M 20/60 drive pairs, giving 3:1 per stage and 9:1 overall. Separate stages can use different pitches; each individual belt and its two sprockets must match.
- Part b near 300: a compact all-catalogued 5M layout gives 3.368421:1 per drive stage with a 0.055028 mm mismatch. For exact nominal geometry, L=297.544843 mm uses 8M 60/30 leg teeth and 22/52 drive teeth; only the 52-tooth size is custom. Alternatively, L=300.497309 mm uses 72/36 leg teeth and stock 31/67 drive teeth; only the 72-tooth size is custom.

Here “catalogued” means present in Gates' stock-product tables, not confirmed inventory at a Canadian distributor. Widths below are concrete ordering examples, not strength selections. Use 15 mm for 5M and 12 mm for 8M examples pending load sizing.

## Solver alignment and calculation

Read the installed VSL v4 README, model context and embedded belt geometry. V4 defines q_ab=ra/rb, q_dc=rd/rc, q_fe=rf/re. AB and CD both span L2; EF spans L3. Therefore L2=L3=L requires three belts to share the same centre distance. The user-written qde is interpreted as the common drive reduction q_dc=q_fe.

Radii are **pitch radii**, the values to enter in VSL, not tooth-tip or flange radii. For tooth count N and pitch p in mm:

    r = p*N/(2*pi)
    delta = R-r
    B(C) = 2*sqrt(C^2-delta^2) + pi*(R+r) + 2*delta*asin(delta/C)

B is belt pitch length; C is shaft centre distance. Solve B(C)=catalogue length numerically, using the exact smooth pitch-line expression rather than the usual quadratic approximation. Require C>R+r to exclude overlapping pitch circles. Actual tooth profiles, flange/hub envelopes and axial packaging still need CAD review.

Digits shown describe the calculation, not manufacturing accuracy or the tensioned as-built length. If AB has n and 2n teeth, a useful exact construction uses drive teeth m and m+n at the same pitch: both pairs have the same radius difference, and B_drive=B_AB-p*(n-m). The mixed-pitch 250 mm example works by the same radial-difference identity.

## Original 205.3 mm proposal

| Pulley | Teeth | Pitch (mm) | Pitch radius (mm) | Example catalogue sprocket for 15 mm belt |
| --- | ---: | ---: | ---: | --- |
| a | 50 | 5 | 39.788736 | P50-5MGT-15-MPB |
| b | 25 | 5 | 19.894368 | P25-5MGT-15-MPB |
| c, e | 18 | 5 | 14.323945 | P18-5MGT-15-MPB |
| d, f | 56 | 5 | 44.563384 | P56-5MGT-15 |

The inferred belt is **5MGT-600**, 120 teeth. Complete US ordering examples are 5MGT-600-09, 5MGT-600-15 and 5MGT-600-25 (9/15/25 mm wide). The given geometry cannot identify which width your colleague intended. A 15 mm example is US product 9270-6052. Europe lists the Carbon version as 5MGTC-600-15, product 9270-06019. Confirm region-specific order code with the supplier rather than treating those product numbers as interchangeable.

| Stage | Belt pitch length | Exact nominal C (mm) | Required pitch-line length at C=205.3 (mm) |
| --- | ---: | ---: | ---: |
| AB, 50/25 | 600 | 205.285253 | 600.029354 |
| CD and EF, 18/56 | 600 each | 205.268562 | 600.062191 |

Thus qab=2 and qdc=qfe=56/18=3.111111; total drive reduction is 9.679012:1. Small-pulley wrap is 168.877 degrees for AB and 163.057 degrees for each drive stage, corresponding to approximately 11.73 and 8.15 engaged teeth. The catalogue belt lengths and tooth counts exist. This verifies the geometric basis, not belt capacity or simultaneous operating tension from a shared adjustment.

## Part a: identical 2:1 pulley combinations

All three belts are identical within each row. Assign a=large, b=small, c=e=small, d=f=large. The reversed placement on AB does not change its belt length.

| ID | L_AB / L_drive (mm) | a / b teeth (pitch radii mm) | c=e / d=f teeth (pitch radii mm) | Belts AB / CD=EF | q per drive stage | Status |
| --- | ---: | --- | --- | --- | ---: | --- |
| A250-small | 249.588860 / 249.588860 | 36 (28.647890) / 18 (14.323945) | 18 (14.323945) / 36 (28.647890) | 5MGT-635-15 / 5MGT-635-15 | 2.000000 | Exact nominal; catalogued teeth |
| A250-more-teeth | 251.648966 / 251.648966 | 52 (41.380285) / 26 (20.690143) | 26 (20.690143) / 52 (41.380285) | 5MGT-700-15 / 5MGT-700-15 | 2.000000 | Exact nominal; catalogued teeth |
| A300 | 301.676768 / 301.676768 | 56 (44.563384) / 28 (22.281692) | 28 (22.281692) / 56 (44.563384) | 5MGT-815-15 / 5MGT-815-15 | 2.000000 | Exact nominal; catalogued teeth |

These rows use catalogue pulley sizes. For A250-small use P18-5MGT-15-MPB and P36-5MGT-15 (or the listed MPB version). For A250-more-teeth use P26-5MGT-15-MPB and P52-5MGT-15. For A300 use P28-5MGT-15-MPB and P56-5MGT-15. Per leg: one a, one b, two c/e, two d/f, and three belts. Consequently the common-pair design uses three small and three large sprockets per leg.

The smallest 18-tooth MPB example has a catalogue maximum bore of 3/8 inch (9.525 mm); the shaft connection can therefore drive the choice of a larger pair. A250-more-teeth has 12.32 teeth in mesh versus 8.67 for A250-small. A300 has 13.34. Do not infer torque capacity from engagement alone.

## Part b: catalogue pulley options first

| ID | L_AB / L_drive (mm) | a / b teeth (pitch radii mm) | c=e / d=f teeth (pitch radii mm) | Belts AB / CD=EF | q per drive stage | Status |
| --- | ---: | --- | --- | --- | ---: | --- |
| B250-stock-exact | 247.954036 / 247.954036 | 50 (63.661977) / 25 (31.830989) | 20 (15.915494) / 60 (47.746483) | 8MGT-800-12 / 5MGT-700-15 | 3.000000 | Exact nominal; catalogued teeth |
| B250-stock-5M-close | 243.981851 / 243.982393 | 56 (44.563384) / 28 (22.281692) | 38 (30.239439) / 90 (71.619724) | 5MGT-700-15 / 5MGT-815-15 | 2.368421 | Near match; catalogued teeth |
| B250-stock-8M-exact | 254.894842 / 254.894842 | 80 (101.859164) / 40 (50.929582) | 27 (34.377468) / 67 (85.307049) | 8MGT-1000-12 / 8MGT-896-12 | 2.481481 | Exact nominal; catalogued teeth |
| B300-stock-5M-close | 301.676768 / 301.621740 | 56 (44.563384) / 28 (22.281692) | 19 (15.119720) / 64 (50.929582) | 5MGT-815-15 / 5MGT-815-15 | 3.368421 | Near match; catalogued teeth |

For B250-stock-exact the leg sprockets are 8MX-50S-12 and 8MX-25S-12; drive sprockets are P20-5MGT-15-MPB and P60-5MGT-15. For B250-stock-8M-exact use 8MX-80S-12, 8MX-40S-12, 8MX-27S-12 and 8MX-67S-12. These 8M Taper-Lock catalogue items also require the appropriate shaft bushings. The larger all-8M example has a 203.718 mm pitch diameter at a, making the mixed-pitch option more compact.

For B250-stock-5M-close use P56-5MGT-15 / P28-5MGT-15-MPB for AB and P38-5MGT-15 / P90-5MGT-15 for each drive. Its centre mismatch is only +0.000542 mm; it is still a numerical near match, not an exact identity. For B300-stock-5M-close use P56 / P28 for AB and P19-5MGT-15-MPB / P64-5MGT-15 for each drive. At the AB nominal centre the drive requires 815.109278 mm, versus its 815 mm belt. Determine whether the shared adjustment can give acceptable measured tension in all belts.

## Part b: custom tooth counts for exact nominal centres

| ID | L_AB / L_drive (mm) | a / b teeth (pitch radii mm) | c=e / d=f teeth (pitch radii mm) | Belts AB / CD=EF | q per drive stage | Status |
| --- | ---: | --- | --- | --- | ---: | --- |
| B250-custom-5M-exact | 251.631817 / 251.631817 | 82 (65.253527) / 41 (32.626763) | 18 (14.323945) / 59 (46.950708) | 5MGT-815-15 / 5MGT-700-15 | 3.277778 | Exact nominal; custom 5M:41; 5M:59; 5M:82 |
| B300-custom-drive-exact | 297.544843 / 297.544843 | 60 (76.394373) / 30 (38.197186) | 22 (28.011270) / 52 (66.208456) | 8MGT-960-12 / 8MGT-896-12 | 2.363636 | Exact nominal; custom 8M:52 |
| B300-one-custom-size-exact | 300.497309 / 300.497309 | 72 (91.673247) / 36 (45.836624) | 31 (39.470426) / 67 (85.307049) | 8MGT-1040-12 / 8MGT-1000-12 | 2.161290 | Exact nominal; custom 8M:72 |
| B300-custom-3to1-exact | 299.477611 / 299.477611 | 98 (124.777475) / 49 (62.388738) | 24 (30.557749) / 73 (92.946487) | 8MGT-1200-12 / 8MGT-1000-12 | 3.041667 | Exact nominal; custom 8M:24; 8M:49; 8M:73; 8M:98 |

B250-custom-5M-exact keeps everything at 5 mm pitch, with custom a=82, b=41, d=f=59 and stock c=e=18. B300-custom-drive-exact keeps a=60, b=30, c=e=22 catalogue sizes and makes two 52-tooth drive sprockets. B300-one-custom-size-exact instead needs only one custom pulley per leg (a=72), with b=36, c=e=31 and d=f=67 available in the 8M catalogue.

Custom means a compatible **Gates 5MGT or 8M Poly Chain tooth form**, with controlled pitch accuracy, runout, material and flanges; tooth count and pitch radius alone are not a manufacturing drawing. Gates does not guarantee full product performance with non-Gates sprockets. A manufacturer-supplied custom sprocket or correctly grooved blank is preferable to assuming a generic HTD tooth form fits.

## Higher ratios within the requested 2-5 interval

The search allowed every tooth-count ratio from 2 through 5. Larger reductions can fit nominal belt lengths closely, but may produce very large pulleys and lose exact equality:

| ID | L_AB / L_drive (mm) | a / b teeth (pitch radii mm) | c=e / d=f teeth (pitch radii mm) | Belts AB / CD=EF | q per drive stage | Status |
| --- | ---: | --- | --- | --- | ---: | --- |
| B250-stock-4to1-close | 253.921869 / 253.914374 | 112 (142.602829) / 56 (71.301415) | 35 (44.563384) / 140 (178.253536) | 8MGT-1200-12 / 8MGT-1280-12 | 4.000000 | Near match; catalogued teeth |
| B300-custom-high-ratio-close | 303.272957 / 303.271171 | 84 (106.952122) / 42 (53.476061) | 33 (42.016905) / 155 (197.352129) | 8MGT-1120-12 / 8MGT-1440-12 | 4.696970 | Near match; custom 8M:84; 8M:155 |

The 4:1 example has a 356.507 mm pitch diameter at d/f; its mismatch is -0.007494 mm. The 4.696970:1 example has a 394.704 mm pitch diameter at d/f and mismatch -0.001786 mm. These are geometric alternatives, not preferred packages. A ratio lying in 2-5 does not mean every real-valued ratio in that interval can be realized exactly with integer teeth and stock belts.

## Adjustment without backside idlers

Jack screws or adjustable links can set centre distance and preload without idlers. However, AB and CD share the same two axes: lengthening L2 tensions both simultaneously. One jack screw cannot independently correct their belt-length tolerances, stiffnesses and desired preloads. Exact nominal equality removes the design mismatch but not those real tolerances. Even identical AB/CD pulley/belt combinations can require attention to matched belts or independent shaft-position provisions.

Keep L2 and L3 equal at the final measured setup if that kinematic constraint is required. Reserve shortening travel to install belts and lengthening travel to tension them. For the 8M/14M family, Gates' manual Table 12 gives 1.8 mm installation shortening and 0.8 mm tension allowance for pitch lengths over 500 through 1000 mm, assuming flanged sprockets can be removed. Installing over retained flanges needs substantially more movement. This 8M/14M table is not claimed as a verified 5M specification: obtain the 5M installation requirement from Gates. Do not force a belt over a flange.

Final operating C depends on actual belt tolerances, elastic extension, required tension and linkage deflection; there is no load-independent exact operating L obtainable from tooth counts alone. Specify the nominal geometry here, provide adjustment, then measure each span's tension. Required loads, RPM, shock/reversal duty, shafts and available axial width are needed to select belt width and pretension. Those strength inputs were not supplied, so no width/capacity certification is made.

## Product-family clarification

“Poly Chain GT” and “PowerGrip GT” are different belt families; “Polygrip GT” appears to conflate their names. Designing around Poly Chain's more limited length range is sensible for this study. It does not prove that every Poly Chain length is available in every cheaper family, width or region. The 5M catalogue specifically pairs its Poly Chain belts with compatible PowerGrip/Poly Chain 5MGT sprockets. Do not generalize that compatibility to HTD or other pitches without checking the manufacturer's exact profiles.

## Sources, search bounds and checks

1. [Gates US Industrial Power Transmission catalogue](https://www.gates.com/content/dam/documents-library/catalogs/power-transmission-catalog.pdf): printed p.2 (8M belts; PDF page 51), p.14 (5M belts; PDF page 63), p.165 (8M 12 mm sprockets; PDF page 214), p.175 (5M 15 mm sprockets; PDF page 224). Downloaded and text-extracted; the relevant 5M and 8M sprocket tables were visually checked. One printed 50-tooth 5M pitch-diameter entry appears inconsistent; all radii here use N*p/(2*pi), not rounded/inconsistent inch values.
2. [Gates 2024 European catalogue](https://www.gates.com/content/dam/documents-library/catalogs/industrial-power-transmission-catalogue-en.pdf): printed p.161 (PDF page 163), visually checked 5MGTC lengths, widths and stock-column entries.
3. [Gates Poly Chain design manual](https://www.gates.com/content/dam/documents-library/catalogs/poly-chain-gt-carbon-drive-design-manual-en.pdf): printed pp.98-105, especially tolerances, tension and adjustment allowances; 8M/14M scope.
4. [Gates 5M product family](https://www.gates.com/us/en/power-transmission/synchronous-belts/poly-chain-synchronous-belts.p.9270-000000-000001.html) and [Gates 815 mm 15 mm product](https://www.gates.com/in/en/power-transmission/synchronous-belts/poly-chain-synchronous-belts.p.9268-000000-000045.v.IN-9270-5625.html). Some regional live pages have inconsistent title/specification fields (the 635 listing returned 425 mm details); the verified catalogue tables control this analysis.

Catalogue size availability checked 2026-10-22; distributor inventory and price not checked. The colleague's actual purchase or selected width cannot be established from geometry.

The bounded search used 5M belt lengths 300,375,425,500,535,600,635,700,815 mm and 8M lengths 640,720,800,896,960,1000,1040,1120,1200,1224,1280,1440 mm. It used the US 15 mm steel/iron 5M and 12 mm 8M catalogue sprocket tables for stock classification. Additional aluminium/regional pulley lines and 14M were not exhaustively searched. Custom small pulleys were screened from 18 teeth in 5M or 22 in 8M up to 112, with large pulleys up to 224; those lower bounds are search choices, not asserted manufacturer minima. Individual centres were 235-315 mm; paired results are within 15 mm of 250/300 with centre mismatch <=0.25 mm. Hence a “no exact all-stock non-2 match near 300” finding applies to this scope only.

Re-run `python screen.py` to recreate full results in the ignored results folder. All selected rows have qab=2 and identical CD/EF stages. Full nominal forward residual and radial-difference identity checks passed below 1e-9 mm. No solver files, user workbooks or reference sources were changed. No commit, push or hardware validation was performed.
