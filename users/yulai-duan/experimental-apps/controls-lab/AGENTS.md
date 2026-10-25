# Controls Lab maintenance

Follow the repository's root AGENTS.md and contribution checks. Read README.md and context/README.md before edits.

This is a standalone HTML analytical guide, not a vehicle simulation or hardware controller. Preserve the DP#3 coordinate contract and explicit assumptions. Do not replace the preset with Jon's startup DP#1 library. New geometry or incompatible setup changes require a version change and source parity checks.

Run `node verify.cjs` after model changes. Inspect responsive layout and affected controls after UI changes. Keep `reference/` frozen to its recorded source; do not change reference values just to make a test pass. Record actual tests and limitations in context. This member app uses workspace validation unless mixed with other repository changes.

Keep the hosted path stable. No backend, telemetry, tokens or shared preset service is included. Retain JSON import/export and offline operation.
