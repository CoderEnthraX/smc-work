SMC STRUCTURE STRATEGY - METAAPI RECEIVER v1.0
==============================================
TradingView alert -> this receiver (Cloudflare Worker) -> MetaApi -> your FxPro MT5 account.
No MT5 to keep running, no VPS. The strategy is unchanged (group 22 "Message format" = TheConnector).

Setup, step by step:  SMC_Strategy_v8.3_METAAPI_RECEIVER_GUIDE.pdf  (in the main folder)

FILES
  worker.js     THE RECEIVER. Paste this whole file into your Cloudflare Worker. Nothing to edit inside it -
                every setting is a Variable or Secret in Cloudflare (list at the top of the file and in the guide).
  test.mjs      36 checks against a fake MetaApi:            node test.mjs
  replay.mjs    replays the strategy's own alert stream from the simulator through the receiver
                (the stream file comes from the test simulator and is not part of this folder).
  package.json  lets node run the tests.

NEVER put your MetaApi token, your SECRET, your MT5 password or a Telegram bot token into these files,
into a chat or into a screenshot. They belong only in MetaApi's and Cloudflare's own secret fields.
