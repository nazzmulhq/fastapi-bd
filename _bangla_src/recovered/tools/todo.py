import os,sys
sys.path.insert(0,os.path.dirname(__file__))
from common import *
order=[l.strip() for l in open(os.path.join(SP,'tools/files.txt')) if l.strip()]
done=[f for f in order if os.path.exists(os.path.join(BN,f))]
left=[f for f in order if f not in done]
sz=lambda f:os.path.getsize(os.path.join(EN,f))
print(f'done {len(done)}/{len(order)}  chars left {sum(sz(f) for f in left)}')
for f in left[:int(sys.argv[1]) if len(sys.argv)>1 else 8]: print(sz(f),f)
