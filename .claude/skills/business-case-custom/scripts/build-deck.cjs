#!/usr/bin/env node
// Renders a business-case deck from a JSON content spec using deck-lib.cjs.
// Usage: node build-deck.cjs <content.json> <output.pptx>
const path = require('path');
const fs = require('fs');
const { newDeck, addCover, renderContentSlide } = require('./deck-lib.cjs');

const [, , contentPath, outPath] = process.argv;
if (!contentPath || !outPath) {
  console.error('Usage: node build-deck.cjs <content.json> <output.pptx>');
  process.exit(1);
}

const content = JSON.parse(fs.readFileSync(path.resolve(contentPath), 'utf8'));
const pptx = newDeck();

let pageNum = 0;
content.slides.forEach((s) => {
  if (s.type === 'cover') {
    addCover(pptx, { title: s.title, subtitle: s.subtitle, date: content.meta.date });
  } else {
    pageNum += 1;
    renderContentSlide(pptx, {
      kicker: s.kicker,
      headline: s.headline,
      topic: content.meta.topic,
      pageNum,
      blocks: s.blocks || [],
    });
  }
});

pptx.writeFile({ fileName: path.resolve(outPath) }).then(() => {
  console.log(`Wrote ${outPath}`);
});
