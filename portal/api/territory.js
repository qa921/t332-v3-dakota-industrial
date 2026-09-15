const crypto = require('node:crypto');

// Backend base URL is server-side only and never sent to the browser.
const BACKEND_URL = process.env.BACKEND_URL || 'https://t332-v3-dakota-industrial.onrender.com';
const CUSTOMER_GUIDANCE = 'Nearby property data is temporarily unavailable. Please try again in a few minutes, or adjust the search radius or minimum building age. If the problem continues, contact support.';

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store'); res.setHeader('X-Content-Type-Options', 'nosniff');
  const raw = req.headers.authorization || ''; let supplied = '';
  try { supplied = raw.startsWith('Basic ') ? Buffer.from(raw.slice(6), 'base64').toString('utf8') : ''; } catch {}
  const expected = 'contributor:' + process.env.ACCESS_TOKEN;
  const same = process.env.ACCESS_TOKEN && crypto.timingSafeEqual(crypto.createHash('sha256').update(supplied).digest(), crypto.createHash('sha256').update(expected).digest());
  if (!same) { res.setHeader('WWW-Authenticate', 'Basic realm="Contributor prerequisite", charset="UTF-8"'); return res.status(401).json({ error: 'unauthorized' }); }
  try {
    const query = new URL(req.url, 'https://portal.local').search;
    const upstream = await fetch(BACKEND_URL + '/api/territory' + query, { headers: { Authorization: 'Bearer ' + process.env.ACCESS_TOKEN } });
    const body = await upstream.json().catch(() => null);
    if (!body || typeof body !== 'object') {
      return res.status(503).json({ available: false, reason: CUSTOMER_GUIDANCE, properties: [] });
    }
    if (upstream.status !== 200) {
      const safeReason = (typeof body.reason === 'string' && !/https?:\/\//i.test(body.reason)) ? body.reason : CUSTOMER_GUIDANCE;
      return res.status(503).json({ available: false, reason: safeReason, properties: [] });
    }
    return res.status(200).json(body);
  } catch (e) {
    return res.status(503).json({ available: false, reason: CUSTOMER_GUIDANCE, properties: [] });
  }
};
