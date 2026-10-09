"""Print English page with code placeholders + the source of included code files (for explanations)."""
import sys,os,json,re,subprocess
sys.path.insert(0,os.path.dirname(__file__))
from common import *
rel=sys.argv[1]
EWORK=os.path.join(SRC,'ework')
t=open(os.path.join(EN,rel),encoding='utf8').read()
lines=t.split('\n');mapping={};n=0;out=[];last=0
for s,e,bl in blocks(t):
    out+=lines[last:s]
    if has_comment(bl) or len(bl)<=4: out+=bl
    else:
        n+=1;key=f'⟦CODE{n}⟧'
        ind=bl[0][:len(bl[0])-len(bl[0].lstrip())]
        mapping[key]=json.dumps(bl)
        out.append(ind+key)
    last=e+1
out+=lines[last:]
os.makedirs(os.path.dirname(os.path.join(EWORK,rel)),exist_ok=True)
json.dump(mapping,open(os.path.join(EWORK,rel+'.json'),'w'))
print('\n'.join(out))
if '--code' in sys.argv:
    base=os.path.dirname(os.path.join(EN,rel))
    seen=set()
    for m in re.finditer(r'\{\*\s*(\S+)\s*(.*?)\*\}|\{!>?\s*(\S+?)\s*!\}',t):
        if m.group(3): m=re.match(r'(.*)()',m.group(3))
        p=os.path.join(SP,'repo',re.sub(r'^(\.\./)+','',m.group(1)))
        if p in seen or not os.path.exists(p): continue
        seen.add(p)
        src=open(p,encoding='utf8').read().rstrip('\n').split('\n')
        print(f'\n##### CODE {m.group(1)} {m.group(2)}')
        for i,l in enumerate(src,1): print(f'{i:3} {l if len(l)<200 else l[:120]+" ...[truncated]"}')
