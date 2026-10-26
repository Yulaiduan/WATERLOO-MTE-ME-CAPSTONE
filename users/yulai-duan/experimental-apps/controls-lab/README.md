# CAMEL Controls Lab

Yulai Duan with Codex · October 26, 2026 · Analytical teaching tool; hardware gains are not validated.

**[Open the dashboard](https://yulaiduan.github.io/WATERLOO-MTE-ME-CAPSTONE/users/yulai-duan/experimental-apps/controls-lab/)**

The same self-contained [index.html](index.html) can be downloaded and opened in an ordinary browser. No account, installation, server or internet connection is required by the downloaded application. The hosted site is public and has no shared storage or hardware connection.

## Explore and share

1. Read the four-step control overview: goals, MCU coordination, motor drives and measurements.
2. Choose total chassis mass, upper/lower link masses, natural frequency and damping ratio. Each mass has a slider and numeric input. The chassis contribution is divided by four; a labelled pose-dependent linkage inertia estimate is added for gain sizing. Move the Link2 pose to see the leg drawing and joint gains change together.
3. Switch to **Chassis stiffness** to see what four identical leg gains already create in heave, roll and pitch. Adjust the assumed support spacings.

**Export setup / Import setup** exchanges versioned JSON. **Save dashboard** downloads an HTML copy with the current settings embedded. **Reset** returns to the documented defaults, even in a customized saved file. Every person has an independent copy; sharing a URL does not synchronize edits.

Expand **Edit vertical gains** to enter kₕ/cₕ directly. Frequency and damping ratio then become read-only derived values. Invalid edits retain the last valid results and disable saving until corrected. Zero damping is allowed and labelled undamped.

## Defaults and interpretation

Jon V4 DP#3: 300/300 mm links, 20° mounting angle, guide ratio 2, drive ratios 2/2, 200 mm wheel radius, phase zero and source Link2 range 100–165°. Start at 135°, assumed total chassis mass 35 kg (8.75 kg per corner), upper/lower link masses 0 kg each to retain the earlier massless-link baseline, illustrative natural frequency 2 Hz and damping ratio 0.8. Assumed support-force spacings are 1.2 m front–rear and 0.8 m left–right; they are not confirmed chassis dimensions.

All calculations use SI units and radians internally. The joint gains are local, zero-error, height-only equivalents with current-pose static-load/spring compensation. Wheel coupling and driver-coordinate conversion remain separate. The chassis table is inherited impedance at fixed references, not another PID to add to unchanged leg stiffness. No dynamic chassis/contact simulation or hardware stability claim is made.

## Linkage inertia estimate — October 26, 2026

The chassis input includes carried payload and excludes separately entered links and wheels. Each linkage slider is **mass per individual link**, shared by all four identical legs. The displayed physical subtotal is `M_chassis + 4*(m_upper+m_lower)`; it excludes wheels and any other omitted moving assemblies. Include chassis-mounted hardware in chassis mass once.

The scalar gain-sizing mass is `m_eff(q) = M_chassis/4 + m_link,equiv(q)`. It is not total robot mass. Chassis mass remains divided by four regardless of the linkage settings. Uniform 300 mm rods have midpoint COM and centroid inertia `I_i=m_i*l²/12`. In the retained y/z plane, write the hip-relative knee and hub positions as B(q), P(q). For this local heave estimate, hip y stays fixed, hip z=h(q)=-P_z(q), and hub z stays fixed. Hub horizontal travel is unconstrained; its inertia is omitted. Link COM positions in that ground frame are:

```text
r_upper = [B_y/2, h+B_z/2]
r_lower = [(B_y+P_y)/2, h+(B_z+P_z)/2]
J_h = dh/dq
m_link,equiv = sum_i [m_i*||dr_i/dq||² + I_i*(dtheta_i/dq)²] / J_h²
k_h = m_eff*(2*pi*f_n)²
c_h = 2*zeta*m_eff*(2*pi*f_n)
```

Both absolute link angles have `|dtheta_i/dq|=1` under DP#3. The estimate includes link COM translation and link rotation, and is recalculated at each chart pose. The nonnegative equivalent mass is an inertia conversion, not extra kilograms to add to the physical subtotal. The kinetic-energy method follows [Modern Robotics, mass matrix](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-1-3-understanding-the-mass-matrix/) and [rigid-body kinetic energy](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-2-dynamics-of-a-single-rigid-body-part-1-of-2/); these constraints and uniform-rod assumptions are this app's approximation.

This is a local heave sizing estimate with current-pose gravity/spring compensation assumed, not a complete rigid-body/contact model. Nonzero link masses also change gravity compensation; the app does not calculate or validate that feedforward. Wheels, reflected motor/gear inertia, tire deformation, friction and delays are omitted. Actual body roll/pitch frequencies need the full mass/inertia/COM model. The inherited stiffness table still follows the same four-support geometry and must not be treated as an additional body PID. Slider ranges are convenient exploration ranges, not measured hardware bounds; valid typed/imported masses outside them expand the ranges.

Model `camel-controls/2.0.0` exports setup schema 2 with `chassisMassKg` and explicit uniform-rod linkage masses. Schema-1/model-1 setups import by multiplying the old `massKg` corner value by four and setting linkage masses to zero, preserving old response/direct gains. New exports require the updated dashboard. JSON export/import, saved HTML and Reset include all three masses.

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

The suite passes 3,772 assertions: 651 poses compared against Jon's retained source kernel, source finite differences, all five saved gain examples, independent modal matrix checks, scaling, direct-mode inversion, invalid inputs, setup round trips, legacy migration and 131 independent finite-difference rod-energy comparisons. See [numerical results](verification.json), [browser checks](browser-checks.json) and [context](context/README.md).

The prior delivery checked desktop and 390 px phone layouts, all controls, file export/import and saved HTML contents. Current mass-control browser checks are recorded separately in browser-checks.json. Automated direct local-file navigation was blocked by the test browser, so an actual double-click launch remains unverified there. The app has no external runtime dependencies. GitHub hosting verification is recorded in the delivery/handoff; analytical agreement does not validate a physical robot.
