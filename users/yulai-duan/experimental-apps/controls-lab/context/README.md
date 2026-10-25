# Controls Lab context

Yulai Duan with Codex · October 25, 2026.

The user requested a simple, adjustable, shareable control-architecture guide. The first delivery was an offline HTML/ZIP. The user then explicitly requested publication on the team's public GitHub repository for hosting.

Implemented: proposed control-flow overview; DP#3 mechanism drawing; frequency/damping or direct vertical-gain input; pose-dependent height gains; four-support inherited heave/roll/pitch impedance; versioned JSON export/import; HTML download with current setup embedded. The HTML is unchanged from the verified offline delivery. The source checker now reads app-local frozen fixtures so teammates can reproduce it in a clean checkout.

Model: `camel-controls/1.0.0`; geometry: `jon-v4-dp3`, source revision `5e52a1220d4ecc9881a80995cbd882df1bfc9be6`. h is downward hip-to-hub drop; q is source Link2 theta2, positive CCW. Gains are local zero-error height contributions assuming current-pose static compensation. Full wheel feedback cross terms, motor reduction/vendor units, real inertias, delays and hardware limits remain outside scope.

Defaults: assumed 8.75 kg effective dynamic corner mass, illustrative 2 Hz and ζ=0.8, 135°, support spacings L=1.2 m/W=0.8 m. Actual physical spring rate is distinct from requested vertical stiffness. The inherited chassis table must not be stacked with another body PID as if it were an independent additional gain.

Verification: [3,349 analytical assertions](../verification.json) and [browser interactions/layout](../browser-checks.json). Source coordinate parity max error 2.22e-16 m; finite-difference Jacobian error 1.87e-11 m/rad. This is not hardware or body-dynamics validation. Local-file browser automation is unavailable; HTTP preview and downloaded-file syntax/embedded values were verified.

Publication uses GitHub Pages' normal main/root source, keeping the app at `users/yulai-duan/experimental-apps/controls-lab/`. No existing Pages site was configured when inspected; no custom domain or access changes to the repository are needed. All site visitors get independent browser settings; the website has no shared database. See the [live link and editing instructions](../README.md).

Next work should preserve the small UI and improve explanations from team feedback. A different geometry or a future dynamic/body-control module needs its own declared model, inputs and verification. Avoid bringing unrelated local project outputs or private material into this public app.
