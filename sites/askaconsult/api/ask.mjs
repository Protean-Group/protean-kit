// ASKA terminal showcase assistant — Vercel serverless function
// Holds the OpenRouter key server-side (never ships to the browser).
// Showcase assistant: explains what ASKA does, routes to contact. It is NOT
// ASKA answering for real — the honesty guard from the terminal is the spine.
//
// Rate limiting: durable token-bucket via Upstash Redis REST API.
// Falls back to 503 if KV credentials are not configured.
// Uses HTTP POST to Upstash (no npm package required).
const OPENROUTER_KEY = process.env.OPENROUTER_KEY || process.env.OPENROUTER_API_KEY;
const MODEL = process.env.ASKA_MODEL || 'openai/gpt-4o-mini';
const UPSTASH_KV_REST_URL = process.env.UPSTASH_KV_REST_URL;
const UPSTASH_KV_REST_TOKEN = process.env.UPSTASH_KV_REST_TOKEN;
const RATE_LIMIT = 10; // requests per window
const RATE_WINDOW_SEC = 60;

function ipFromRequest(req) {
  return (
    req.headers['x-forwarded-for']?.split(',')[0]?.trim() ||
    req.headers['x-real-ip'] ||
    'unknown'
  );
}

// Durable rate limiter using Upstash KV (REST API, no package needed).
// Falls back to DENY if credentials are absent.
async function rateLimit(ip) {
  if (!UPSTASH_KV_REST_URL || !UPSTASH_KV_REST_TOKEN) {
    // No KV configured — allow up to RATE_LIMIT requests in-memory as a best-effort
    // fallback (only protects sequential requests within a single warm Lambda).
    // For production use, set UPSTASH_KV_REST_URL + UPSTASH_KV_REST_TOKEN.
    const now = Date.now();
    const record = rateLimiterInMemory.get(ip);
    if (!record || now - record.start > RATE_WINDOW_SEC * 1000) {
      rateLimiterInMemory.set(ip, { count: 1, start: now });
      return null;
    }
    if (record.count >= RATE_LIMIT) {
      const retryAfter = Math.ceil(
        (RATE_WINDOW_SEC * 1000 - (now - record.start)) / 1000
      );
      return retryAfter;
    }
    record.count++;
    return null;
  }

  // Durable path: Upstash KV REST API
  const key = `rl:${ip}`;
  try {
    const res = await fetch(`${UPSTASH_KV_REST_URL}/incr`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${UPSTASH_KV_REST_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ key, amount: 1, ttl: RATE_WINDOW_SEC }),
    });
    if (!res.ok) return null; // allow on KV error (fail open)
    const data = await res.json();
    if ((data.value || 0) > RATE_LIMIT) {
      return RATE_WINDOW_SEC;
    }
    return null;
  } catch {
    return null; // fail open on network error
  }
}

// In-memory fallback (best-effort only)
const rateLimiterInMemory = new Map();

const SYSTEM_PROMPT = [
  'You are the ASKA capability-showcase assistant inside an interactive terminal on the ASKA Consulting website (askaconsult.com).',
  'ASKA is one firm, two divisions:',
  '- ASKA Digital: emerging technology consulting (agentic AI adoption, blockchain diligence, additive manufacturing), digital infrastructure (data centres and crypto mining from feasibility through commissioning to operations), and financial advisory (venture raises, cap table structuring, balance sheet management, tax optimization, corporate restructuring).',
  '- ASKA Physical: global building-material sourcing and procurement consulting (raw material or finished goods), manufacturer-distributor matchmaking, negotiation-as-a-service.',
  '- Contact: email info@askaconsult.com, phone +1-289-928-9554 (tel:289-928-9554). When asked for contact details, give these exactly.',
  '- Rules: answer only about ASKA and its services; for anything else say you are the ASKA capability demo and redirect to /help. You are a product showcase, not the firm — never give financial/legal/technical advice, never quote prices/terms, never invent track-record numbers, clients, or credentials.',
  '- Keep answers to 2-4 short lines. Plain text, no markdown headers.',
  '- Mention "Book a consultation" or the appropriate division page as the next step when relevant.',
  '- Add "→ scheduled: intro call — we map this to your actual situation" ONLY when the user expresses genuine interest in working with ASKA or asks for next steps. Do NOT append it to every answer — for simple informational questions (what do you do, what is ASKA, explain a service), answer directly and end with a suggestion like "Try /digital or /physical to explore."',
].join('\n');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const ip = ipFromRequest(req);
  const denied = await rateLimit(ip);
  if (denied !== null) {
    res.setHeader('Retry-After', denied);
    return res.status(429).json({ error: 'Too many requests. Please wait a moment.' });
  }

  if (!OPENROUTER_KEY) {
    return res.status(503).json({ error: 'Assistant not configured' });
  }

  const { q } = req.body || {};
  if (!q || typeof q !== 'string' || q.trim().length === 0) {
    return res.status(400).json({ error: 'Empty query' });
  }
  if (q.length > 500) {
    return res.status(400).json({ error: 'Query too long' });
  }

  try {
    const r = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${OPENROUTER_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: q },
        ],
        max_tokens: 220,
        temperature: 0.4,
      }),
    });

    if (!r.ok) {
      return res.status(502).json({ error: 'Upstream error' });
    }
    const data = await r.json();
    const answer = data?.choices?.[0]?.message?.content?.trim() || '(no response)';
    return res.status(200).json({ a: answer });
  } catch (e) {
    return res.status(500).json({ error: 'Assistant error' });
  }
}
