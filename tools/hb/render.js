const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const [,, inp, out, foot] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + inp, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: out, format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: `<div style="font-family:Arial;font-size:6.5px;color:#6b7686;width:100%;padding:0 15mm;display:flex;justify-content:space-between"><span>${foot}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
    margin: { top: '16mm', bottom: '18mm', left: '15mm', right: '15mm' } });
  await b.close();
})();
