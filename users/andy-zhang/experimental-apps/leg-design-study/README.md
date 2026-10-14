# Generalized leg design report

Owner: Andy Zhang. Updated: 2026-10-14. Status: experimental design screening.

Open **[index.html](index.html)** directly in any modern browser, or double-click
**[Open Design Report.cmd](Open%20Design%20Report.cmd)** on Windows. The static
HTML includes its own styles, figures and numerical evidence. It needs no
server, internet connection, Python, Node or running Motion Lab. Keep the
adjacent [16-page PDF](docs/generalized-leg-report.pdf) with the HTML when sharing
the folder. The page also supports the browser's Print / Save as PDF command.

This is the requested offline report, separate from Motion Lab's tooling.
Jonathan's conventions are retained: unequal L2/L3, variable a/b guide ratio,
clockwise mounting alpha, and a lower-link angle above global horizontal through
the wheel centre. It combines the screenshot baseline, two optimization methods,
individual torque profiles, travel/buffer tradeoffs, nine spring fits and one
independently checked motor example. Results are conditional numerical evidence,
not approved hardware or canonical robot validation.

Read [context.md](context.md) for continuation, [design reasoning](docs/generalized-leg-study.md),
[equations and searches](docs/generalized-leg-math.md), [physics](docs/generalized-leg-physics.md),
[impact assumptions](docs/impact-load-envelope.md), [validation](docs/validation.md)
and [revision map](docs/revisions.md). Source base: `6c74cfd`.

## Optional reproduction

Viewing the report requires none of these steps. To reproduce calculations,
use Python 3.13 and Node.js 22 from this folder:

```sh
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt -r requirements-report.txt
node --test tests/design-study.test.js
node scripts/verify_offline_report.cjs
.venv/Scripts/python.exe -m unittest -v test_generalized_leg
.venv/Scripts/python.exe scripts/verify_generalized_leg.py
.venv/Scripts/python.exe scripts/build_design_report.py
```

On macOS/Linux the venv executable is `.venv/bin/python`; those platforms are
not yet tested. The PDF builder uses retained selected evidence rather than
silently rerunning optimization or physics. The analytical Node model has no
third-party dependencies. Python reuses the sibling Wheel Leg Lab's established
`spring_mechanisms.py` force laws, and tests compare its legacy 2D model and
Jonathan's original V2 embedded solver. Retain the full repository for numerical
reproduction; the HTML/PDF can be read separately. No new server endpoints,
Motion Lab menu entries or automatic startup tasks are installed.

The optional browser verifier uses installed Edge/Chrome and Playwright from
the sibling Wheel Leg Lab's locked Node dependencies. It validates local-file
reading with JavaScript disabled, numerical parity, mobile layout and printing.

## Alpha-zero path and inversion follow-up

The separate **[inversion-paths.html](inversion-paths.html)** / **[12-page PDF](docs/inversion-path-report.pdf)**
searches 26.46 million geometry/window combinations with alpha=phi0=0, equal
or near-equal links, 300–350 mm total capacity and the 200 mm wheel radius.
Use **[Open Inversion Report.cmd](Open%20Inversion%20Report.cmd)** for offline viewing.
[Design reasoning](docs/inversion-path-study.md) records the strict symmetry
limit, approximate 350/350 mm 7:4 branch, longer alternatives, explicit
assembly-phase relaxation and unresolved full-inversion wheel clearance.
This follow-up is also static; it adds no Motion Lab controls or services.

Optional new checks and regeneration from this folder:

```sh
.venv/Scripts/python.exe inversion_search.py --output docs/inversion-path-results.json
.venv/Scripts/python.exe -m unittest -v test_inversion_search
.venv/Scripts/python.exe scripts/verify_inversion_geometry.py
.venv/Scripts/python.exe scripts/build_inversion_report.py
node scripts/verify_inversion_report.cjs
```

Source base is `865b5f1`. The renderer consumes retained evidence; it does not
silently run the search. Coarse quality counts and dense selected metrics are
labelled separately. The PDF/HTML regenerate locally from the pinned environment.

## Force and useful-travel ranking

Open **[force-travel.html](force-travel.html)** or **[Open Force Travel Report.cmd](Open%20Force%20Travel%20Report.cmd)**
for the third offline report, with its **[nine-page PDF](docs/force-travel-report.pdf)**.
[The design record](docs/force-travel-study.md) compares 11.48 million new
phase-zero windows, local constrained refinement and separate fixed-indexing
alternatives. Rounded 320/320 mm links with a 9:5 guide give 325/285 mm total/usable
height and 57.83 Nm unassisted equivalent-load hip peak at the 45 kg case.
Indexed 300/300 mm, 2:1 and phase -25 degrees gives an exact 12.5 degree line,
with a wider control range. Full physical inversion remains a packaging issue.

These are ideal force/travel screens, not new spring/motor ratings. Viewing
needs no server or installed runtime and adds no Motion Lab controls.
Optional reproduction commands are in the design record; use the existing
Python 3.13 / Node 22 environments and requirements.
