#!/usr/bin/env node

/**
 * Granola Auth Helper
 *
 * Checks and reports on Granola authentication status.
 * Granola handles its own OAuth through the desktop app and stores
 * credentials in supabase.json — no separate auth flow needed here.
 *
 * Usage:
 *   node granola-auth.cjs --status   Check authentication status
 *   node granola-auth.cjs --setup    Guide through Granola sign-in
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const GREEN = '\033[0;32m';
const YELLOW = '\033[1;33m';
const RED = '\033[0;31m';
const NC = '\033[0m';

function getGranolaCredsPath() {
  const homedir = os.homedir();
  const platform = os.platform();

  if (platform === 'darwin') {
    return path.join(homedir, 'Library/Application Support/Granola/supabase.json');
  } else if (platform === 'win32') {
    const roaming = process.env.APPDATA || path.join(homedir, 'AppData/Roaming');
    return path.join(roaming, 'Granola/supabase.json');
  } else {
    return path.join(homedir, '.config/Granola/supabase.json');
  }
}

function checkAuth() {
  const credsPath = getGranolaCredsPath();

  if (!fs.existsSync(credsPath)) {
    return { authenticated: false, reason: 'Granola credentials not found (is Granola installed and signed in?)' };
  }

  try {
    const data = JSON.parse(fs.readFileSync(credsPath, 'utf-8'));
    const workosTokens = JSON.parse(data.workos_tokens || '{}');
    const token = workosTokens.access_token;

    if (!token) {
      return { authenticated: false, reason: 'No access token in Granola credentials — try signing out and back in to Granola' };
    }

    // Write a marker so install-automation.sh knows auth is confirmed
    const dexConfigDir = path.join(os.homedir(), '.config/dex');
    if (!fs.existsSync(dexConfigDir)) {
      fs.mkdirSync(dexConfigDir, { recursive: true });
    }
    fs.writeFileSync(
      path.join(dexConfigDir, 'granola-tokens.json'),
      JSON.stringify({ source: 'granola-supabase', verified: new Date().toISOString() }, null, 2)
    );

    return { authenticated: true };
  } catch (e) {
    return { authenticated: false, reason: `Could not parse Granola credentials: ${e.message}` };
  }
}

const args = process.argv.slice(2);
const isSetup = args.includes('--setup');
const isStatus = args.includes('--status');

if (isStatus) {
  const result = checkAuth();
  if (result.authenticated) {
    console.log(`${GREEN}✓${NC} Granola: authenticated (credentials found in Granola app data)`);
    process.exit(0);
  } else {
    console.log(`${YELLOW}!${NC} Granola: not authenticated — ${result.reason}`);
    process.exit(1);
  }
} else if (isSetup) {
  console.log('Checking Granola authentication...');
  const result = checkAuth();

  if (result.authenticated) {
    console.log(`${GREEN}✓${NC} Granola is already authenticated.`);
    console.log('  Credentials are managed by the Granola desktop app — no separate sign-in needed.');
    process.exit(0);
  } else {
    console.log(`${YELLOW}!${NC} ${result.reason}`);
    console.log('');
    console.log('To authenticate:');
    console.log('  1. Download and install Granola from https://granola.ai');
    console.log('  2. Sign in to Granola with your work account');
    console.log('  3. Record or import a meeting so the cache is populated');
    console.log('  4. Re-run this setup');
    console.log('');
    console.log('The background sync will work once Granola is installed and signed in.');
    // Exit 0 so install-automation.sh continues with cache-only mode
    process.exit(0);
  }
} else {
  // Default: just check and report
  const result = checkAuth();
  if (result.authenticated) {
    console.log(`${GREEN}✓${NC} Granola authenticated`);
    process.exit(0);
  } else {
    console.log(`${YELLOW}!${NC} ${result.reason}`);
    process.exit(1);
  }
}