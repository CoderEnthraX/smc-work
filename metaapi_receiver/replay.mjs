// Replays the strategy's own alert stream (from the simulator, TheConnector format) through worker.js and a fake MetaApi
// broker that also closes trades by itself at their ORIGINAL stop or target, like FxPro. After every alert (or every
// candle, in the "same candle at once" run) the broker's open trades must be exactly TradingView's open trades.
//   node replay.mjs <replay_stream.json>
import fs from "fs";
import worker from "./worker.js";
const clientId = tag => String(tag).replace(/[^A-Za-z0-9_]/g, "_").slice(0, 26);   // the same rule as in worker.js
const streams = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
let bad = 0, total = 0;
function broker() {
  const B = { positions: [], telegram: [], orders: 0, nextId: 1 };
  B.fetch = async (url, init = {}) => {
    const u = new URL(url);
    if (u.hostname === "api.telegram.org") { B.telegram.push(JSON.parse(init.body).text); return new Response("{}"); }
    const p = u.pathname.replace("/users/current/accounts/acc1", "");
    await new Promise(r => setTimeout(r, Math.random() * 3));                // network jitter
    if (init.method === "GET" && p === "/positions") return new Response(JSON.stringify(B.positions));
    const t = JSON.parse(init.body);
    if (t.actionType === "ORDER_TYPE_BUY" || t.actionType === "ORDER_TYPE_SELL") {
      B.orders++; const id = String(B.nextId++);
      B.positions.push({ id, type: t.actionType === "ORDER_TYPE_BUY" ? "POSITION_TYPE_BUY" : "POSITION_TYPE_SELL", symbol: t.symbol, volume: t.volume, clientId: t.clientId, stopLoss: t.stopLoss, takeProfit: t.takeProfit });
      return new Response(JSON.stringify({ stringCode: "TRADE_RETCODE_DONE", positionId: id }));
    }
    if (t.actionType === "POSITION_CLOSE_ID") {
      const i = B.positions.findIndex(x => x.id === t.positionId);
      if (i < 0) return new Response(JSON.stringify({ stringCode: "TRADE_RETCODE_INVALID", message: "gone" }));
      B.positions.splice(i, 1); return new Response(JSON.stringify({ stringCode: "TRADE_RETCODE_DONE" }));
    }
    return new Response("{}", { status: 400 });
  };
  return B;
}
async function send(env, body) {
  const w = []; globalThis.fetch = env.__B.fetch;
  const res = await worker.fetch(new Request("https://x.workers.dev/k", { method: "POST", body, headers: { "CF-Connecting-IP": "52.89.214.238" } }), env, { waitUntil: p => w.push(p) });
  await Promise.all(w); return res.status;
}
const origLog = console.log; console.log = () => {};                         // the receiver's own log lines
for (const concurrent of [false, true]) {
  for (const s of streams) {
    const B = broker(); const kv = new Map();
    const env = { __B: B, __FAST: true, SECRET: "k", METAAPI_TOKEN: "t", ACCOUNT_ID: "acc1", REGION: "london", MAX_LOTS: "100", TELEGRAM_BOT_TOKEN: "b", TELEGRAM_CHAT_ID: "1",
                  SEEN: { get: async k => kv.get(k) || null, put: async (k, v) => kv.set(k, v) } };
    const tagOf = {}; const tvOpen = new Set(); let mism = 0, statusBad = 0;
    const cmp = () => { const bo = new Set(B.positions.map(p => p.clientId)); const tv = new Set([...tvOpen].map(id => clientId(tagOf[id])));
      if (bo.size !== tv.size || [...tv].some(x => !bo.has(x))) mism++; };
    const byBar = new Map();
    for (const e of s.events) { if (!byBar.has(e.bar)) byBar.set(e.bar, []); byBar.get(e.bar).push(e); }
    for (const [bar, evs] of byBar) {
      const jobs = [];
      for (const e of evs) {
        if (e.type === "entry") { tagOf[e.id] = JSON.parse(e.msg).tag; tvOpen.add(e.id); }
        else {
          tvOpen.delete(e.id);
          if (e.brokerClosesItself) { const i = B.positions.findIndex(p => p.clientId === clientId(tagOf[e.id])); if (i >= 0) B.positions.splice(i, 1); }
        }
        const job = send(env, e.msg).then(st => { if (st !== 200) statusBad++; });
        if (concurrent) jobs.push(job); else { await job; cmp(); }
      }
      if (concurrent) { await Promise.all(jobs); cmp(); }
    }
    total++;
    const ok = mism === 0 && statusBad === 0 && B.telegram.length === 0 && B.positions.length === s.openAtEnd.length;
    if (!ok) bad++;
    origLog((ok ? "  ok   " : "  FAIL ") + (concurrent ? "[same candle at once] " : "[one by one]          ") + s.name.padEnd(30) + s.events.length + " alerts, " + B.orders + " orders, mismatches " + mism + ", telegram " + B.telegram.length + ", open at end " + B.positions.length);
  }
}
origLog("\n" + (total - bad) + " of " + total + " replays: the broker always held exactly TradingView's open trades");
process.exit(bad ? 1 : 0);
