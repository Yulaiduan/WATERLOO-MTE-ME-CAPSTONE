# Requirement parameter research

Prepared with Codex for Yulai Duan. Updated 2026-10-03.
Status: proposed simulation inputs supported by literature and analytical checks.

The [research record](../../docs/benchmarks/2026-10-02-requirement-parameter-screen/README.md)
relates the supplied mass, payload, step, slope and range requirements to equal-link
geometry, COM, wheel mass, hip-drum spring force and electrical energy. It retains
public sources, explicit assumptions, a reproducible calculation and compact results.

- With chassis pitch allowed, 235–250 mm links merit the first detailed study for
  a 150 mm step; the 240 mm example has 184 mm upward travel from a 50° ride pose.
- Keeping the chassis horizontal at 35° and a 700 mm wheelbase needs about
  379 mm links before travel reserve; explore 400–430 mm for that separate case.
- A 32.5 kg gross example with a 50 mm hip drum gives a 90% gravity-assist fit of
  272 N preload at the 25° stop and 7.35 N/mm stiffness. This is a static fit,
  not a selected spring or proof of motor adequacy.
- The 0.7–1.2 kg wheel mass interval is a provisional complete-wheel budget.
  Range remains conditional on actual drive, suspension, electronics and battery losses.

Next establish slope attitude requirements, shaft/transmission mapping, real tire
data and component limits before driven simulation. No canonical assets,
controllers, interfaces or validation rules are changed by this contribution.
