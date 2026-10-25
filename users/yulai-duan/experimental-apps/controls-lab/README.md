# CAMEL Controls Lab

Yulai Duan with Codex · October 25, 2026 · Analytical teaching tool; hardware gains are not validated.

**[Open the dashboard](https://yulaiduan.github.io/WATERLOO-MTE-ME-CAPSTONE/users/yulai-duan/experimental-apps/controls-lab/)**

The same self-contained [index.html](index.html) can be downloaded and opened in an ordinary browser. No account, installation, server or internet connection is required by the downloaded application. The hosted site is public and has no shared storage or hardware connection.

## Explore and share

1. Read the four-step control overview: goals, MCU coordination, motor drives and measurements.
2. Choose an assumed effective corner mass, natural frequency and damping ratio. Move the Link2 pose to see the leg drawing and joint gains change together.
3. Switch to **Chassis stiffness** to see what four identical leg gains already create in heave, roll and pitch. Adjust the assumed support spacings.

**Export setup / Import setup** exchanges versioned JSON. **Save dashboard** downloads an HTML copy with the current settings embedded. **Reset** returns to the documented defaults, even in a customized saved file. Every person has an independent copy; sharing a URL does not synchronize edits.

Expand **Edit vertical gains** to enter kₕ/cₕ directly. Frequency and damping ratio then become read-only derived values. Invalid edits retain the last valid results and disable saving until corrected. Zero damping is allowed and labelled undamped.

## Defaults and interpretation

Jon V4 DP#3: 300/300 mm links, 20° mounting angle, guide ratio 2, drive ratios 2/2, 200 mm wheel radius, phase zero and source Link2 range 100–165°. Start at 135°, assumed effective dynamic mass 8.75 kg, illustrative natural frequency 2 Hz and damping ratio 0.8. Assumed support-force spacings are 1.2 m front–rear and 0.8 m left–right; they are not confirmed chassis dimensions.

All calculations use SI units and radians internally. The joint gains are local, zero-error, height-only equivalents with current-pose static-load/spring compensation. Wheel coupling and driver-coordinate conversion remain separate. The chassis table is inherited impedance at fixed references, not another PID to add to unchanged leg stiffness. No dynamic chassis/contact simulation or hardware stability claim is made.

## Source and maintenance

The entire app is editable in `index.html`: `<style>` controls layout; `camel-model` contains equations/defaults/schema; `camel-ui` contains drawings and interactions; `launch-setup` holds an optional saved starting setup. Keep the geometry/model IDs versioned when equations or compatibility change.

GitHub Pages publishes `main` from the repository root. Keep this app at its current path to preserve the link. Updates to its source reach the same URL after the Pages build completes. Pages configuration is a repository setting; no extra dashboard framework or custom deployment workflow is required.

Run the numerical checks from this folder with Node installed:

```sh
node verify.cjs
node verify.cjs --write
```

The second command refreshes [verification.json](verification.json) and [default-setup.json](default-setup.json). The self-contained [reference fixtures](reference/README.md) remove dependence on anyone's local output folders. No packages are needed. Publish through the repository's normal contribution log and checks.

## Verification

The suite passes 3,349 assertions: 651 poses compared against Jon's retained source kernel, source finite differences, all five saved gain examples, independent modal matrix checks, scaling, direct-mode inversion, invalid inputs and setup round trips. See [numerical results](verification.json), [browser checks](browser-checks.json) and [context](context/README.md).

Desktop and 390 px phone layouts, all controls, file export/import and saved HTML contents were checked. Automated direct local-file navigation was blocked by the test browser, so an actual double-click launch remains unverified there. The app has no external runtime dependencies. GitHub hosting verification is recorded in the delivery/handoff; analytical agreement does not validate a physical robot.
