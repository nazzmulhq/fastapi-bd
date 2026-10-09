import os,sys,re
sys.path.insert(0,os.path.dirname(__file__))
from common import *
from ref_lines import T
sys.path.insert(0,os.path.join(SP,'repo/scripts'))
def slug(t):
    t=re.sub(r'`','',t).strip().lower()
    t=re.sub(r'[^\w\- ]','',t)
    return re.sub(r'[\s]+','-',t).strip('-')
missing=set()
for root,_,fs in os.walk(os.path.join(EN,'reference')):
    for f in fs:
        if not f.endswith('.md'): continue
        p=os.path.join(root,f); rel=os.path.relpath(p,EN)
        lines=open(p,encoding='utf8').read().split('\n'); out=[]; infence=False
        for l in lines:
            if l.startswith('```'): infence=not infence; out.append(l); continue
            if infence or l.startswith(':::') or l.startswith('    ') or not l.strip():
                out.append(l); continue
            if l in T:
                nl=T[l]
                m=re.match(r'^(#{2,6}) (.*)$',l)
                if m: nl=nl+' { #'+slug(m.group(2))+' }'
                out.append(nl)
            else:
                out.append(l)
                if re.search(r'[A-Za-z]{3}',l) and not l.startswith(('* `','* 200','* 403','@','app','def','///')): missing.add(l)
        dst=os.path.join(BN,rel); os.makedirs(os.path.dirname(dst),exist_ok=True)
        open(dst,'w',encoding='utf8').write('\n'.join(out))
print('untranslated prose lines:',len(missing))
for m in sorted(missing): print('  ',m)
