import sys, time
from pynescript.ast import parse
t = time.time()
src = open(sys.argv[1]).read()
try:
    parse(src); print("PARSED OK", sys.argv[1], round(time.time() - t), "s")
except Exception as e:
    print("PARSE ERROR", sys.argv[1], repr(e)[:3000])
