import sys
s = open(sys.argv[1]).read()
a = s.index('//==CORE-BEGIN=='); b = s.index('//==CORE-END==')
open(sys.argv[2], 'w').write(s[a:b])
