#!/usr/bin/env node
/**
 * Career Evidence Candidate Detector
 *
 * Repository-wide PostToolUse hook for Write and Edit. Path-filters to
 * 05-Areas/Career/Evidence/. A file the user placed in that folder is already
 * evidence; this hook describes it as an unconfirmed candidate and never
 * writes the evidence log.
 */
const fs = require('fs');
const path = require('path');
const { loadPaths } = require('./paths.cjs');

const _paths = loadPaths();
const SKIP_LOG_NAME = 'career-evidence-skip.jsonl';
const SKIP_EXTS = new Set([
  '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico', '.svg', '.pdf',
  '.zip', '.tar', '.gz', '.mp3', '.mp4', '.mov', '.wav', '.pptx', '.xlsx', '.docx',
]);

function isInside(root, absoluteFilePath) {
  const relative = path.relative(root, absoluteFilePath);
  return !(
    relative === ''
    || relative.startsWith(`..${path.sep}`)
    || relative === '..'
    || path.isAbsolute(relative)
  );
}

function persistSkip(reason) {
  try {
    const dir = _paths.DEX_RUNTIME_DIR;
    fs.mkdirSync(dir, { recursive: true });
    fs.appendFileSync(
      path.join(dir, SKIP_LOG_NAME),
      `${JSON.stringify({ ts: new Date().toISOString(), reason })}\n`,
    );
  } catch {
    // Fail open: a skip log miss must never block the write that triggered us.
  }
}

function skip(reason, { persist = false } = {}) {
  if (persist) {
    console.error(`[dex-hook-skip] ${reason}`);
    persistSkip(reason);
  }
  process.exit(0);
}

function isRegularVaultFile(filePath) {
  const vaultRoot = path.resolve(_paths.VAULT_ROOT);
  const absoluteFilePath = path.resolve(filePath);
  const relativeToVault = path.relative(vaultRoot, absoluteFilePath);
  if (
    relativeToVault === ''
    || relativeToVault.startsWith(`..${path.sep}`)
    || relativeToVault === '..'
    || path.isAbsolute(relativeToVault)
  ) return false;

  let cursor = vaultRoot;
  const parts = relativeToVault.split(path.sep);
  for (const [index, part] of parts.entries()) {
    cursor = path.join(cursor, part);
    let stat;
    try {
      stat = fs.lstatSync(cursor);
    } catch {
      return false;
    }
    if (stat.isSymbolicLink()) return false;
    const isLast = index === parts.length - 1;
    if (isLast ? !stat.isFile() : !stat.isDirectory()) return false;
  }
  return true;
}

function bodyWithoutFrontmatter(content) {
  const match = content.match(/^---\s*\n[\s\S]*?\n---(?:\s*\n|$)/);
  return match ? content.slice(match[0].length) : content;
}

function isMetadataLine(trimmed) {
  if (!trimmed || trimmed === '---') return true;
  if (trimmed.startsWith('#')) return true;
  if (trimmed.startsWith('|')) return true;
  if (trimmed.startsWith('<!--')) return true;
  if (/^\*\*[^*]+:\*\*/.test(trimmed)) return true;
  if (/^[A-Za-z][\w-]*:\s/.test(trimmed)) return true;
  return false;
}

function briefDescription(content, fileName) {
  for (const line of bodyWithoutFrontmatter(content).split('\n')) {
    const trimmed = line.trim().replace(/^[-*]\s+/, '');
    if (isMetadataLine(trimmed)) continue;
    if (trimmed.length < 8) continue;
    return trimmed.substring(0, 120);
  }
  return `Evidence captured from ${fileName}`;
}

function classifySkillArea(content) {
  const skillAreas = [];
  const skillPatterns = {
    Leadership: /leadership|team|managed|mentored|coached|stakeholder|judgement|stewardship/i,
    Strategy: /strategy|strategic|roadmap|vision|planning/i,
    Technical: /technical|architecture|system|engineering|code/i,
    Communication: /presentation|stakeholder|executive|board|communication/i,
    Customer: /customer|client|user|NPS|satisfaction|retention/i,
    Product: /product|feature|launch|release|adoption/i,
    Sales: /deal|revenue|pipeline|close|win/i,
  };

  for (const [area, pattern] of Object.entries(skillPatterns)) {
    if (pattern.test(content)) skillAreas.push(area);
  }
  return skillAreas.length > 0 ? skillAreas.join(', ') : 'General';
}

function main() {
  let input;
  try {
    input = JSON.parse(fs.readFileSync(0, 'utf-8'));
  } catch {
    skip('invalid-json-input');
  }

  const filePath = input?.tool_input?.file_path || input?.toolInput?.file_path || '';
  if (!filePath || typeof filePath !== 'string') {
    skip('missing-file-path');
  }

  const absoluteFilePath = path.resolve(filePath);
  if (!isInside(_paths.CAREER_DIR, absoluteFilePath)) {
    skip('not-career-path');
  }

  if (!isRegularVaultFile(absoluteFilePath)) {
    skip('not-regular-vault-file', { persist: true });
  }

  const ext = path.extname(absoluteFilePath).toLowerCase();
  if (SKIP_EXTS.has(ext)) {
    skip(`unsupported-extension:${ext}`, { persist: true });
  }

  if (!isInside(_paths.EVIDENCE_DIR, absoluteFilePath)) {
    skip('not-evidence-folder', { persist: true });
  }

  const baseName = path.basename(absoluteFilePath);
  if (baseName.toLowerCase() === 'readme.md') {
    skip('seed-readme', { persist: true });
  }

  let content;
  try {
    content = fs.readFileSync(absoluteFilePath, 'utf-8');
  } catch {
    skip('unreadable-file', { persist: true });
  }

  const retrievedAt = new Date().toISOString();
  const fileName = path.basename(absoluteFilePath, '.md');
  const skillArea = classifySkillArea(content);
  const briefDesc = briefDescription(content, fileName);

  const frontmatter = content.match(/^---\s*\n([\s\S]*?)\n---(?:\s*\n|$)/);
  const eventDateMatch = frontmatter?.[1]?.match(/^date:\s*["']?(\d{4}-\d{2}-\d{2})["']?\s*$/m);
  const eventDate = eventDateMatch?.[1] || 'unknown';
  const sourcePath = path.relative(_paths.VAULT_ROOT, absoluteFilePath).split(path.sep).join('/');
  const evidenceLogPath = path.join(_paths.CAREER_DIR, 'Evidence_Log.md');
  const destinationPath = path.relative(_paths.VAULT_ROOT, evidenceLogPath).split(path.sep).join('/');
  const entry = `| ${eventDate} | ${skillArea} | [[${fileName}]] | ${briefDesc.replace(/\|/g, '/')} |`;
  const uncertainty = eventDate === 'unknown'
    ? 'source event date is unknown; do not substitute the retrieval date'
    : 'achievement meaning and skill-area classification are inferred and require user validation';

  const output = {
    continue: true,
    hookSpecificOutput: {
      hookEventName: 'PostToolUse',
      additionalContext: [
        '<career_evidence_candidate>',
        'Candidate only; nothing was saved.',
        `Source path: ${sourcePath}`,
        `Source event date: ${eventDate}`,
        `Retrieved as-of: ${retrievedAt}`,
        `Proposed destination: ${destinationPath}`,
        `Unconfirmed candidate entry: ${entry}`,
        `Uncertainty: ${uncertainty}.`,
        'Before any save, show the exact proposed bytes and destination, obtain explicit confirmation for this evidence entry, then write and read back the destination. If confirmation or read-back is absent, do not save or claim capture.',
        '</career_evidence_candidate>',
      ].join('\n'),
    },
  };
  console.log(JSON.stringify(output));
}

try {
  main();
} catch {
  skip('unexpected-error', { persist: true });
}
