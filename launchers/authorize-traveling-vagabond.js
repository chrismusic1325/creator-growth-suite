const fs = require('fs');
const path = require('path');
const http = require('http');
const root = path.resolve(__dirname, '..');
const agent = path.join(root, 'engines', 'agenttube');
const { google } = require(path.join(agent, 'node_modules', 'googleapis'));
const clientId = process.env.YOUTUBE_CLIENT_ID;
const clientSecret = process.env.YOUTUBE_CLIENT_SECRET;
const redirectUri = 'http://localhost:8080/oauth2callback';
const outDir = path.join(root, 'account-profiles', 'youtube', 'traveling-vagabond');
fs.mkdirSync(outDir, { recursive: true });
const oauth = new google.auth.OAuth2(clientId, clientSecret, redirectUri);
const scopes = [
  'https://www.googleapis.com/auth/youtube.upload',
  'https://www.googleapis.com/auth/youtube',
  'https://www.googleapis.com/auth/youtube.readonly',
  'https://www.googleapis.com/auth/yt-analytics.readonly',
  'https://www.googleapis.com/auth/youtube.force-ssl'
];
const authUrl = oauth.generateAuthUrl({ access_type: 'offline', prompt: 'consent select_account', scope: scopes });
console.log('\nCOPY THIS URL INTO CHROME:\n');
console.log(authUrl);
console.log('');
const server = http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, 'http://localhost:8080');
    if (u.pathname !== '/oauth2callback') { res.end('Waiting for OAuth callback...'); return; }
    const code = u.searchParams.get('code');
    if (!code) throw new Error('No authorization code returned.');
    const { tokens } = await oauth.getToken(code);
    oauth.setCredentials(tokens);
    const yt = google.youtube({ version: 'v3', auth: oauth });
    const response = await yt.channels.list({ part: ['snippet'], mine: true });
    const channel = response.data.items?.[0];
    const title = channel?.snippet?.title || 'UNKNOWN';
    const id = channel?.id || 'UNKNOWN';
    fs.writeFileSync(path.join(outDir, 'tokens.json'), JSON.stringify({ youtube: tokens }, null, 2));
    fs.writeFileSync(path.join(outDir, 'channel.json'), JSON.stringify({ title, id }, null, 2));
    fs.writeFileSync(path.join(agent, 'config', 'tokens.json'), JSON.stringify({ youtube: tokens }, null, 2));
    fs.writeFileSync(path.join(root, 'runtime', 'active-youtube-channel.txt'), 'traveling-vagabond\n');
    res.writeHead(200, {'Content-Type':'text/html'});
    res.end(`<h2>Authorized successfully.</h2><p>${title}</p><p>You can close this tab.</p>`);
    console.log(`AUTHORIZED CHANNEL: ${title} (${id})`);
    console.log('Traveling Vagabond 7 is now the default AgentTube profile.');
    server.close(() => process.exit(0));
  } catch (err) {
    console.error('OAuth failed:', err.message);
    res.statusCode = 500;
    res.end('OAuth failed. Return to the terminal.');
    server.close(() => process.exit(2));
  }
});
server.listen(8080, '127.0.0.1', () => {
  console.log('Waiting for Google authorization callback on http://localhost:8080/oauth2callback');
});
