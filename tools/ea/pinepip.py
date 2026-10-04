# the Pine v11.2 pip rule (stCls + stPipAuto), line for line, for TradingView-style symbols
CRY = ",BTC,ETH,LTC,XRP,SOL,BCH,ADA,DOGE,DOT,BNB,AVAX,LINK,XLM,TRX,UNI,MATIC,POL,SHIB,TON,XMR,ETC,ATOM,NEAR,APT,SUI,"
def pine_pip(tk, typ, bc, cur, mintick):
    isPt = "XPT" in tk or "XPD" in tk
    cls = 4 if typ == "crypto" else 2 if ("XAU" in tk or bc == "XAU" or "GOLD" in tk) else 3 if ("XAG" in tk or bc == "XAG" or "SILVER" in tk) else 5 if isPt else \
          4 if (bc != "" and ("," + bc + ",") in CRY) else 1 if typ == "forex" else 5
    isBtc = bc == "BTC" or (bc == "" and tk.startswith("BTC")); isEth = bc == "ETH" or (bc == "" and tk.startswith("ETH"))
    return 0.1 if cls == 2 else 0.01 if cls == 3 else 1.0 if (cls == 4 and isBtc) else 0.1 if (cls == 4 and isEth) else (0.01 if cur == "JPY" else 0.0001) if cls == 1 else 10 * mintick
cases = [("XAUUSD", "commodity", "XAU", "USD", 0.001, 0.1), ("GOLD", "cfd", "", "USD", 0.01, 0.1), ("XAGUSD", "commodity", "XAG", "USD", 0.0001, 0.01),
         ("BTCUSD", "crypto", "BTC", "USD", 0.01, 1.0), ("BTCUSDT", "crypto", "BTC", "USDT", 0.01, 1.0), ("ETHUSD", "crypto", "ETH", "USD", 0.01, 0.1),
         ("ETHBTC", "crypto", "ETH", "BTC", 0.000001, 0.1), ("SOLUSD", "crypto", "SOL", "USD", 0.001, 0.01),
         ("EURUSD", "forex", "EUR", "USD", 0.00001, 0.0001), ("GBPUSD", "forex", "GBP", "USD", 0.00001, 0.0001), ("USDJPY", "forex", "USD", "JPY", 0.001, 0.01),
         ("EURJPY", "forex", "EUR", "JPY", 0.001, 0.01), ("XPTUSD", "cfd", "XPT", "USD", 0.01, 0.1), ("US30USD", "cfd", "", "USD", 0.1, 1.0)]
bad = 0
for tk, typ, bc, cur, mt, ex in cases:
    p = pine_pip(tk, typ, bc, cur, mt); ok = abs(p - ex) < 1e-12; bad += not ok
    print("%-8s pip %-8g %s" % (tk, p, "ok" if ok else "WRONG"))
print("ALL OK" if not bad else "SOME WRONG")
