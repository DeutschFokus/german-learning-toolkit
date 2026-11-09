// Prints the learning-profile form and turns it into a fillable PDF.
//
//   node render_form.cjs <form.html> <output.pdf> [field-font.ttf] ["title|subject|author"]
//
// 1. Splits the #flow blocks into fixed A4 pages (a section is never split).
// 2. Measures every element marked with data-field / data-kind.
// 3. Prints with Chromium, then uses pdf-lib to place a real form field
//    (text, multi-line text, check box or radio button) exactly over each
//    drawn box. Fields have no border or background of their own, so the
//    printed design stays visible underneath — on screen and on paper.

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');
const fontkit = require('@pdf-lib/fontkit');

(async () => {
  const [input, output, fontPath = '', meta = ''] = process.argv.slice(2);
  if (!input || !output) {
    console.error('usage: node render_form.cjs <form.html> <output.pdf> [font.ttf] [meta]');
    process.exit(2);
  }

  const browser = await chromium.launch();
  let layout;
  let pdfBytes;
  try {
    const page = await browser.newPage({ viewport: { width: 794, height: 1123 } });
    await page.emulateMedia({ media: 'print' });
    await page.goto('file://' + path.resolve(input), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);

    layout = await page.evaluate(() => {
      const flow = document.getElementById('flow');
      const blocks = Array.from(flow.children);
      const pages = [];
      const problems = [];
      const newPage = () => {
        const sheet = document.createElement('div');
        sheet.className = 'page';
        const inner = document.createElement('div');
        inner.className = 'page-inner';
        const foot = document.createElement('div');
        foot.className = 'page-foot';
        sheet.append(inner, foot);
        document.body.appendChild(sheet);
        pages.push(sheet);
        return inner;
      };
      const overflows = (el) => el.scrollHeight > el.clientHeight + 1;

      let inner = newPage();
      for (const block of blocks) {
        inner.appendChild(block);
        if (overflows(inner) && inner.children.length > 1) {
          inner.removeChild(block);
          inner = newPage();
          inner.appendChild(block);
        }
        if (overflows(inner)) {
          const label = block.querySelector('h2, h1')?.textContent || block.className;
          problems.push(`"${label}" is taller than one page — split it into two sections.`);
        }
      }
      flow.remove();

      const footer = document.body.dataset.footer || '';
      pages.forEach((sheet, i) => {
        sheet.querySelector('.page-foot').innerHTML =
          `<span>${footer}</span><b>${i + 1} / ${pages.length}</b>`;
      });

      const fill = pages.map((sheet) => {
        const inner = sheet.querySelector('.page-inner');
        const top = inner.getBoundingClientRect().top;
        const bottom = inner.lastElementChild.getBoundingClientRect().bottom;
        return Math.round(((bottom - top) / inner.clientHeight) * 100);
      });

      const fields = [];
      pages.forEach((sheet, index) => {
        const pr = sheet.getBoundingClientRect();
        sheet.querySelectorAll('[data-field]').forEach((el) => {
          const r = el.getBoundingClientRect();
          fields.push({
            page: index,
            name: el.dataset.field,
            kind: el.dataset.kind,
            value: el.dataset.value || null,
            x: r.left - pr.left,
            y: r.top - pr.top,
            w: r.width,
            h: r.height,
            pw: pr.width,
            ph: pr.height,
          });
        });
      });
      return { pages: pages.length, fill, fields, problems };
    });

    if (layout.problems.length) {
      throw new Error(layout.problems.join('\n'));
    }
    pdfBytes = await page.pdf({ preferCSSPageSize: true, printBackground: true, tagged: true });
  } finally {
    await browser.close();
  }

  const doc = await PDFDocument.load(pdfBytes);
  if (doc.getPageCount() !== layout.pages) {
    throw new Error(`Expected ${layout.pages} pages but Chromium printed ${doc.getPageCount()}.`);
  }
  doc.registerFontkit(fontkit);
  const font = fontPath
    ? await doc.embedFont(fs.readFileSync(fontPath), { subset: false })
    : await doc.embedFont(StandardFonts.Helvetica);

  const form = doc.getForm();
  const ink = rgb(0.09, 0.21, 0.36);
  const groups = new Map();
  const counts = { text: 0, check: 0, radio: 0 };

  for (const f of layout.fields) {
    const pdfPage = doc.getPage(f.page);
    const { width: PW, height: PH } = pdfPage.getSize();
    const sx = PW / f.pw;
    const sy = PH / f.ph;
    const rect = {
      x: f.x * sx,
      y: PH - (f.y + f.h) * sy,
      width: f.w * sx,
      height: f.h * sy,
      borderWidth: 0,
      borderColor: undefined,
      backgroundColor: undefined,
      textColor: ink,
    };
    if (f.kind === 'text' || f.kind === 'multiline') {
      const field = form.createTextField(f.name);
      if (f.kind === 'multiline') field.enableMultiline();
      field.addToPage(pdfPage, { ...rect, font });
      field.setFontSize(f.kind === 'multiline' ? 9 : 9.5);
      counts.text += 1;
    } else if (f.kind === 'check') {
      form.createCheckBox(f.name).addToPage(pdfPage, rect);
      counts.check += 1;
    } else if (f.kind === 'radio') {
      let group = groups.get(f.name);
      if (!group) {
        group = form.createRadioGroup(f.name);
        groups.set(f.name, group);
        counts.radio += 1;
      }
      // pdf-lib always paints radio buttons with a background, which would hide
      // the printed circle — so the field draws the same circle itself.
      group.addOptionToPage(f.value, pdfPage, {
        ...rect,
        backgroundColor: rgb(1, 1, 1),
        borderColor: rgb(0.48, 0.525, 0.59),
        borderWidth: 1,
      });
    } else {
      throw new Error(`Unknown field kind "${f.kind}" for ${f.name}`);
    }
  }
  form.updateFieldAppearances(font);

  const [title = '', subject = '', author = ''] = meta.split('|');
  doc.setTitle(title, { showInWindowTitleBar: true });
  doc.setSubject(subject);
  doc.setAuthor(author);
  doc.setKeywords(['German', 'Deutsch', 'learning profile', 'questionnaire']);
  doc.setCreator(author || 'German Learning Toolkit');

  fs.writeFileSync(output, await doc.save({ updateFieldAppearances: false }));
  console.log(
    `✔ ${path.relative(process.cwd(), output)} — ${layout.pages} pages, ` +
      `${counts.text} text fields, ${counts.check} tick boxes, ${counts.radio} single-choice questions`
  );
  console.log(`  page fill: ${layout.fill.map((p, i) => `p${i + 1} ${p}%`).join(' · ')}`);
})().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
