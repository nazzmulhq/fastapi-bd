import os,sys
sys.path.insert(0,os.path.dirname(__file__))
from common import *
order=[l.strip() for f in ('eorder.txt','eorder_ext.txt') if os.path.exists(os.path.join(SRC,'tools',f)) for l in open(os.path.join(SRC,'tools',f)) if l.strip()]
EWORK=os.path.join(SRC,'ework')
done=[f for f in order if os.path.exists(os.path.join(EWORK,f))]
left=[f for f in order if f not in done]
print(f'easy done {len(done)}/{len(order)}')
for f in left[:int(sys.argv[1]) if len(sys.argv)>1 else 6]: print(os.path.getsize(en_path(f)),f)
