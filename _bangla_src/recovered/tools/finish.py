import sys,os,json,re
sys.path.insert(0,os.path.dirname(__file__))
from common import *
def restore(rel):
    w=open(os.path.join(WORK,rel),encoding='utf8').read()
    mp=json.load(open(os.path.join(WORK,rel+'.json')))
    lines=w.split('\n');out=[]
    for l in lines:
        m=re.match(r'^(\s*)(⟦CODE\d+⟧)\s*$',l)
        if m and m.group(2) in mp:
            bl=json.loads(mp[m.group(2)]);out+=bl
        else: out.append(l)
    txt='\n'.join(out)
    if not txt.endswith('\n'): txt+='\n'
    return txt
def check(rel,bn):
    en=open(os.path.join(EN,rel),encoding='utf8').read();probs=[]
    if '⟦CODE' in bn: probs.append('unrestored placeholder')
    H=lambda t:[m for m in re.findall(r'^#{1,6} .*?\{ ?#([^ }]+) ?\}',t,re.M)]
    if H(en)!=H(bn): probs.append(f'heading anchors differ: en={H(en)} bn={H(bn)}')
    nh=lambda t:len(re.findall(r'^#{1,6} ',re.sub(r'```.*?```','',t,flags=re.S),re.M))
    if nh(en)!=nh(bn): probs.append(f'heading count en={nh(en)} bn={nh(bn)}')
    be,bb=blocks(en),blocks(bn)
    if len(be)!=len(bb): probs.append(f'code block count en={len(be)} bn={len(bb)}')
    else:
        for i,((_,_,a),(_,_,b)) in enumerate(zip(be,bb)):
            if a==b: continue
            sa=[strip_comments(x) for x in a];sb=[strip_comments(x) for x in b]
            if sa!=sb or len(a)!=len(b): probs.append(f'code block {i+1} changed: {a[0]!r}')
    inc=lambda t:re.findall(r'\{\*.*?\*\}',t)
    if inc(en)!=inc(bn): probs.append('include lines differ')
    U=lambda t:re.findall(r'\]\(([^)\s]+)\)',t)+re.findall(r'href="([^"]+)"',t)
    if sorted(U(en))!=sorted(U(bn)): 
        a,b=U(en),U(bn);probs.append(f'links differ: missing={[x for x in a if x not in b]} extra={[x for x in b if x not in a]}')
    for pat in (r'^\s*/{3}(?!/)',r'^\s*/{4}'):
        ce=len(re.findall(pat,en,re.M));cb=len(re.findall(pat,bn,re.M))
        if ce!=cb: probs.append(f'block markers {pat}: en={ce} bn={cb}')
    for tag in ('abbr','dfn','code','strong','em','a','div','details','img'):
        ce=len(re.findall(f'<{tag}[ >]',en));cb=len(re.findall(f'<{tag}[ >]',bn))
        if ce!=cb: probs.append(f'<{tag}> count en={ce} bn={cb}')
    # leftover english prose estimate
    prose=re.sub(r'```.*?```','',bn,flags=re.S);prose=re.sub(r'`[^`]*`|<[^>]+>|\]\([^)]*\)|\{[^}]*\}','',prose)
    lat=len(re.findall(r'[A-Za-z]',prose));ben=len(re.findall(r'[ঀ-৿]',prose))
    return probs,ben/(lat+ben+1)
for rel in sys.argv[1:]:
    bn=restore(rel)
    os.makedirs(os.path.dirname(os.path.join(BN,rel)),exist_ok=True)
    open(os.path.join(BN,rel),'w',encoding='utf8').write(bn)
    probs,r=check(rel,bn)
    print(('OK ' if not probs else 'ISSUES ')+rel+f'  bangla-ratio={r:.2f}')
    for p in probs: print('   -',p)
