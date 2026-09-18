// Reusable Omnisient business-case deck primitives (PptxGenJS, 16:9).
// Design system extracted from 06-Resources/Intercom-Pro-Business-Case.pptx – keep values in sync if that deck's look ever changes.
const pptxgen = require('pptxgenjs');

const PAGE = { W: 10, H: 5.625 };

const COLORS = {
  navy: '0D1B4B',
  accent: '3A6FD8',
  cardFill: 'F0F4FB',
  cardFillAlt: 'F6F8FC',
  cardBorder: 'E4E8F2',
  riskFill: 'FDF2F2',
  riskAccent: 'B91C1C',
  bodyText: '2C2C44',
  cardBody: '475569',
  footerGray: '94A3B8',
  lightOnNavy: 'FFFFFF',
  lightOnNavy2: 'CFE0FF',
  lightOnNavy3: 'DBE6FB',
};

const FONT = 'Poppins';

const SIZE = {
  title: 34,
  headline: 25,
  kicker: 11,
  lead: 14.5,
  cardTitle: 13,
  cardBody: 11,
  callout: 11.5,
  footer: 8,
};

function newDeck() {
  const pptx = new pptxgen();
  pptx.defineLayout({ name: 'BIZCASE_16x9', width: PAGE.W, height: PAGE.H });
  pptx.layout = 'BIZCASE_16x9';
  return pptx;
}

function addCover(pptx, { title, subtitle, date }) {
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.navy };
  slide.addText(title, {
    x: 0.7, y: 2.0, w: PAGE.W - 1.4, h: 1.0,
    fontFace: FONT, fontSize: SIZE.title, bold: true, color: COLORS.lightOnNavy,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.7, y: 2.85, w: PAGE.W - 1.4, h: 0.5,
      fontFace: FONT, fontSize: SIZE.lead, color: COLORS.lightOnNavy2,
    });
  }
  slide.addText(`Omnisient · Confidential${date ? ' · ' + date : ''}`, {
    x: 0.7, y: PAGE.H - 0.6, w: PAGE.W - 1.4, h: 0.3,
    fontFace: FONT, fontSize: SIZE.footer, color: COLORS.lightOnNavy3,
  });
  return slide;
}

// Chrome shared by every content slide: top bar, kicker, headline, footer, page number.
function addContentSlide(pptx, { kicker, headline, topic, pageNum }) {
  const slide = pptx.addSlide();
  slide.background = { color: 'FFFFFF' };
  slide.addShape('rect', { x: 0, y: 0, w: PAGE.W, h: 0.08, fill: { color: COLORS.accent }, line: { type: 'none' } });
  slide.addShape('rect', { x: PAGE.W - 0.65, y: 0.25, w: 0.15, h: 0.15, fill: { color: COLORS.accent }, line: { type: 'none' } });
  slide.addText(kicker.toUpperCase(), {
    x: 0.5, y: 0.26, w: PAGE.W - 1.2, h: 0.25,
    fontFace: FONT, fontSize: SIZE.kicker, bold: true, color: COLORS.accent, charSpacing: 1,
  });
  slide.addText(headline, {
    x: 0.5, y: 0.5, w: PAGE.W - 1, h: 0.6,
    fontFace: FONT, fontSize: SIZE.headline, bold: true, color: COLORS.navy,
  });
  slide.addShape('line', {
    x: 0.5, y: PAGE.H - 0.32, w: PAGE.W - 1, h: 0,
    line: { color: COLORS.cardBorder, width: 0.75 },
  });
  slide.addText(`Omnisient · ${topic} · Confidential`, {
    x: 0.5, y: PAGE.H - 0.28, w: PAGE.W - 2, h: 0.22,
    fontFace: FONT, fontSize: SIZE.footer, color: COLORS.footerGray,
  });
  slide.addText(String(pageNum), {
    x: PAGE.W - 1.0, y: PAGE.H - 0.28, w: 0.5, h: 0.22, align: 'right',
    fontFace: FONT, fontSize: SIZE.footer, color: COLORS.footerGray,
  });
  return slide;
}

// --- Content block primitives (all take explicit x/y/w/h) ---

function addCardGrid(slide, cards, { x = 0.5, y, w = PAGE.W - 1, h = 1.5, gap = 0.2 } = {}) {
  const n = cards.length;
  const colW = (w - gap * (n - 1)) / n;
  cards.forEach((card, i) => {
    const cx = x + i * (colW + gap);
    slide.addShape('roundRect', {
      x: cx, y, w: colW, h, rectRadius: 0.06,
      fill: { color: COLORS.cardFill }, line: { color: COLORS.cardBorder, width: 0.75 },
    });
    slide.addText(card.title, {
      x: cx + 0.15, y: y + 0.15, w: colW - 0.3, h: 0.3,
      fontFace: FONT, fontSize: SIZE.cardTitle, bold: true, color: COLORS.navy,
    });
    slide.addText(card.body, {
      x: cx + 0.15, y: y + 0.5, w: colW - 0.3, h: h - 0.65, valign: 'top',
      fontFace: FONT, fontSize: SIZE.cardBody, color: COLORS.cardBody,
    });
  });
}

function addNavyPanel(slide, { x = 0.5, y, w = PAGE.W - 1, h = 1.5, title, body, bullets }) {
  slide.addShape('roundRect', { x, y, w, h, rectRadius: 0.06, fill: { color: COLORS.navy }, line: { type: 'none' } });
  let cursorY = y + 0.18;
  if (title) {
    slide.addText(title, {
      x: x + 0.2, y: cursorY, w: w - 0.4, h: 0.3,
      fontFace: FONT, fontSize: SIZE.cardTitle, bold: true, color: COLORS.lightOnNavy,
    });
    cursorY += 0.35;
  }
  const bodyH = h - (cursorY - y) - 0.15;
  if (bullets) {
    const text = bullets.map((b) => ({ text: b, options: { bullet: { code: '25CF' }, breakLine: true, paraSpaceAfter: 4 } }));
    slide.addText(text, { x: x + 0.2, y: cursorY, w: w - 0.4, h: bodyH, valign: 'top', fontFace: FONT, fontSize: SIZE.cardBody, color: COLORS.lightOnNavy2 });
  } else if (body) {
    slide.addText(body, { x: x + 0.2, y: cursorY, w: w - 0.4, h: bodyH, valign: 'top', fontFace: FONT, fontSize: SIZE.cardBody, color: COLORS.lightOnNavy2 });
  }
}

function addCallout(slide, { x = 0.5, y, w = PAGE.W - 1, h = 0.5, text, tone = 'blue' }) {
  const fill = tone === 'red' ? COLORS.riskFill : COLORS.cardFillAlt;
  const bar = tone === 'red' ? COLORS.riskAccent : COLORS.accent;
  slide.addShape('rect', { x, y, w: 0.06, h, fill: { color: bar }, line: { type: 'none' } });
  slide.addShape('rect', { x: x + 0.06, y, w: w - 0.06, h, fill: { color: fill }, line: { type: 'none' } });
  slide.addText(text, { x: x + 0.25, y, w: w - 0.5, h, valign: 'middle', fontFace: FONT, fontSize: SIZE.callout, color: COLORS.bodyText });
}

function addBulletList(slide, { x = 0.5, y, w = PAGE.W - 1, h, items }) {
  const text = items.map((i) => ({ text: i, options: { bullet: { code: '25CF' }, breakLine: true, paraSpaceAfter: 8 } }));
  slide.addText(text, { x, y, w, h: h || 0.4 * items.length + 0.2, valign: 'top', fontFace: FONT, fontSize: SIZE.lead, color: COLORS.bodyText });
}

function addParagraph(slide, { x = 0.5, y, w = PAGE.W - 1, h = 0.6, text }) {
  slide.addText(text, { x, y, w, h, valign: 'top', fontFace: FONT, fontSize: SIZE.lead, color: COLORS.bodyText });
}

function addTable(slide, { x = 0.5, y, w = PAGE.W - 1, headers, rows }) {
  const headerRow = headers.map((h) => ({
    text: h, options: { bold: true, color: COLORS.lightOnNavy, fill: { color: COLORS.navy }, fontFace: FONT, fontSize: SIZE.cardBody, valign: 'middle' },
  }));
  const bodyRows = rows.map((r, i) => r.map((cell) => ({
    text: String(cell), options: { color: COLORS.bodyText, fill: { color: i % 2 === 0 ? 'FFFFFF' : COLORS.cardFillAlt }, fontFace: FONT, fontSize: SIZE.cardBody, valign: 'middle' },
  })));
  slide.addTable([headerRow, ...bodyRows], { x, y, w, border: { type: 'solid', color: COLORS.cardBorder, pt: 0.5 }, autoPage: false });
}

// --- Auto-flow renderer: stacks blocks vertically; 'row' nests blocks side by side ---

function defaultHeight(block) {
  switch (block.type) {
    case 'cardGrid': return block.h || 1.5;
    case 'navyPanel': return block.h || 1.5;
    case 'callout': return block.h || 0.5;
    case 'bulletList': return block.h || 0.4 * block.items.length + 0.2;
    case 'table': return block.h || 0.4 * (block.rows.length + 1);
    case 'paragraph': return block.h || 0.6;
    case 'row': return Math.max(...block.blocks.map(defaultHeight));
    default: throw new Error(`Unknown block type: ${block.type}`);
  }
}

function renderBlock(slide, block, { x, y, w }) {
  const h = defaultHeight(block);
  switch (block.type) {
    case 'cardGrid': addCardGrid(slide, block.cards, { x, y, w, h }); break;
    case 'navyPanel': addNavyPanel(slide, { x, y, w, h, title: block.title, body: block.body, bullets: block.bullets }); break;
    case 'callout': addCallout(slide, { x, y, w, h, text: block.text, tone: block.tone }); break;
    case 'bulletList': addBulletList(slide, { x, y, w, h, items: block.items }); break;
    case 'table': addTable(slide, { x, y, w, headers: block.headers, rows: block.rows }); break;
    case 'paragraph': addParagraph(slide, { x, y, w, h, text: block.text }); break;
    case 'row': {
      const gap = block.gap ?? 0.2;
      const weights = block.blocks.map((b) => b.weight || 1);
      const totalWeight = weights.reduce((a, b2) => a + b2, 0);
      const totalGap = gap * (block.blocks.length - 1);
      let cx = x;
      block.blocks.forEach((child, i) => {
        const cw = (w - totalGap) * (weights[i] / totalWeight);
        renderBlock(slide, child, { x: cx, y, w: cw });
        cx += cw + gap;
      });
      break;
    }
    default: throw new Error(`Unknown block type: ${block.type}`);
  }
  return h;
}

function renderContentSlide(pptx, { kicker, headline, topic, pageNum, blocks = [], startY = 1.35, gap = 0.15 }) {
  const slide = addContentSlide(pptx, { kicker, headline, topic, pageNum });
  let cursorY = startY;
  blocks.forEach((block) => {
    const h = renderBlock(slide, block, { x: 0.5, y: cursorY, w: PAGE.W - 1 });
    cursorY += h + gap;
  });
  return slide;
}

module.exports = {
  PAGE, COLORS, FONT, SIZE,
  newDeck, addCover, addContentSlide, renderContentSlide,
  addCardGrid, addNavyPanel, addCallout, addBulletList, addTable, addParagraph,
};
