const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const root = path.resolve(__dirname, '..');
  const { defaultConfig, pose } = await import(pathToFileURL(path.join(root, 'src/linkage/model.js')));
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  try {
    const page = await browser.newPage({ viewport: { width: 1148, height: 1100 } });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('http://127.0.0.1:4175/force-plots/');
    await page.locator('#wl-summary tr').nth(2).waitFor();
    const rows = () => page.locator('#wl-summary tr').evaluateAll(xs => xs.map(x => [...x.cells].map(c => c.textContent)));
    let values = await rows();
    for (let i = 0; i < 3; i++) {
      const upper = [45, 60, 75][i], a = 30 * Math.PI / 180, b = upper * Math.PI / 180;
      const L = .2 / (2 * (Math.sin(b) - Math.sin(a)));
      const c = defaultConfig(); c.geometry.upperLength = L; c.geometry.lowerLength = L;
      const minimum = 1 / pose(c, Math.PI / 2 - a).verticalJacobian;
      assert.ok(Math.abs(parseFloat(values[i][1]) - L * 1000) < .51);
      assert.ok(Math.abs(parseFloat(values[i][3]) - minimum) < .006);
      let integral = 0;
      const n = 2000, dy = .2 / n;
      for (let j = 0; j < n; j++) {
        const h = 2 * L * Math.sin(a) + (j + .5) * dy;
        const q = Math.acos(h / (2 * L));
        integral += dy / pose(c, q).verticalJacobian;
      }
      assert.ok(Math.abs(parseFloat(values[i][4]) - integral / .2) < .006);
    }
    const setRange = async (id, value) => page.locator(id).evaluate((node, v) => { node.value = v; node.dispatchEvent(new Event('input', { bubbles: true })); }, value);
    await setRange('#wl-radius', 250);
    values = await rows(); assert.equal(values[1][1], '273 mm'); assert.equal(values[1][2], '0.546');
    await setRange('#wl-travel', 250);
    values = await rows(); assert.equal(values[1][1], '342 mm');
    await page.locator('#wl-torque').fill('2'); await page.locator('#wl-torque').dispatchEvent('input');
    values = await rows(); assert.ok(Math.abs(parseFloat(values[1][4]) - 2 * Math.PI / 6 / .25) < .006);
    await page.locator('#wl-projection').check();
    assert.equal(await page.locator('.wl-chart path[stroke-dasharray="5 4"]').count(), 6);
    await page.locator('#wl-legend button').nth(0).click();
    assert.equal(await page.locator('#wl-legend button').nth(0).getAttribute('aria-pressed'), 'false');
    assert.equal(await page.locator('.wl-chart path[stroke-dasharray="5 4"]').count(), 4);
    await page.locator('#wl-legend button').nth(0).click();
    await setRange('#wl-progress', 0);
    const before = await page.locator('.wl-links').first().getAttribute('d');
    await page.locator('#wl-play').click(); await page.waitForTimeout(450);
    const after = await page.locator('.wl-links').first().getAttribute('d'); assert.notEqual(after, before);
    await page.locator('#wl-play').click();
    const paused = await page.locator('.wl-links').first().getAttribute('d'); await page.waitForTimeout(150);
    assert.equal(await page.locator('.wl-links').first().getAttribute('d'), paused);
    await setRange('#wl-progress', 100);
    assert.ok((await page.locator('.wl-theta').nth(2).textContent()).includes('75.0'));
    await page.locator('#wl-play').click(); await page.waitForTimeout(6200);
    assert.equal(await page.locator('#wl-play').textContent(), 'Animate cycle');
    assert.ok((await page.locator('.wl-theta').nth(2).textContent()).includes('30.0'));
    const output = path.join(root, 'artifacts/force-plots'); fs.mkdirSync(output, { recursive: true });
    await setRange('#wl-radius', 200); await setRange('#wl-travel', 200);
    await page.locator('#wl-torque').fill('1'); await page.locator('#wl-torque').dispatchEvent('input');
    await page.locator('#wl-projection').uncheck(); await setRange('#wl-progress', 50);
    await page.screenshot({ path: path.join(output, 'desktop.png'), fullPage: true });
    await page.setViewportSize({ width: 360, height: 1000 }); await page.waitForTimeout(100);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.screenshot({ path: path.join(output, 'mobile.png'), fullPage: true });
    for (const [radius, travel, low, high] of [[250,50,40,85],[150,350,10,65]]) {
      await setRange('#wl-radius', radius); await setRange('#wl-travel', travel);
      await setRange('#wl-low', low); await setRange('#wl-high', high);
      await setRange('#wl-progress', 100);
      assert.equal(await page.locator('path').evaluateAll(ps => ps.some(p => /NaN|Infinity/.test(p.getAttribute('d') || ''))), false);
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    }
    const external = [];
    const offline = await browser.newPage();
    await offline.route('**/*', route => {
      if (route.request().url().startsWith('http://127.0.0.1:4175/')) return route.continue();
      external.push(route.request().url()); return route.abort();
    });
    await offline.goto('http://127.0.0.1:4175/force-plots/');
    await offline.locator('#wl-summary tr').nth(2).waitFor(); assert.deepEqual(external, []);
    assert.deepEqual(errors, []);
    console.log('PASS: force and travel averages agree with existing linkage Jacobian; radius/travel/torque controls; projection and visibility; animation/pause/scrub/full cycle; 360px and extreme geometry; offline page; no browser errors.');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
