// Renders an HTML file to PDF with headless Chromium (via Playwright).
//
//   node render.cjs <input.html> <output.pdf>
//
// Page size, margins, footers and page breaks all come from the CSS
// (@page rules), so this script only has to print. `outline: true` makes
// Chromium write a bookmark for every heading; build.py later replaces
// those bookmarks with clean, numbered titles.

const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [input, output] = process.argv.slice(2);
  if (!input || !output) {
    console.error('usage: node render.cjs <input.html> <output.pdf>');
    process.exit(2);
  }

  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto('file://' + path.resolve(input), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({
      path: output,
      preferCSSPageSize: true,
      printBackground: true,
      outline: true,
      tagged: true,
    });
  } finally {
    await browser.close();
  }
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
