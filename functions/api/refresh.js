/**
 * POST /api/refresh — spustí nový build Pages projektu.
 *
 * Proměnné projektu (Settings → Variables and secrets, typ Secret):
 *   DEPLOY_HOOK       URL deploy hooku "manual"
 *   REFRESH_PASSWORD  heslo, které se zadává na webu
 *
 * Volitelně: KV binding pojmenovaný RL zapne limit 1 build / 5 minut.
 */

const COOLDOWN_MS = 5 * 60 * 1000;

function json(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function onRequest({ request, env }) {
  if (request.method !== "POST") return json({ error: "method_not_allowed" }, 405);

  if (!env.DEPLOY_HOOK || !env.REFRESH_PASSWORD) {
    return json({ error: "not_configured" }, 500);
  }

  if (!safeEqual(request.headers.get("X-Refresh-Key") || "", env.REFRESH_PASSWORD)) {
    return json({ error: "unauthorized" }, 401);
  }

  if (env.RL) {
    const last = Number(await env.RL.get("last")) || 0;
    const waited = Date.now() - last;
    if (last && waited < COOLDOWN_MS) {
      return json(
        { error: "rate_limited", retry_after: Math.ceil((COOLDOWN_MS - waited) / 1000) },
        429
      );
    }
  }

  const r = await fetch(env.DEPLOY_HOOK, { method: "POST" });
  if (!r.ok) return json({ error: "hook_failed", status: r.status }, 502);

  if (env.RL) await env.RL.put("last", String(Date.now()), { expirationTtl: 600 });

  return json({ ok: true }, 200);
}
