import sys,os,json
sys.path.insert(0,os.path.dirname(__file__))
from common import *
rel=sys.argv[1]
t=open(os.path.join(EN,rel),encoding='utf8').read()
lines=t.split('\n');mapping={};n=0;out=[];last=0
for s,e,bl in blocks(t):
    out+=lines[last:s]
    if has_comment(bl): out+=bl
    else:
        n+=1;key=f'⟦CODE{n}⟧';mapping[key]='\n'.join(bl[0:]).replace(bl[0][:len(bl[0])-len(bl[0].lstrip())],'',0)
        ind=bl[0][:len(bl[0])-len(bl[0].lstrip())]
        mapping[key]=json.dumps(bl)
        out.append(ind+key)
    last=e+1
out+=lines[last:]
os.makedirs(os.path.dirname(os.path.join(WORK,rel)),exist_ok=True)
json.dump(mapping,open(os.path.join(WORK,rel+'.json'),'w'))
print('\n'.join(out))
