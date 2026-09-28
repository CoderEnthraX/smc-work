// Tests for worker.js against a FAKE MetaApi (no network). Run:  node test.mjs
import worker from "./worker.js";
const clientId = tag => String(tag).replace(/[^A-Za-z0-9_]/g, "_").slice(0, 26);   // the same rule as in worker.js

const TV = "52.89.214.238";
let fails = 0, passes = 0;
function check(name, cond, extra) {
  if (cond) { passes++; console.log("  ok   " + name); }
  else { fails++; console.log("  FAIL " + name + (extra ? "  " + JSON.stringify(extra) : "")); }
}

// ---------------------------------------------------------------- fake MetaApi + Telegram
function fakeBroker(opts = {}) {
  const B = { positions: [], calls: [], telegram: [], nextId: 1000, opts, kv: new Map() };
  B.fetch = async (url, init = {}) => {
    const u = new URL(url);
    if (u.hostname === "api.telegram.org") { B.telegram.push(JSON.parse(init.body).text); return new Response("{}"); }
    B.calls.push({ method: init.method, path: u.pathname, host: u.hostname, headers: init.headers, body: init.body ? JSON.parse(init.body) : null });
    if (init.headers["auth-token"] !== "tok") return new Response(JSON.stringify({ message: "unauthorized" }), { status: 401 });
    const p = u.pathname.replace("/users/current/accounts/acc1", "");
    if (init.method === "GET" && p === "/positions") return new Response(JSON.stringify(B.positions));
    if (init.method === "GET" && p === "/account-information") return new Response(JSON.stringify({ broker: "FxPro", server: "FxPro-MT5", currency: "USD", balance: 10000, equity: 10000 }));
    if (init.method === "POST" && p === "/trade") {
      const t = JSON.parse(init.body);
      if (B.opts.delayOpen && t.actionType.startsWith("ORDER_TYPE")) await new Promise(r => setTimeout(r, B.opts.delayOpen));
      if (B.opts.reject) return new Response(JSON.stringify({ numericCode: 10019, stringCode: "TRADE_RETCODE_NO_MONEY", message: "No money" }));
      if (t.actionType === "ORDER_TYPE_BUY" || t.actionType === "ORDER_TYPE_SELL") {
        const id = String(B.nextId++);
        B.positions.push({ id, type: t.actionType === "ORDER_TYPE_BUY" ? "POSITION_TYPE_BUY" : "POSITION_TYPE_SELL", symbol: t.symbol, volume: t.volume,
          stopLoss: t.stopLoss, takeProfit: t.takeProfit, clientId: t.clientId, comment: t.clientId });
        if (B.opts.loseAnswer) { B.opts.loseAnswer = false; return new Response("gateway timeout", { status: 504 }); }
        return new Response(JSON.stringify({ numericCode: 10009, stringCode: "TRADE_RETCODE_DONE", orderId: id, positionId: id }));
      }
      if (t.actionType === "POSITION_CLOSE_ID") {
        const i = B.positions.findIndex(x => x.id === t.positionId);
        if (i < 0) return new Response(JSON.stringify({ numericCode: 10013, stringCode: "TRADE_RETCODE_INVALID", message: "no position" }));
        B.positions.splice(i, 1);
        return new Response(JSON.stringify({ numericCode: 10009, stringCode: "TRADE_RETCODE_DONE", positionId: t.positionId }));
      }
      return new Response(JSON.stringify({ stringCode: "TRADE_RETCODE_INVALID" }));
    }
    return new Response("not found", { status: 404 });
  };
  return B;
}
function envFor(B, extra = {}) {
  const e = { __B: B, SECRET: "s3cretKEY123", METAAPI_TOKEN: "tok", ACCOUNT_ID: "acc1", REGION: "london", TELEGRAM_BOT_TOKEN: "bt", TELEGRAM_CHAT_ID: "1", __FAST: true, ...extra };
  if (extra.kv !== false) e.SEEN = { get: async k => B.kv.get(k) || null, put: async (k, v) => { B.kv.set(k, v); } };
  delete e.kv;
  return e;
}
async function send(env, body, { path = "/s3cretKEY123", ip = TV, method = "POST" } = {}) {
  const waits = [];
  const ctx = { waitUntil: p => waits.push(p) };
  const req = new Request("https://smc.example.workers.dev" + path, { method, body: method === "POST" ? body : undefined, headers: { "CF-Connecting-IP": ip } });
  globalThis.fetch = env.__B.fetch;          // each test talks to its own fake broker
  const res = await worker.fetch(req, env, ctx);
  await Promise.all(waits);
  return { status: res.status, text: await res.text() };
}
// the exact text the strategy sends (f_stMsg, TheConnector, sl_price / tp_price) - optional accessKey when group 22 ID is filled
const openMsg = (act, sym, vol, sl, tp, tag, key) => '{"action":"' + act + '","symbol":"' + sym + '","volume":' + vol + ',"sl_price":' + sl + ',"tp_price":' + tp + (tag ? ',"tag":"' + tag + '"' : "") + (key ? ',"accessKey":"' + key + '"' : "") + "}";
const closeMsg = (act, sym, tag) => '{"action":"' + act + '","symbol":"' + sym + '"' + (tag ? ',"tag":"' + tag + '"' : "") + "}";
const trades = B => B.calls.filter(c => c.method === "POST");

console.log("parsing (through the receiver itself)");
{ const B = fakeBroker(); const env = envFor(B);
  let r = await send(env, openMsg("buy", "XAUUSD", 0.05, 4290.123, 4330.456, "smcgold-k3f9"));
  check("the strategy's buy message is accepted", r.status === 200 && B.positions.length === 1 && B.positions[0].clientId === "smcgold_k3f9");
  r = await send(env, closeMsg("closelong", "XAUUSD", "smcgold-k3f9"));
  check("the strategy's close message is accepted", r.status === 200 && B.positions.length === 0);
  for (const [name, body] of [["not JSON", "buy XAUUSD"], ["no stop", '{"action":"buy","symbol":"XAUUSD","volume":0.05,"tp_price":4330}'],
    ["sl instead of sl_price", '{"action":"buy","symbol":"XAUUSD","volume":0.05,"sl":10,"tp":30}'], ["stop above target on a buy", openMsg("buy", "XAUUSD", 0.05, 4330, 4290, "t")],
    ["stop below target on a sell", openMsg("sell", "XAUUSD", 0.05, 4290, 4330, "t")], ["volume 0", openMsg("sell", "XAUUSD", 0, 4330, 4290, "t")],
    ["no symbol", '{"action":"buy","volume":0.05,"sl_price":1,"tp_price":2}'], ["unknown action", '{"action":"closeall","symbol":"XAUUSD"}']]) {
    const n0 = B.calls.length;
    r = await send(env, body);
    check("rejected (400, nothing sent, Telegram): " + name, r.status === 400 && B.calls.length === n0);
  }
  check("every rejection reached Telegram", B.telegram.length === 8);
}

console.log("security");
{ const B = fakeBroker(); const env = envFor(B);
  let r = await send(env, openMsg("buy", "XAUUSD", 0.05, 4290, 4330, "smcgold-k3f9"), { path: "/wrong" });
  check("wrong secret -> 404, nothing sent", r.status === 404 && B.calls.length === 0);
  r = await send(env, openMsg("buy", "XAUUSD", 0.05, 4290, 4330, "smcgold-k3f9"), { ip: "1.2.3.4" });
  check("not a TradingView address -> 403, nothing traded", r.status === 403 && trades(B).length === 0 && B.telegram.length === 1);
  r = await send(envFor(B, { TV_IPS_ONLY: "0" }), openMsg("buy", "XAUUSD", 0.05, 4290, 4330, "smcgold-k3f9"), { ip: "1.2.3.4" });
  check("address check can be switched off", r.status === 200 && B.positions.length === 1);
  r = await send(env, "", { method: "GET", path: "/s3cretKEY123/health" });
  check("health check shows the account", r.status === 200 && JSON.parse(r.text).broker === "FxPro" && JSON.parse(r.text).openPositions === 1);
  r = await send(envFor(B, { METAAPI_TOKEN: "bad" }), "", { method: "GET", path: "/s3cretKEY123/health" });
  check("health check reports a wrong token", r.status === 502 && r.text.includes("401"));
  const B2 = fakeBroker(); const logs = []; const orig = console.log; console.log = s => logs.push(String(s));
  await send(envFor(B2), '{"action":"buy","symbol":"XAUUSD","volume":0.05,"sl":1,"tp":2,"accessKey":"TOPSECRET"}');
  await send(envFor(B2), openMsg("buy", "XAUUSD", 0.05, 4290, 4330, "smcgold-k3f9", "TOPSECRET"));
  console.log = orig;
  check("access key never written to the log or Telegram", !logs.join("").includes("TOPSECRET") && !B2.telegram.join("").includes("TOPSECRET"));
  check("message with an access key still trades", B2.positions.length === 1);
  check("the MetaApi token goes only in the auth-token header", B2.calls.every(c => c.headers["auth-token"] === "tok" && !c.path.includes("tok")));
  check("MetaApi address built from the region", B2.calls.every(c => c.host === "mt-client-api-v1.london.agiliumtrade.ai"));
}

console.log("opening");
{ const B = fakeBroker(); const env = envFor(B);
  const r = await send(env, openMsg("buy", "XAUUSD", 0.05, 4290.123, 4330.456, "smcgold-k3f9"));
  const t = trades(B)[0];
  check("answers TradingView with 200", r.status === 200);
  check("market buy with exact stop, target, lots and clientId", t && t.body.actionType === "ORDER_TYPE_BUY" && t.body.symbol === "XAUUSD" && t.body.volume === 0.05 && t.body.stopLoss === 4290.123 && t.body.takeProfit === 4330.456 && t.body.clientId === "smcgold_k3f9", t && t.body);
  await send(env, openMsg("buy", "XAUUSD", 0.05, 4290.123, 4330.456, "smcgold-k3f9"));
  check("the same alert twice -> one trade", B.positions.length === 1 && trades(B).length === 1);
  const Bn = fakeBroker(); const envN = envFor(Bn, { kv: false });
  await send(envN, openMsg("sell", "XAUUSD", 0.05, 4330, 4290, "smcgold-z9y8"));
  await send(envN, openMsg("sell", "XAUUSD", 0.05, 4330, 4290, "smcgold-z9y8"));
  check("twice without the KV store -> still one trade (the open position is seen)", Bn.positions.length === 1);
  await send(env, openMsg("sell", "XAUUSD", 3, 4330, 4290, "smcgold-big1"));
  check("above MAX_LOTS (1) -> refused, Telegram", B.positions.length === 1 && B.telegram.some(s => s.includes("MAX_LOTS")));
  await send(envFor(B, { MAX_LOTS: "5" }), openMsg("sell", "XAUUSD", 3, 4330, 4290, "smcgold-big2"));
  check("MAX_LOTS can be raised", B.positions.length === 2);
  const Bd = fakeBroker(); await send(envFor(Bd, { DRY_RUN: "1" }), openMsg("buy", "EURUSD", 0.5, 1.0801, 1.0850, "smcgold-dry1"));
  check("DRY_RUN sends no order", trades(Bd).length === 0);
  const Bs = fakeBroker(); await send(envFor(Bs, { SYMBOL_MAP: '{"XAUUSD":"GOLD"}' }), openMsg("buy", "XAUUSD", 0.05, 4290, 4330, "smcgold-map1"));
  check("SYMBOL_MAP renames the symbol", Bs.positions[0] && Bs.positions[0].symbol === "GOLD");
  const Br = fakeBroker({ reject: true }); await send(envFor(Br), openMsg("buy", "XAUUSD", 0.05, 4290, 4330, "smcgold-rej1"));
  check("broker refuses -> Telegram says so", Br.telegram.some(s => s.includes("open failed") && s.includes("NO_MONEY")));
  const Bl = fakeBroker({ loseAnswer: true }); await send(envFor(Bl), openMsg("buy", "XAUUSD", 0.05, 4290, 4330, "smcgold-lost"));
  check("answer lost but the order went through -> counted as opened, not sent again", Bl.positions.length === 1 && trades(Bl).length === 1 && !Bl.telegram.some(s => s.includes("failed")));
}

console.log("closing - stacked trades");
{ const B = fakeBroker(); const env = envFor(B);
  for (const [tag, vol] of [["smcgold-aaa1", 0.03], ["smcgold-aaa2", 0.04], ["smcgold-aaa3", 0.05]]) await send(env, openMsg("buy", "XAUUSD", vol, 4290, 4330, tag));
  await send(env, openMsg("sell", "EURUSD", 0.5, 1.09, 1.08, "smcgold-eur1"));
  check("4 positions open", B.positions.length === 4);
  await send(env, closeMsg("closelong", "XAUUSD", "smcgold-aaa2"));
  check("close by tag closes ONLY that trade", B.positions.length === 3 && !B.positions.some(p => p.clientId === "smcgold_aaa2"));
  await send(env, closeMsg("closeshort", "XAUUSD", "smcgold-aaa1"));
  check("closeshort never closes a long with the same tag", B.positions.length === 3);
  const before = trades(B).length;
  await send(env, closeMsg("closelong", "XAUUSD", "smcgold-gone"));
  check("close for a trade FxPro already closed -> nothing sent, no Telegram", trades(B).length === before && B.telegram.length === 0);
  await send(env, closeMsg("closelong", "XAUUSD", ""));
  check("close without a tag closes every long on that symbol only", B.positions.length === 1 && B.positions[0].symbol === "EURUSD");
}

console.log("close arriving before its own open (entry and exit on the same candle)");
{ const B = fakeBroker({ delayOpen: 150 }); const env = envFor(B);
  const a = send(env, openMsg("buy", "XAUUSD", 0.05, 4290, 4330, "smcgold-race"));
  const b = send(env, closeMsg("closelong", "XAUUSD", "smcgold-race"));
  await Promise.all([a, b]);
  check("the close waits for the open and closes it - no trade left behind", B.positions.length === 0 && trades(B).length === 2);
}

console.log("\n" + passes + " passed, " + fails + " failed");
process.exit(fails ? 1 : 0);
