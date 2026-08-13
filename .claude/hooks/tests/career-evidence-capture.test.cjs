const test = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '../../..');
const HOOK = path.resolve(__dirname, '../career-evidence-capture.cjs');
const SETTINGS_PATH = path.join(ROOT, '.claude/settings.json');
const SKIP_LOG = path.join('System', '.dex', 'career-evidence-skip.jsonl');

function createVault(t) {
  const vault = fs.mkdtempSync(path.join(os.tmpdir(), 'dex-career-evidence-'));
  fs.mkdirSync(path.join(vault, '05-Areas', 'Career', 'Evidence', 'Achievements'), { recursive: true });
  t.after(() => fs.rmSync(vault, { recursive: true, force: true }));
  return vault;
}

function runHook(vault, filePath, extra = {}) {
  return spawnSync(process.execPath, [HOOK], {
    cwd: extra.cwd || vault,
    encoding: 'utf8',
    env: {
      ...process.env,
      CLAUDE_PROJECT_DIR: vault,
      VAULT_PATH: vault,
    },
    input: JSON.stringify({
      hook_event_name: 'PostToolUse',
      tool_name: extra.toolName || 'Write',
      tool_input: { file_path: filePath },
    }),
  });
}

function skipLog(vault) {
  const logPath = path.join(vault, SKIP_LOG);
  if (!fs.existsSync(logPath)) return [];
  return fs.readFileSync(logPath, 'utf8')
    .split('\n')
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

test('repository settings wire career evidence capture on Write and Edit', () => {
  const settings = JSON.parse(fs.readFileSync(SETTINGS_PATH, 'utf8'));
  const entries = settings.hooks?.PostToolUse || [];
  const wired = entries.filter((entry) =>
    (entry.hooks || []).some((hook) =>
      typeof hook.command === 'string' && hook.command.includes('career-evidence-capture.cjs'),
    ),
  );
  assert.equal(wired.length, 1, 'career-evidence-capture.cjs must be a repository-wide PostToolUse hook');
  const matcher = new RegExp(`^(?:${wired[0].matcher})$`);
  assert.match('Write', matcher);
  assert.match('Edit', matcher);
  const command = wired[0].hooks.find((hook) => hook.command.includes('career-evidence-capture.cjs')).command;
  assert.match(command, /\$CLAUDE_PROJECT_DIR/);
});

test('career-coach skill no longer owns the only capture registration', () => {
  const skill = fs.readFileSync(
    path.join(ROOT, '.claude/skills/_available/capabilities/career/skills/career-coach/SKILL.md'),
    'utf8',
  );
  const frontmatter = skill.match(/^---\n([\s\S]*?)\n---/);
  assert.ok(frontmatter, 'career-coach SKILL.md must have YAML frontmatter');
  assert.doesNotMatch(frontmatter[1], /career-evidence-capture/);
});

test('achievement detection emits a consent prompt without writing evidence', (t) => {
  const vault = createVault(t);
  const source = path.join(vault, '05-Areas', 'Career', 'Evidence', 'Achievements', 'launch.md');
  const original = [
    '---',
    'date: 2026-07-10',
    '---',
    '# Launch',
    '',
    'Shipped the launch and improved an explicitly measured outcome.',
    '',
  ].join('\n');
  fs.writeFileSync(source, original);

  const result = runHook(vault, source);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(fs.readFileSync(source, 'utf8'), original);
  assert.equal(
    fs.existsSync(path.join(vault, '05-Areas', 'Career', 'Evidence_Log.md')),
    false,
    'a PostToolUse observation must never silently create or append evidence',
  );

  const output = JSON.parse(result.stdout);
  assert.equal(output.continue, true);
  assert.equal(output.hookSpecificOutput.hookEventName, 'PostToolUse');
  const context = output.hookSpecificOutput.additionalContext;
  assert.match(context, /candidate only; nothing was saved/i);
  assert.match(context, /source path: 05-Areas\/Career\/Evidence\/Achievements\/launch\.md/i);
  assert.match(context, /source event date: 2026-07-10/i);
  assert.match(context, /retrieved as-of: \d{4}-\d{2}-\d{2}T/i);
  assert.match(context, /uncertainty:/i);
  assert.match(context, /show the exact proposed bytes/i);
  assert.match(context, /explicit confirmation/i);
  assert.match(context, /read back/i);
  assert.deepEqual(skipLog(vault), []);
});

test('issue 505 repro: evidence write outside career-coach still emits a candidate', (t) => {
  const vault = createVault(t);
  const source = path.join(vault, '05-Areas', 'Career', 'Evidence', 'Achievements', 'judgement.md');
  fs.writeFileSync(source, [
    '# Chose not to build the rewrite',
    '',
    'Persuaded a sceptical stakeholder to keep the current path and unpicked a bad decision.',
    '',
  ].join('\n'));

  const result = runHook(vault, source, { toolName: 'Edit' });

  assert.equal(result.status, 0, result.stderr);
  const context = JSON.parse(result.stdout).hookSpecificOutput.additionalContext;
  assert.match(context, /candidate only; nothing was saved/i);
  assert.match(context, /persuaded a sceptical stakeholder/i);
  assert.doesNotMatch(context, /Evidence captured from judgement/);
  assert.equal(fs.existsSync(path.join(vault, '05-Areas', 'Career', 'Evidence_Log.md')), false);
  assert.deepEqual(skipLog(vault), []);
});

test('issue 505 repro: evidence without metrics or keyword verbs is still kept', (t) => {
  const vault = createVault(t);
  const source = path.join(vault, '05-Areas', 'Career', 'Evidence', 'Achievements', 'influence.md');
  fs.writeFileSync(source, [
    '---',
    'date: 2026-08-01',
    '---',
    '# Influence without a number',
    '',
    '**Pillar:** Team Growth',
    '',
    'Held the line in a review when the easier move was to overpromise.',
    '',
  ].join('\n'));

  const result = runHook(vault, source);

  assert.equal(result.status, 0, result.stderr);
  const context = JSON.parse(result.stdout).hookSpecificOutput.additionalContext;
  assert.match(context, /held the line in a review/i);
  assert.doesNotMatch(context, /\*\*Pillar:\*\*/);
  assert.match(context, /source event date: 2026-08-01/i);
});

test('missing source dates stay unknown and still do not create files', (t) => {
  const vault = createVault(t);
  const source = path.join(vault, '05-Areas', 'Career', 'Evidence', 'Achievements', 'note.md');
  fs.writeFileSync(source, 'Completed a customer launch.\n');

  const result = runHook(vault, source);

  assert.equal(result.status, 0, result.stderr);
  const context = JSON.parse(result.stdout).hookSpecificOutput.additionalContext;
  assert.match(context, /source event date: unknown/i);
  assert.match(context, /uncertainty: source event date is unknown/i);
  assert.equal(fs.existsSync(path.join(vault, '05-Areas', 'Career', 'Evidence_Log.md')), false);
});

test('a career file outside Evidence is skipped with a visible reason', (t) => {
  const vault = createVault(t);
  const source = path.join(vault, '05-Areas', 'Career', 'note.md');
  fs.writeFileSync(source, 'Completed a customer launch.\n');

  const result = runHook(vault, source);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /\[dex-hook-skip] not-evidence-folder/);
  const entries = skipLog(vault);
  assert.equal(entries.length, 1);
  assert.equal(entries[0].reason, 'not-evidence-folder');
  assert.equal(typeof entries[0].ts, 'string');
  assert.equal(Object.keys(entries[0]).sort().join(','), 'reason,ts');
});

test('a write outside Career stays silent and does not log a skip', (t) => {
  const vault = createVault(t);
  const source = path.join(vault, '04-Projects', 'note.md');
  fs.mkdirSync(path.dirname(source), { recursive: true });
  fs.writeFileSync(source, 'Not career evidence.\n');

  const result = runHook(vault, source);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr, '');
  assert.deepEqual(skipLog(vault), []);
});

test('a symlinked Career ancestor cannot expose an outside file', (t) => {
  const vault = fs.mkdtempSync(path.join(os.tmpdir(), 'dex-career-vault-'));
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'dex-career-outside-'));
  t.after(() => fs.rmSync(vault, { recursive: true, force: true }));
  t.after(() => fs.rmSync(outside, { recursive: true, force: true }));
  fs.mkdirSync(path.join(vault, '05-Areas'), { recursive: true });
  fs.symlinkSync(outside, path.join(vault, '05-Areas', 'Career'), 'dir');
  const source = path.join(outside, 'private.md');
  fs.writeFileSync(source, 'Achieved a private measured outcome.\n');

  const result = runHook(vault, path.join(vault, '05-Areas', 'Career', 'private.md'));

  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /\[dex-hook-skip] not-regular-vault-file/);
  assert.equal(fs.readFileSync(source, 'utf8'), 'Achieved a private measured outcome.\n');
  const entries = skipLog(vault);
  assert.equal(entries.length, 1);
  assert.equal(entries[0].reason, 'not-regular-vault-file');
});
