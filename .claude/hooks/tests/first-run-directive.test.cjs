const test = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const HOOK_PATH = path.resolve(__dirname, '..', 'session-start.sh');

function createSandbox(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'dex-first-run-'));
  const vault = path.join(root, 'vault');
  const home = path.join(root, 'home');
  const launchAgents = path.join(root, 'LaunchAgents');
  const dedupFile = path.join(root, 'session-context-dedup');
  fs.mkdirSync(vault, { recursive: true });
  fs.mkdirSync(home, { recursive: true });
  fs.mkdirSync(launchAgents, { recursive: true });
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return { vault, home, launchAgents, dedupFile };
}

function runSessionStart(sandbox) {
  const result = spawnSync('/bin/bash', [HOOK_PATH], {
    cwd: sandbox.vault,
    encoding: 'utf-8',
    env: {
      ...process.env,
      CLAUDE_PROJECT_DIR: sandbox.vault,
      DEX_LAUNCH_AGENTS_DIR: sandbox.launchAgents,
      DEX_SESSION_CONTEXT_DEDUP_FILE: sandbox.dedupFile,
      HOME: sandbox.home,
      PATH: process.env.PATH || '/usr/bin:/bin',
      VAULT_PATH: sandbox.vault,
      DEX_SESSION_HEALTH_CALLS: path.join(
        path.dirname(sandbox.vault),
        'unused-session-health-calls',
      ),
    },
    timeout: 10_000,
  });

  assert.equal(
    result.status,
    0,
    `session-start.sh exited ${result.status}\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`,
  );
  return result.stdout;
}

function completeOnboarding(sandbox) {
  const marker = path.join(sandbox.vault, 'System', '.onboarding-complete');
  fs.mkdirSync(path.dirname(marker), { recursive: true });
  fs.writeFileSync(marker, '{}\n');
}

test('a never-onboarded vault begins canonical onboarding on its first session', (t) => {
  const sandbox = createSandbox(t);

  const stdout = runSessionStart(sandbox);

  assert.match(stdout, /FIRST-TIME SETUP REQUIRED/);
  assert.match(stdout, /begin onboarding NOW/);
  assert.match(stdout, /start_onboarding_session\(\)/);
  assert.match(stdout, /\.claude\/flows\/onboarding\.md/);
  assert.doesNotMatch(stdout, /resume setup NOW/);
});

test('an interrupted onboarding resumes through the canonical flow', (t) => {
  const sandbox = createSandbox(t);
  const sessionFile = path.join(
    sandbox.vault,
    'System',
    '.onboarding-session.json',
  );
  fs.mkdirSync(path.dirname(sessionFile), { recursive: true });
  fs.writeFileSync(sessionFile, JSON.stringify({ current_step: 3 }));

  const stdout = runSessionStart(sandbox);

  assert.match(stdout, /FIRST-TIME SETUP REQUIRED/);
  assert.match(stdout, /resume setup NOW/);
  assert.match(stdout, /restores their progress/);
});

test('an onboarded vault emits no first-time setup directive', (t) => {
  const sandbox = createSandbox(t);
  completeOnboarding(sandbox);

  const stdout = runSessionStart(sandbox);

  assert.doesNotMatch(stdout, /FIRST-TIME SETUP REQUIRED/);
  assert.doesNotMatch(stdout, /begin onboarding NOW/);
  assert.doesNotMatch(stdout, /resume setup NOW/);
});
