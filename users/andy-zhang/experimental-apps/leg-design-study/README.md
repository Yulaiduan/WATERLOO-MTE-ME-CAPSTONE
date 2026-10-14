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
