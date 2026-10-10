# Third-party notices

The separate Terrain Workbench also adapts the PostHog reference's cream canvas, olive text, amber actions and flat bordered panels. The reference and MIT terms below cover this additional use. Its engineering plots, mechanism sketch and calculation graph are app-specific; the workbench uses no PostHog logo or mascot.

## PostHog design reference

The Terrain interface adapts visual patterns from the [PostHog HTML demo](https://code.jiangshu.ai/awesome-design-html/assets/web/design.posthog.html), in [yzfly/awesome-design-html](https://github.com/yzfly/awesome-design-html). Source reference is preserved at `.references/design.posthog.html`; upstream license/attribution is preserved at `.references/awesome-design-html-LICENSE.txt`.

This is an independent Terrain application. PostHog is the selected style reference; no corporate affiliation or endorsement is claimed. Terrain branding and rover artwork are original app assets. The third-party demo is not an official PostHog specification.

The reference repository states its web references are based on [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md), licensed under MIT. Its iOS references draw inspiration from [Meliwat/awesome-ios-design-md](https://github.com/Meliwat/awesome-ios-design-md) and published app designs; no iOS reference is used in this atlas.

### MIT License

Copyright (c) 2026 云中江树 (yzfly)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Geographic context

`public/countries.geojson` uses [Natural Earth 1:110m administrative country outlines](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson). Natural Earth data is [public domain](https://www.naturalearthdata.com/about/terms-of-use/). Geographic context does not imply geographic sourcing of the illustrative terrain parameters. The map also displays attribution.

## Runtime dependencies and fonts

The animated wheel-leg force page bundles D3 7.9.0 from `https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js`. Copyright 2010–2023 Mike Bostock. Its ISC license is retained at `public/force-plots/D3-LICENSE.txt` alongside the saved runtime.

MapLibre GL JS is BSD-3-Clause and Vite is MIT, as declared by the installed packages. Their upstream licenses remain in installed package distributions; this notice does not replace them. See the corresponding dependency package LICENSE files. Optional IBM Plex font requests use Google Fonts, with system-font fallbacks. Font assets and applicable licenses remain provided by their upstream distributors; no local font binaries are bundled here.

## Separate terrain evidence

Existing `data/terrain/` sources are not connected to this interface runtime. Their source-specific provenance and limitations are documented in [Terrain data and profile specification](docs/terrain-data-and-profile-specification.md) and accompanying provenance JSON files. Preserve source notices when distributing those evidence assets.
