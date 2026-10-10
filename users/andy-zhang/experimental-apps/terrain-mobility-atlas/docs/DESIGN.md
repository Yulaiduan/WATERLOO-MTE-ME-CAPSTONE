# Interface design

## Current simplified iteration, October 2, 2026

The user's follow-up removes the overdesigned atlas presentation. Current UI retains vehicle controls, the terrain map, one selected scenario inspector and compact exports. Hero/rover art, global coverage board, upgrade cards and decorative overlays are removed. Cream/olive/amber, flat borders and readable numbers remain. Desktop uses a 286 px capability sidebar and map/details column; mobile puts the map first and controls below. Six native numeric inputs expose units and range hints, with surfaces, vehicle presets and explicit local saving. Native region and scenario-cell selectors provide keyboard alternatives to map selection. The inspector shows terrain versus capacity, missing evidence and normalized limiting margin. Method/data sources are collapsed details; export is selected-scenario JSON with preview/download/copy. `/workbench/` provides the separate numerical workflow, documented in [workbench design](workbench/DESIGN.md). The first-iteration description below is historical and its removed interface elements no longer describe the current product.

First iteration dated **2026-10-02**. The selected reference is the [PostHog HTML demo](https://code.jiangshu.ai/awesome-design-html/assets/web/design.posthog.html) in [yzfly/awesome-design-html](https://github.com/yzfly/awesome-design-html). Local source: `.references/design.posthog.html`; actual browser reference capture: [posthog-reference.jpg](../evidence/ui-iteration-1/posthog-reference.jpg). Attribution/license: [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Adaptation

The app borrows the reference's olive-neutral canvas, amber primary emphasis, flat borders, small corners, editorial type, and compact workspace chrome. It remains a working engineering atlas: capability controls, map, inspector, and comparison have priority. The header/hero uses original Terrain branding and [rover artwork](../public/design/terrain-rover.svg), with a purple marker accent, rather than reusing PostHog's mascot or logo.

The reference loads Inter and JetBrains Mono. This adaptation intentionally uses **IBM Plex Sans / IBM Plex Mono** for a coherent technical workbench. Font requests are optional Google Fonts CSS; system fallbacks preserve operation when unavailable.

## Tokens

Source of truth: `src/style.css`; map colors also live in `src/main.js`.

| Role | Value |
| --- | --- |
| Canvas | `#eeefe9` |
| Soft surface | `#e5e7e0` |
| Card / document | `#ffffff` / `#fcfcfa` |
| Ink / body / muted | `#23251d` / `#4d4f46` / `#6c6e63` |
| Border / soft border | `#bfc1b7` / `#dcdfd2` |
| Primary / pressed | `#f7a501` / `#dd9001` |
| Marker purple / soft | `#7c44a6` / `#e7d8ee` |
| Pass / near / fail / unknown | `#2c8c66` / `#bd8519` / `#cd4239` / `#74828e` |
| Keyboard focus | 2 px `#1d4ed8`, 3 px offset |
| Corners | Usually 4–6 px |
| Typography | Plex Sans; Plex Mono for engineering labels/numbers |

The body base is 14 px, control labels 12–14 px, and minor metadata generally 11 px or larger. Headings use heavier weight with clear contrast. Numeric labels use tabular spacing where relevant. White/soft cards and one-pixel divisions create structure without dashboard shadows; modest shadows are reserved for menus/dialogs. Status cards use darker text and soft backgrounds rather than placing small pale text directly on status colors.

## Structure and responsiveness

Desktop reads left to right: vehicle envelope → map/coverage/upgrade → selected-cell inspector. The map uses warm parchment and olive geographic outlines. Panels use natural page scrolling rather than shrinking type to force every control into a fixed-height screen. Header Explore/Compare tabs and workspace breadcrumb reflect application mode.

| Width | Layout |
| --- | --- |
| Above 1260 px | Three columns: 280 px controls, flexible map, 310 px inspector; desktop workspace minimum height ~830 px. |
| At/below 1260 px | 270 px controls and flexible map; inspector spans the next row. |
| At/below 900 px | 250 px controls and flexible map; map toolbar stacks; inspector adapts to narrower space. |
| At/below 680 px | Single natural-scroll page, map first, then full controls and inspector; map remains 430 px tall. |
| At/below 370 px | Sliders become one column. |
| At/above 1700 px | Workspace max 1636 px, centered; controls/inspector 300/330 px. |

An intermediate 1440 px rule adjusts spacing. Narrow headers keep named actions rather than replacing every control with an unlabeled icon. At mobile sizes, controls and inspector stay on the page instead of requiring an unimplemented drawer. The map-first order gives location/results context before lower controls.

Browser review found the mobile upgrade strip cramped; it was changed to a grid with the call to action beneath the explanatory text.

## Interaction rules

- Presets/sliders/surface checks update the capability envelope and all evaluated results.
- Environment selection changes scope; it does not change vehicle capability.
- Explore shows fit or selected context layer; Compare shows gained/lost footprint against the session baseline.
- Selecting a context layer exits Compare and shows the corresponding layer; button state remains announced.
- Inspector separates status, margin, individual constraints, primary limitation, and evidence note.
- Legend distinguishes comfortable margin from near-limit and uses text as well as color.
- JSON/CSV exports open a metadata/payload preview dialog, then provide complete download and copy actions. Large JSON previews show a clearly marked 120-line/12,000-character shortened view and file size. Copy failure reveals/selects complete text for manual copying. No upload is involved.
- Save stores the vehicle on the current origin/device; feedback is exposed through status text/toasts.

## Accessibility

Use native buttons, selects, sliders, checkboxes, textarea, and dialog elements. Labels identify numeric controls and sliders reference their explanatory hints. Navigation/layer buttons expose `aria-pressed`; layer menu exposes `aria-expanded` and closes on Escape. Map controls have accessible names. Decorative SVGs, hero art, and map-label markers are hidden from assistive technology. A region select provides a keyboard alternative to map clicking for scenario access.

CSS applies explicit blue keyboard focus, gives range inputs a 24 px interaction height with 16 px thumbs, and enlarges important mobile buttons to 44 px where defined. Status icon/text accompany color. Native modal dialogs provide focus containment; root's browser QA documents the observed keyboard behavior. Reduced-motion CSS suppresses UI transitions/animations; camera fit/fly operations also use zero duration when `prefers-reduced-motion` requests it, rather than marking camera movement essential.

This iteration is not a formal WCAG audit. Layout/accessibility observations and remaining practical limits belong in [VALIDATION.md](VALIDATION.md), with actual screenshots rather than mockup claims.
