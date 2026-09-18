---
name: html-to-pdf-custom
description: Convert one or more HTML files to pixel-perfect PDFs that are an exact visual copy of how the file renders in a normal browser window — not a stretched or shrunk reinterpretation. Screenshots the natural on-screen render via Puppeteer rather than relying on the file's own @media print rules.
---

# HTML to PDF

Convert one or more HTML files to pixel-perfect PDFs that are an **exact visual copy** of how the file renders in a normal browser window — not a stretched or shrunk reinterpretation.

**Do not rely on the file's own `@media print` stylesheet.** Many decks (e.g. slide-style HTML using `.slide { aspect-ratio: 16/9 }` inside a `max-width` wrapper) define a print block that inflates each slide to a fixed pixel size (e.g. 1920x1080). This looks correct structurally, but if the file's fonts use `clamp(min, Nvw, max)`, the vw-based sizing already maxes out at normal desktop widths — so inflating the container in print mode without the text scaling with it makes every slide look disproportionately shrunk. Screenshotting the natural on-screen render and upscaling resolution avoids this entirely and is the only approach that reliably matches what the user sees in-browser.

## Usage

```
/html-to-pdf-custom [--input <path>] [--output <dir>]
```

- `--input <path>` — path to an HTML file, or a glob pattern (e.g. `*.html`). If omitted, use the most recently modified `.html` file in the current directory.
- `--output <dir>` — directory to write PDFs into. If omitted, write each PDF alongside its source HTML file with the same base name and a `.pdf` extension.

---

## Handling instructions

### Step 1 — Resolve input file(s)

If `--input` was provided, expand globs and collect all matching `.html` files.

If no `--input` was provided, find the most recently modified `.html` file in the current working directory (non-recursive). If none is found, stop and ask the user to specify a path.

Confirm the resolved file list to the user before proceeding.

---

### Step 2 — Identify the repeating page/slide container

Read the file's inline `<style>` block(s) and identify the element that represents one page/slide, in priority order:
1. `.slide`
2. `.page`
3. `section`
4. `body` (single-page documents — treat the whole page as one "slide")

Note its natural on-screen width. If it sits inside a wrapper with `max-width` (e.g. `.deck-wrap { max-width: 1160px }`), that max-width — not any `@media print` override — is the width to render at. This is the size the user actually sees in a browser tab.

Determine the aspect ratio from the container's CSS (`aspect-ratio`, or `width`/`height` under normal screen rules, ignoring `@media print`). Use this to size the final PDF pages (e.g. 16:9 → 1920×1080, A4-ish content → scale proportionally).

Report the detected container selector, natural width, and aspect ratio to the user.

---

### Step 3 — Ensure Puppeteer is available

Check whether Puppeteer is installed by running:

```
node -e "require('puppeteer')"
```

If this fails, install it:

```
npm install puppeteer
```

Run this in a temporary working directory (e.g. `/tmp/html-to-pdf-tmp`) rather than the project root to avoid polluting the project's node_modules. Create the directory if it does not exist.

---

### Step 4 — Screenshot each page/slide at its natural size

Write and execute a Node.js script that:

1. Launches Puppeteer.
2. Sets the viewport to the container's natural on-screen width (Step 2), a generous height, and `deviceScaleFactor: 3` for crisp, high-resolution output.
3. Opens the HTML file via a `file://` URL (absolute path, spaces encoded as `%20`), waiting on `networkidle0`.
4. Calls `page.emulateMediaType('screen')` explicitly — this guarantees the file's `@media print` rules never apply, even if Puppeteer would otherwise default to print media for `page.pdf()`.
5. Selects all matching container elements (`page.$$(selector)`) and calls `elementHandle.screenshot({ path })` on each in turn, saving one PNG per page/slide.

```js
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: NATURAL_WIDTH, height: 900, deviceScaleFactor: 3 });
  await page.goto('file://' + path.resolve(INPUT_PATH).replace(/ /g, '%20').replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
  await page.emulateMediaType('screen');

  const slides = await page.$$(SELECTOR);
  const shots = [];
  for (let i = 0; i < slides.length; i++) {
    const p = path.join(TMP_DIR, `shot-${i}.png`);
    await slides[i].screenshot({ path: p });
    shots.push(p);
  }
  await browser.close();
})();
```

---

### Step 5 — Assemble the screenshots into a PDF

In the same script (or a second pass), build a small wrapper HTML with one `<img>` per page, each filling the page edge-to-edge at the aspect ratio detected in Step 2, then render that wrapper to PDF with Puppeteer:

```js
const wrapperHtml = `<!DOCTYPE html><html><head><style>
  * { margin:0; padding:0; }
  @page { size: ${PAGE_W}px ${PAGE_H}px; margin: 0; }
  .pg { width: ${PAGE_W}px; height: ${PAGE_H}px; page-break-after: always; break-after: page; overflow: hidden; }
  .pg:last-child { page-break-after: auto; }
  .pg img { width: 100%; height: 100%; object-fit: contain; display:block; }
</style></head><body>${shots.map(p => `<div class="pg"><img src="file://${p.replace(/\\/g,'/')}" /></div>`).join('')}</body></html>`;

fs.writeFileSync(wrapperPath, wrapperHtml, 'utf8');

const browser2 = await puppeteer.launch();
const page2 = await browser2.newPage();
await page2.setViewport({ width: PAGE_W, height: PAGE_H, deviceScaleFactor: 1 });
await page2.goto('file://' + wrapperPath.replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
await page2.pdf({
  path: OUTPUT_PATH,
  width: `${PAGE_W}px`,
  height: `${PAGE_H}px`,
  printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 },
});
await browser2.close();
```

Delete the intermediate screenshot PNGs and wrapper HTML from the temp directory after the PDF is written.

---

### Step 6 — Verify before reporting done

Read back at least one generated screenshot (ideally the first slide and one text-dense slide) with the Read tool and visually confirm text is full-size and matches the source file's on-screen appearance — not shrunk, not cropped, not overflowing. Only report success after this check passes.

---

### Step 7 — Report results

For each file processed, report:
- Input file path
- Detected container selector, natural width, and aspect ratio
- Number of pages/slides captured
- Output PDF path

If any file fails, report the error and continue processing remaining files.

---

## Error handling

| Situation | Action |
|---|---|
| No HTML files found | Stop and ask the user to specify `--input` |
| No repeating container found (single-page doc) | Treat `body` as one page, screenshot it whole |
| Puppeteer install fails | Report the npm error and suggest installing Node.js if it is not present |
| Output directory does not exist | Create it before writing |
| File:// path has spaces | Encode spaces as `%20` in the URL passed to Puppeteer |
| Screenshots look shrunk relative to the source | Do not fall back to `page.pdf()` on the original file — re-check that viewport width matches the container's natural (non-print) width and that `emulateMediaType('screen')` was applied |
