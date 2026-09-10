const fs = require('fs');
const path = require('path');
const http = require('http');
const { spawn, spawnSync } = require('child_process');

const root = path.resolve(__dirname, '..');
const agent = path.join(root, 'engines', 'agenttube');
const { google } = require(path.join(agent, 'node_modules', 'googleapis'));

const slug = process.argv[2];
const expected = process.argv.slice(3).join(' ') || slug;

if (!slug) {
  console.error('Missing YouTube profile slug.');
  process.exit(2);
}

const clientId = process.env.YOUTUBE_CLIENT_ID;
const clientSecret = process.env.YOUTUBE_CLIENT_SECRET;
const redirectUri = process.env.YOUTUBE_REDIRECT_URI || 'http://localhost:8080/oauth2callback';

if (!clientId || !clientSecret) {
  console.error('Missing saved YouTube OAuth credentials.');
  process.exit(2);
}

const outDir = path.join(root, 'account-profiles', 'youtube', slug);
fs.mkdirSync(outDir, { recursive: true });

const oauth = new google.auth.OAuth2(clientId, clientSecret, redirectUri);

const scopes = [
  'https://www.googleapis.com/auth/youtube.upload',
  'https://www.googleapis.com/auth/youtube',
  'https://www.googleapis.com/auth/youtube.readonly',
  'https://www.googleapis.com/auth/yt-analytics.readonly',
  'https://www.googleapis.com/auth/youtube.force-ssl'
];

const authUrl = oauth.generateAuthUrl({
  access_type: 'offline',
  prompt: 'consent select_account',
  scope: scopes
});

const env = { ...process.env, OAUTH_URL: authUrl };

// Copy URL to Windows clipboard so the user never has to Ctrl+C the terminal.
try {
  spawnSync(
    'powershell.exe',
    ['-NoProfile', '-Command', 'Set-Clipboard -Value $env:OAUTH_URL'],
    { env, stdio: 'ignore' }
  );
} catch (_) {}

// Try to open Chrome/default browser without blocking this callback server.
try {
  const p = spawn(
    'powershell.exe',
    ['-NoProfile', '-Command', 'Start-Process $env:OAUTH_URL'],
    { env, detached: true, stdio: 'ignore' }
  );
  p.unref();
} catch (_) {}

console.log('');
console.log('============================================================');
console.log(` AUTHORIZE: ${expected}`);
console.log('============================================================');
console.log('The Google authorization URL is already copied to your clipboard.');
console.log('');
console.log('If the browser did not open automatically:');
console.log('  1. Open Chrome.');
console.log('  2. Click the address bar.');
console.log('  3. Press Ctrl+V.');
console.log('  4. Press Enter.');
console.log('');
console.log(`Choose the Google account for: ${expected}`);
console.log('Do NOT press Ctrl+C in this terminal.');
console.log('Waiting for Google to return to localhost...');
console.log('');

const server = http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, 'http://localhost:8080');

    if (u.pathname !== '/oauth2callback') {
      res.end('Waiting for Google OAuth callback...');
      return;
    }

    const error = u.searchParams.get('error');
    if (error) throw new Error(`Google returned: ${error}`);

    const code = u.searchParams.get('code');
    if (!code) throw new Error('No authorization code returned.');

    const { tokens } = await oauth.getToken(code);
    oauth.setCredentials(tokens);

    const youtube = google.youtube({ version: 'v3', auth: oauth });
    const response = await youtube.channels.list({
      part: ['snippet'],
      mine: true
    });

    const channel = response.data.items?.[0];
    if (!channel) throw new Error('Authorization succeeded but no YouTube channel was returned.');

    const title = channel.snippet?.title || 'UNKNOWN';
    const id = channel.id || 'UNKNOWN';

    fs.writeFileSync(
      path.join(outDir, 'tokens.json'),
      JSON.stringify({ youtube: tokens }, null, 2)
    );

    fs.writeFileSync(
      path.join(outDir, 'channel.json'),
      JSON.stringify({ expected, title, id }, null, 2)
    );

    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(
      `<h2>YouTube authorization saved</h2>` +
      `<p><b>${title}</b></p>` +
      `<p>You can close this tab and return to Git Bash.</p>`
    );

    console.log('AUTHORIZED SUCCESSFULLY');
    console.log(`Expected profile: ${expected}`);
    console.log(`Actual channel:    ${title}`);
    console.log(`Channel ID:        ${id}`);
    console.log('');

    server.close(() => process.exit(0));
  } catch (err) {
    console.error('');
    console.error('AUTHORIZATION FAILED:', err.message);
    res.statusCode = 500;
    res.end('Authorization failed. Return to the terminal.');
    server.close(() => process.exit(2));
  }
});

server.on('error', err => {
  console.error('OAuth callback server failed:', err.message);
  process.exit(2);
});

server.listen(8080, '127.0.0.1');
