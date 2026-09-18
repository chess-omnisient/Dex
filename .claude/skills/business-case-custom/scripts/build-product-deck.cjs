#!/usr/bin/env node
// Renders a document from a JSON content spec using product-deck-lib.cjs (the default style).
// Usage: node build-product-deck.cjs <content.json> <output.pptx>
const path = require('path');
const fs = require('fs');
const lib = require('./product-deck-lib.cjs');
const { newDeck, addHeader, addLead, addPanel, addPanelRows, addPillRow, addCardGrid, addBanner, addFooter, COLORS } = lib;

const [, , contentPath, outPath] = process.argv;
if (!contentPath || !outPath) {
  console.error('Usage: node build-product-deck.cjs <content.json> <output.pptx>');
  process.exit(1);
}

const content = JSON.parse(fs.readFileSync(path.resolve(contentPath), 'utf8'));
const pptx = newDeck();

function defaultHeight(block) {
  switch (block.type) {
    case 'cardGrid': {
      const cols = block.cols || 2;
      const rows = Math.ceil(block.cards.length / cols);
      const cardH = block.cardH || 1.05;
      return rows * (cardH + 0.18) - 0.18;
    }
    case 'twoPanel': return block.h || 1.85;
    case 'pillRow': return 0.62;
    case 'banner': return block.h || 0.55;
    case 'paragraph': return block.h || 0.4;
    default: throw new Error(`Unknown block type: ${block.type}`);
  }
}

function renderBlock(slide, block, { x, y, w }) {
  const h = defaultHeight(block);
  switch (block.type) {
    case 'cardGrid':
      addCardGrid(slide, { x, y, w, cols: block.cols || 2, cards: block.cards, h: block.cardH });
      break;
    case 'twoPanel': {
      const gap = block.gap ?? 0.3;
      const pw = (w - gap) / 2;
      const left = block.left, right = block.right;
      const lc = addPanel(slide, { x, y, w: pw, h, accent: left.accent === 'secondary' ? COLORS.indigo : COLORS.blue, label: left.label, icon: left.icon || 'check' });
      addPanelRows(slide, { x: x + 0.12, y: lc, w: pw - 0.24, items: left.items, tone: left.icon || 'check' });
      const rc = addPanel(slide, { x: x + pw + gap, y, w: pw, h, accent: right.accent === 'secondary' ? COLORS.indigo : COLORS.blue, label: right.label, icon: right.icon || 'no' });
      addPanelRows(slide, { x: x + pw + gap + 0.12, y: rc, w: pw - 0.24, items: right.items, tone: right.icon || 'no' });
      break;
    }
    case 'pillRow':
      addPillRow(slide, { x, y, w, pills: block.pills });
      break;
    case 'banner':
      addBanner(slide, { x, y, w, h, text: block.text, icon: block.icon });
      break;
    case 'paragraph':
      slide.addText(block.text, { x, y, w, h, fontFace: lib.FONT, fontSize: lib.SIZE.lead, color: COLORS.ink, valign: 'top' });
      break;
    default:
      throw new Error(`Unknown block type: ${block.type}`);
  }
  return h;
}

content.slides.forEach((s) => {
  const slide = pptx.addSlide();
  addHeader(slide, { eyebrow: s.eyebrow, title: s.title });
  let cursorY = 1.12;
  if (s.lead) {
    cursorY = addLead(slide, { text: s.lead, y: cursorY });
    cursorY += 0.13;
  } else {
    cursorY = 1.15;
  }
  (s.blocks || []).forEach((block) => {
    const h = renderBlock(slide, block, { x: 0.5, y: cursorY, w: lib.PAGE.W - 1 });
    cursorY += h + (block.gapAfter ?? 0.2);
  });
  addFooter(slide, { tagline: content.meta.tagline, pageNum: pptx.slides.length });
});

pptx.writeFile({ fileName: path.resolve(outPath) }).then(() => {
  console.log(`Wrote ${outPath}`);
});
