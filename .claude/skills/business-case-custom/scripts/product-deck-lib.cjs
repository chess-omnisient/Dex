// Omnisient product design system (PptxGenJS, 16:9) — the DEFAULT style for documents
// this skill produces. White background, brand blue/dark-blue accents, outlined cards,
// icon chips, pill badges, numbered card grids, solid CTA banners, real Omnisient logo.
// deck-lib.cjs's navy Intercom-Pro look is kept as a legacy/alternate style only.
const pptxgen = require('pptxgenjs');

const PAGE = { W: 10, H: 5.625 };

// Official Omnisient brand colors: main blue 3272B9, secondary (dark) blue 30297E.
// No third accent color exists in the brand — "negative/no" rows use secondary blue
// instead of an invented violet, so the whole deck stays inside the two real brand colors.
const COLORS = {
  ink: '1E1B2E',
  indigo: '30297E',
  indigoDark: '30297E',
  blue: '3272B9',
  violet: '30297E',
  border: 'E4E7F0',
  rowFill: 'F1F3FA',
  cardFill: 'FFFFFF',
  subtext: '6B7280',
  pillPublicBg: 'E7F0F8', pillPublicText: '3272B9',
  pillRegisteredBg: 'E7E6F2', pillRegisteredText: '30297E',
  pillEntitledBg: 'E7F0F8', pillEntitledText: '3272B9',
  pillRestrictedBg: 'E5E7EB', pillRestrictedText: '374151',
  pillSecretBg: '30297E', pillSecretText: 'FFFFFF',
  banner: '30297E',
  chipCheck: '3272B9',
  chipNo: '30297E',
  white: 'FFFFFF',
};

const FONT = 'Poppins';

const SIZE = {
  eyebrow: 10,
  title: 22,
  lead: 12,
  panelHeader: 10,
  rowText: 11,
  pillLabel: 11,
  pillSub: 8.5,
  cardTitle: 12,
  cardDesc: 10,
  tag: 8,
  footer: 8,
};

function newDeck() {
  const pptx = new pptxgen();
  pptx.defineLayout({ name: 'PRODUCT_16x9', width: PAGE.W, height: PAGE.H });
  pptx.layout = 'PRODUCT_16x9';
  return pptx;
}

const LOGO_PATH = '/Users/chess/dex/06-Resources/logo.png';
const LOGO_ASPECT = 2000 / 532;

function addLogo(slide, { w = 1.3 } = {}) {
  const h = w / LOGO_ASPECT;
  const x = PAGE.W - 0.5 - w;
  const y = 0.3;
  slide.addImage({ path: LOGO_PATH, x, y, w, h });
}

function addHeader(slide, { eyebrow, title }) {
  slide.background = { color: 'FFFFFF' };
  slide.addText(eyebrow.toUpperCase(), { x: 0.5, y: 0.3, w: 6.5, h: 0.22, fontFace: FONT, fontSize: SIZE.eyebrow, bold: true, color: COLORS.blue, charSpacing: 1 });
  slide.addText(title, { x: 0.5, y: 0.52, w: 7.3, h: 0.42, fontFace: FONT, fontSize: SIZE.title, bold: true, color: COLORS.indigo });
  addLogo(slide);
  slide.addShape('line', { x: 0.5, y: 1.0, w: PAGE.W - 1, h: 0, line: { color: COLORS.border, width: 0.75 } });
}

function addLead(slide, { text, y = 1.12, h = 0.4 }) {
  slide.addText(text, { x: 0.5, y, w: PAGE.W - 1, h, fontFace: FONT, fontSize: SIZE.lead, color: COLORS.ink, valign: 'top' });
  return y + h;
}

function iconChip(slide, { x, y, size = 0.28, tone = 'check', label }) {
  const bg = tone === 'no' ? COLORS.chipNo : tone === 'num' ? 'FFFFFF' : COLORS.chipCheck;
  const textColor = tone === 'num' ? COLORS.blue : COLORS.white;
  slide.addShape('roundRect', { x, y, w: size, h: size, rectRadius: 0.06, fill: { color: bg }, line: tone === 'num' ? { color: COLORS.blue, width: 1 } : { type: 'none' } });
  const glyph = label || (tone === 'no' ? '✕' : '✓');
  slide.addText(glyph, { x, y: y - 0.01, w: size, h: size, align: 'center', valign: 'middle', fontFace: FONT, fontSize: 10, bold: true, color: textColor });
}

function addPanel(slide, { x, y, w, h, accent = COLORS.blue, label, icon = 'check' }) {
  slide.addShape('roundRect', { x, y, w, h, rectRadius: 0.08, fill: { color: COLORS.cardFill }, line: { color: COLORS.border, width: 1 } });
  slide.addShape('rect', { x, y, w, h: 0.035, fill: { color: accent }, line: { type: 'none' } });
  iconChip(slide, { x: x + 0.18, y: y + 0.16, size: 0.22, tone: icon });
  slide.addText(label.toUpperCase(), { x: x + 0.48, y: y + 0.14, w: w - 0.6, h: 0.26, fontFace: FONT, fontSize: SIZE.panelHeader, bold: true, color: accent, charSpacing: 0.5 });
  return y + 0.5;
}

function addPanelRow(slide, { x, y, w, text, tone = 'check' }) {
  const h = 0.4;
  slide.addShape('roundRect', { x, y, w, h, rectRadius: 0.05, fill: { color: COLORS.rowFill }, line: { type: 'none' } });
  iconChip(slide, { x: x + 0.12, y: y + 0.08, size: 0.24, tone });
  slide.addText(text, { x: x + 0.46, y, w: w - 0.6, h, valign: 'middle', fontFace: FONT, fontSize: SIZE.rowText, color: COLORS.ink });
  return h;
}

function addPanelRows(slide, { x, y, w, items, tone = 'check', gap = 0.1 }) {
  let cy = y;
  items.forEach((text) => {
    const h = addPanelRow(slide, { x, y: cy, w, text, tone });
    cy += h + gap;
  });
  return cy;
}

function addPillRow(slide, { x = 0.5, y, w = PAGE.W - 1, pills }) {
  const gap = 0.15;
  const n = pills.length;
  const colW = (w - gap * (n - 1)) / n;
  const h = 0.62;
  pills.forEach((p, i) => {
    const px = x + i * (colW + gap);
    slide.addShape('roundRect', { x: px, y, w: colW, h, rectRadius: 0.3, fill: { color: p.bg }, line: { type: 'none' } });
    slide.addText(p.label, { x: px + 0.12, y: y + 0.07, w: colW - 0.24, h: 0.25, fontFace: FONT, fontSize: SIZE.pillLabel, bold: true, color: p.text });
    slide.addText(p.sub, { x: px + 0.12, y: y + 0.32, w: colW - 0.24, h: 0.24, fontFace: FONT, fontSize: SIZE.pillSub, color: p.text });
  });
  return h;
}

function addCardGrid(slide, { x = 0.5, y, w = PAGE.W - 1, cols = 2, cards, h }) {
  const gap = 0.18;
  const colW = (w - gap * (cols - 1)) / cols;
  const rows = Math.ceil(cards.length / cols);
  const cardH = h || 1.05;
  cards.forEach((card, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const cx = x + col * (colW + gap);
    const cy = y + row * (cardH + gap);
    slide.addShape('roundRect', { x: cx, y: cy, w: colW, h: cardH, rectRadius: 0.07, fill: { color: COLORS.cardFill }, line: { color: COLORS.border, width: 1 } });
    if (card.num) iconChip(slide, { x: cx + 0.15, y: cy + 0.13, size: 0.26, tone: 'num', label: String(card.num) });
    const titleX = card.num ? cx + 0.5 : cx + 0.18;
    slide.addText(card.title, { x: titleX, y: cy + 0.12, w: colW - (card.num ? 0.65 : 0.35), h: 0.28, fontFace: FONT, fontSize: SIZE.cardTitle, bold: true, color: COLORS.indigo });
    slide.addText(card.desc, { x: cx + 0.18, y: cy + 0.42, w: colW - 0.35, h: cardH - 0.5, fontFace: FONT, fontSize: SIZE.cardDesc, color: COLORS.subtext, valign: 'top' });
    if (card.tags) {
      let tx = cx + 0.18;
      const ty = cy + cardH - 0.28;
      card.tags.forEach((tag) => {
        const tw = 0.09 * tag.length + 0.22;
        slide.addShape('roundRect', { x: tx, y: ty, w: tw, h: 0.22, rectRadius: 0.11, fill: { color: COLORS.rowFill }, line: { type: 'none' } });
        slide.addText('✓ ' + tag, { x: tx + 0.06, y: ty, w: tw - 0.1, h: 0.22, valign: 'middle', fontFace: FONT, fontSize: SIZE.tag, color: COLORS.blue });
        tx += tw + 0.08;
      });
    }
  });
  return rows * (cardH + gap) - gap;
}

function addBanner(slide, { x = 0.5, y, w = PAGE.W - 1, h = 0.55, text, icon = '⚑' }) {
  slide.addShape('roundRect', { x, y, w, h, rectRadius: 0.08, fill: { color: COLORS.banner }, line: { type: 'none' } });
  slide.addText(icon, { x: x + 0.18, y, w: 0.3, h, valign: 'middle', fontFace: FONT, fontSize: 13, color: COLORS.white });
  slide.addText(text, { x: x + 0.5, y, w: w - 0.7, h, valign: 'middle', fontFace: FONT, fontSize: SIZE.rowText, bold: true, color: COLORS.white });
  return h;
}

function addFooter(slide, { tagline, pageNum }) {
  slide.addShape('line', { x: 0.5, y: PAGE.H - 0.32, w: PAGE.W - 1, h: 0, line: { color: COLORS.border, width: 0.75 } });
  slide.addText(tagline, { x: 0.5, y: PAGE.H - 0.28, w: PAGE.W - 2, h: 0.22, fontFace: FONT, fontSize: SIZE.footer, color: COLORS.subtext });
  slide.addText(String(pageNum), { x: PAGE.W - 1.0, y: PAGE.H - 0.28, w: 0.5, h: 0.22, align: 'right', fontFace: FONT, fontSize: SIZE.footer, color: COLORS.subtext });
}

module.exports = {
  PAGE, COLORS, FONT, SIZE,
  newDeck, addHeader, addLead, addPanel, addPanelRow, addPanelRows,
  addPillRow, addCardGrid, addBanner, addFooter, addLogo, iconChip,
};
