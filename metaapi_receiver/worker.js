// SMC Structure Strategy - MetaApi receiver  -  v1.0
// A Cloudflare Worker that takes the strategy's TradingView alerts (TheConnector message format, unchanged) and trades
// them on your MT5 account through MetaApi (metaapi.cloud). No MT5 terminal, no VPS, no laptop.
//
//   TradingView alert  ->  https://<your-worker>.workers.dev/<SECRET>  ->  this code  ->  MetaApi  ->  FxPro MT5
//
// Messages it understands (exactly what the strategy sends with group 22 "Message format" = TheConnector):
//   open : {"action":"buy"|"sell","symbol":"XAUUSD","volume":0.05,"sl_price":4290.1,"tp_price":4330.5,"tag":"smcgold-k3f9"}
//   close: {"action":"closelong"|"closeshort","symbol":"XAUUSD","tag":"smcgold-k3f9"}
// Each trade is opened with its tag as MetaApi's clientId, and a close closes ONLY the position carrying that tag
// (all positions of that side and symbol when the message has no tag, like TheConnector).
//
// Settings (Cloudflare -> your Worker -> Settings -> Variables and Secrets). SECRETS are never shown again:
//   SECRET            secret   the last part of your webhook URL - long and random (e.g. 32 letters and digits)
//   METAAPI_TOKEN     secret   your MetaApi API token
//   ACCOUNT_ID        text     your MetaApi account id (MetaApi dashboard -> Accounts)
//   REGION            text     your MetaApi account's region, e.g. new-york, london
//   MAX_LOTS          text     refuse any single order above this many lots (default 1)
//   DRY_RUN           text     1 = log what it would do, send no order (default 0)
//   TV_IPS_ONLY       text     1 = accept only TradingView's webhook addresses (default 1)
//   SYMBOL_MAP        text     optional, e.g. {"XAUUSD":"GOLD","EURUSD":"EURUSD.r"} when FxPro spells a symbol differently
//   TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID   secrets, optional: a Telegram message on every problem
//   NOTIFY_TRADES     text     1 = also a Telegram message on every order sent (default 0)
//   DOMAIN            text     MetaApi's domain (default agiliumtrade.ai) - leave it
// Optional KV namespace binding named SEEN: remembers every message for 2 days, so a repeated alert is never traded twice.

const TV_IPS = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"];
const OK_CODES = ["ERR_NO_ERROR", "TRADE_RETCODE_PLACED", "TRADE_RETCODE_DONE", "TRADE_RETCODE_DONE_PARTIAL", "TRADE_RETCODE_NO_CHANGES"];
const CLOSE_WAITS = [0, 1500, 3000, 5000, 8000];   // a close that finds nothing looks again (its open may still be on its way)

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const parts = url.pathname.split("/").filter(Boolean);
    if (!env.SECRET || !parts.length || !same(parts[0], env.SECRET)) return text(404, "not found");

    // GET /<SECRET>/health - open it in a browser to check the whole chain up to MetaApi (no order is sent)
    if (request.method === "GET" && parts[1] === "health") {
      try {
        const info = await api(env, "GET", "/account-information");
        const pos = await api(env, "GET", "/positions");
        return json(200, { ok: true, dryRun: flag(env.DRY_RUN, false), maxLots: maxLots(env), broker: info.broker, server: info.server,
          currency: info.currency, balance: info.balance, equity: info.equity, openPositions: Array.isArray(pos) ? pos.length : null });
      } catch (e) {
        return json(502, { ok: false, error: String(e.message || e) });
      }
    }
    if (request.method !== "POST") return text(405, "POST only");

    const ip = request.headers.get("CF-Connecting-IP") || "";
    if (flag(env.TV_IPS_ONLY, true) && !TV_IPS.includes(ip)) {
      log("REJECTED: not a TradingView address", { ip });
      ctx.waitUntil(notify(env, "Rejected a webhook from " + ip + " (not TradingView)."));
      return text(403, "forbidden");
    }
    const body = await request.text();
    if (body.length > 4000) return text(413, "too large");
    let msg;
    try { msg = parse(body); } catch (e) {
      log("REJECTED: " + e.message, { body: redact(body) });
      ctx.waitUntil(notify(env, "Rejected an alert: " + e.message + "\n" + redact(body)));
      return text(400, e.message);
    }
    // TradingView waits at most 3 seconds - answer now, trade right after
    ctx.waitUntil(handle(env, msg).catch(e => {
      log("ERROR " + (e.message || e), { msg });
      return notify(env, "ERROR on " + describe(msg) + ": " + (e.message || e));
    }));
    return text(200, "accepted");
  }
};

// ---------------------------------------------------------------------------------------------------- the message
function parse(body) {
  let m;
  try { m = JSON.parse(body); } catch (e) { throw new Error("not JSON - set group 22 'Message format' to TheConnector"); }
  if (!m || typeof m !== "object") throw new Error("empty message");
  const action = String(m.action || "").toLowerCase();
  const symbol = String(m.symbol || "").trim();
  const tag = m.tag === undefined || m.tag === null ? "" : String(m.tag).trim();
  if (!symbol) throw new Error("no symbol");
  if (action === "buy" || action === "sell") {
    if (m.sl_price === undefined && m.sl !== undefined) throw new Error("stop sent as 'sl' - set group 30 'TheConnector stop / target fields' to 'sl_price / tp_price'");
    const volume = Number(m.volume), sl = Number(m.sl_price), tp = Number(m.tp_price);
    if (!(volume > 0)) throw new Error("volume missing or 0");
    if (!(sl > 0) || !(tp > 0)) throw new Error("no stop or no target - an order is never sent without both");
    if (action === "buy" && !(sl < tp)) throw new Error("buy with the stop above the target");
    if (action === "sell" && !(sl > tp)) throw new Error("sell with the stop below the target");
    return { kind: "open", side: action === "buy" ? 1 : -1, symbol, volume, sl, tp, tag };
  }
  if (action === "closelong" || action === "closeshort") return { kind: "close", side: action === "closelong" ? 1 : -1, symbol, tag };
  throw new Error("unknown action '" + action + "'");
}

// MetaApi keeps the clientId in the MT5 comment: letters, digits and _ only, 26 characters at most
function clientId(tag) {
  return String(tag).replace(/[^A-Za-z0-9_]/g, "_").slice(0, 26);
}

// ---------------------------------------------------------------------------------------------------- trading
async function handle(env, m) {
  const sym = mapSymbol(env, m.symbol);
  const cid = m.tag ? clientId(m.tag) : "";
  const key = m.kind + ":" + m.side + ":" + sym + ":" + cid + (m.kind === "open" ? ":" + m.volume + ":" + m.sl + ":" + m.tp : "");
  if (env.SEEN && m.tag) {
    if (await env.SEEN.get(key)) { log("SKIPPED: the same alert arrived twice", { msg: m }); return "duplicate"; }
    await env.SEEN.put(key, "1", { expirationTtl: 2 * 86400 });
  }
  return m.kind === "open" ? openTrade(env, m, sym, cid) : closeTrade(env, m, sym, cid);
}

async function openTrade(env, m, sym, cid) {
  if (m.volume > maxLots(env)) {
    log("REFUSED: " + m.volume + " lots is above MAX_LOTS " + maxLots(env), { msg: m });
    await notify(env, "REFUSED " + describe(m) + ": " + m.volume + " lots is above MAX_LOTS " + maxLots(env) + ". Check group 22 'Quantity to send' (Lots).");
    return "refused";
  }
  if (cid) {
    const open = await positions(env);
    if (open.some(p => mine(p, cid))) { log("SKIPPED: a position with this tag is already open", { msg: m }); return "duplicate"; }
  }
  const trade = { actionType: m.side === 1 ? "ORDER_TYPE_BUY" : "ORDER_TYPE_SELL", symbol: sym, volume: m.volume, stopLoss: m.sl, takeProfit: m.tp };
  if (cid) trade.clientId = cid;
  if (flag(env.DRY_RUN, false)) { log("DRY RUN - would send", { trade }); return "dry"; }
  try {
    const r = await tradeCall(env, trade);
    log("OPENED " + describe(m), { positionId: r.positionId, orderId: r.orderId, code: r.stringCode });
    if (flag(env.NOTIFY_TRADES, false)) await notify(env, "Opened " + describe(m) + " " + m.volume + " lots, SL " + m.sl + " TP " + m.tp);
    return "opened";
  } catch (e) {
    // the answer may have been lost while the order went through: look before calling it a failure
    if (cid) {
      const open = await positions(env).catch(() => []);
      if (open.some(p => mine(p, cid))) { log("OPENED (confirmed after an error: " + e.message + ")", { msg: m }); return "opened"; }
    }
    throw new Error("open failed: " + e.message);
  }
}

async function closeTrade(env, m, sym, cid) {
  for (let i = 0; i < CLOSE_WAITS.length; i++) {
    if (CLOSE_WAITS[i]) await sleep(env, CLOSE_WAITS[i]);
    const open = (await positions(env)).filter(p => p.symbol === sym && side(p) === m.side && (!cid || mine(p, cid)));
    if (!open.length) continue;
    if (flag(env.DRY_RUN, false)) { log("DRY RUN - would close", { ids: open.map(p => p.id) }); return "dry"; }
    const errs = [];
    for (const p of open) {
      try { await tradeCall(env, { actionType: "POSITION_CLOSE_ID", positionId: String(p.id) }); log("CLOSED " + describe(m), { positionId: p.id }); }
      catch (e) { errs.push(p.id + ": " + e.message); }
    }
    if (errs.length) throw new Error("close failed for " + errs.join("; "));
    if (flag(env.NOTIFY_TRADES, false)) await notify(env, "Closed " + describe(m));
    return "closed";
  }
  // normal when FxPro's own stop or target closed it first
  log("NOTHING TO CLOSE (already closed at the broker)", { msg: m });
  return "none";
}

// ---------------------------------------------------------------------------------------------------- MetaApi
async function api(env, method, path, body) {
  if (!env.METAAPI_TOKEN || !env.ACCOUNT_ID || !env.REGION) throw new Error("METAAPI_TOKEN, ACCOUNT_ID or REGION is not set");
  const base = "https://mt-client-api-v1." + env.REGION + "." + (env.DOMAIN || "agiliumtrade.ai");
  const res = await fetch(base + "/users/current/accounts/" + encodeURIComponent(env.ACCOUNT_ID) + path, {
    method, headers: { "auth-token": env.METAAPI_TOKEN, "content-type": "application/json", accept: "application/json" },
    body: body ? JSON.stringify(body) : undefined
  });
  const txt = await res.text();
  let data = null;
  try { data = txt ? JSON.parse(txt) : null; } catch (e) { data = null; }
  if (!res.ok) throw new Error("MetaApi " + res.status + " " + ((data && (data.message || data.error)) || txt.slice(0, 200)));
  return data;
}
async function positions(env) {
  const p = await api(env, "GET", "/positions");
  return Array.isArray(p) ? p : [];
}
async function tradeCall(env, trade) {
  const r = (await api(env, "POST", "/trade", trade)) || {};
  const code = r.stringCode || r.description;
  if (!OK_CODES.includes(code)) throw new Error((code || "no answer") + (r.message ? " - " + r.message : ""));
  return r;
}
function mine(p, cid) {
  return p.clientId === cid || String(p.comment || "").includes(cid) || String(p.brokerComment || "").includes(cid);
}
function side(p) { return p.type === "POSITION_TYPE_BUY" ? 1 : p.type === "POSITION_TYPE_SELL" ? -1 : 0; }

// ---------------------------------------------------------------------------------------------------- small helpers
function mapSymbol(env, s) {
  if (!env.SYMBOL_MAP) return s;
  try { const m = JSON.parse(env.SYMBOL_MAP); return m[s] || s; } catch (e) { return s; }
}
function maxLots(env) { const v = Number(env.MAX_LOTS); return v > 0 ? v : 1; }
function flag(v, dflt) { return v === undefined || v === null || v === "" ? dflt : String(v) === "1" || String(v).toLowerCase() === "true"; }
function same(a, b) {   // compare without an early exit, so the secret cannot be guessed from the answer time
  a = String(a); b = String(b);
  let d = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) d |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return d === 0;
}
function redact(s) { return String(s).replace(/"accessKey"\s*:\s*"[^"]*"/g, '"accessKey":"***"').slice(0, 500); }
function describe(m) { return (m.kind === "open" ? (m.side === 1 ? "BUY " : "SELL ") : (m.side === 1 ? "CLOSE LONG " : "CLOSE SHORT ")) + m.symbol + (m.tag ? " [" + m.tag + "]" : ""); }
function log(what, extra) { console.log(JSON.stringify(Object.assign({ t: new Date().toISOString(), what }, extra || {}))); }
function sleep(env, ms) { return new Promise(r => setTimeout(r, env.__FAST ? ms / 20 : ms)); }   // __FAST: tests only
function text(status, s) { return new Response(s, { status, headers: { "content-type": "text/plain" } }); }
function json(status, o) { return new Response(JSON.stringify(o, null, 1), { status, headers: { "content-type": "application/json" } }); }
async function notify(env, s) {
  if (!env.TELEGRAM_BOT_TOKEN || !env.TELEGRAM_CHAT_ID) return;
  try {
    await fetch("https://api.telegram.org/bot" + env.TELEGRAM_BOT_TOKEN + "/sendMessage", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ chat_id: env.TELEGRAM_CHAT_ID, text: "SMC receiver: " + s })
    });
  } catch (e) { log("telegram failed", { error: String(e) }); }
}
