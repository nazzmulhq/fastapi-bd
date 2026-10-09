# store EN mkdocstrings ::: blocks as ⟦CODEn⟧ placeholders for ework/<rel>
import sys,os,json,re
sys.path.insert(0,os.path.dirname(__file__))
from common import *
rel=sys.argv[1]
en=open(os.path.join(EN,rel),encoding='utf8').read()
blocks=re.findall(r'^::: .*\n(?:    .*\n|\n(?=    ))*',en+'\n',re.M)
mp={}
for i,b in enumerate(blocks,1):
    lines=b.rstrip('\n').split('\n')
    mp[f'⟦CODE{i}⟧']=json.dumps(lines)
    print(f'⟦CODE{i}⟧ =',lines[0],f'({len(lines)} lines)')
os.makedirs(os.path.dirname(os.path.join(SRC,'ework',rel)),exist_ok=True)
json.dump(mp,open(os.path.join(SRC,'ework',rel+'.json'),'w'))
