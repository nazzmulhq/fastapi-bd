import sys,os,json,re
sys.path.insert(0,os.path.dirname(__file__))
from common import *
EWORK=os.path.join(SRC,'ework')
def restore(rel):
    w=open(os.path.join(EWORK,rel),encoding='utf8').read()
    mp=json.load(open(os.path.join(EWORK,rel+'.json')))
    out=[]
    for l in w.split('\n'):
        m=re.match(r'^(\s*)(⟦CODE\d+⟧)\s*$',l)
        if m and m.group(2) in mp:
            bl=json.loads(mp[m.group(2)])
            ind=m.group(1); oind=bl[0][:len(bl[0])-len(bl[0].lstrip())]
            out+=[ind+x[len(oind):] if x.startswith(oind) else x for x in bl]
        else: out.append(l)
    txt='\n'.join(out)
    return txt if txt.endswith('\n') else txt+'\n'
def check(rel,bn):
    en=open(os.path.join(EN,rel),encoding='utf8').read();probs=[]
    if '⟦CODE' in bn: probs.append('unrestored placeholder')
    H=lambda t:re.findall(r'^#{1,6} .*?\{ ?#([^ }]+) ?\}',t,re.M)
    hb=H(bn); it=iter(hb)
    if not all(a in it for a in H(en)): probs.append(f'heading anchors missing/out of order: {[a for a in H(en) if a not in hb]}')
    extra=[a for a in hb if a not in H(en) and not a.startswith('bn-')] if H(en) else []
    if extra: probs.append(f'new anchors must start with bn-: {extra}')
    noanc=[l for l in re.findall(r'^#{1,6} .*$',re.sub(r'```.*?```','',bn,flags=re.S),re.M) if '{ #' not in l and '{#' not in l]
    if noanc: probs.append(f'headings without anchor: {noanc}')
    sb=[[strip_comments(x) for x in b] for _,_,b in blocks(bn)]
    for i,(_,_,a) in enumerate(blocks(en)):
        if [strip_comments(x) for x in a] not in sb: probs.append(f'code block {i+1} missing/changed: {a[0]!r} {a[1][:40]!r}')
    MK=lambda t:re.findall(r'^::: .*\n(?:(?:    .*)?\n)*?(?=\S|\Z)',t+'\n',re.M)
    mb=MK(bn); itm=iter(mb)
    if not all(x in itm for x in MK(en)): probs.append(f'mkdocstrings blocks missing/changed: {[x.split(chr(10))[0] for x in MK(en) if x not in mb]}')
    inc=lambda t:re.findall(r'\{\*.*?\*\}',t)
    ib=inc(bn)
    for x in inc(en):
        if x not in ib: probs.append(f'include missing: {x}')
    U=lambda t:re.findall(r'\]\(([^)\s]+)\)',t)+re.findall(r'(?:href|src)="([^"]+)"',t)
    ub=U(bn)
    miss=[x for x in U(en) if x not in ub]
    if miss: probs.append(f'links missing: {miss}')
    # block balance: openers '/// type' vs closers '///'
    for n in (3,4):
        op=len(re.findall(r'^[ \t]*'+'/'*n+r'(?!/)[ \t]*\S',bn,re.M)); cl=len(re.findall(r'^[ \t]*'+'/'*n+r'(?!/)[ \t]*$',bn,re.M))
        if op!=cl: probs.append(f'unbalanced {"/"*n}: open={op} close={cl}')
    for tag in ('abbr','dfn','details','div','img'):
        ce=len(re.findall(f'<{tag}[ >]',en));cb=len(re.findall(f'<{tag}[ >]',bn))
        if cb<ce: probs.append(f'<{tag}> fewer: en={ce} bn={cb}')
    prose=re.sub(r'```.*?```','',bn,flags=re.S);prose=re.sub(r'`[^`]*`|<[^>]+>|\]\([^)]*\)|\{[^}]*\}','',prose)
    lat=len(re.findall(r'[A-Za-z]',prose));ben=len(re.findall(r'[ঀ-৿]',prose))
    return probs,ben/(lat+ben+1),len(bn)/max(1,len(en))
for rel in [a for a in sys.argv[1:] if not a.startswith('-')]:
    bn=restore(rel)
    probs,r,g=check(rel,bn)
    if not probs or '--force' in sys.argv:
        os.makedirs(os.path.dirname(os.path.join(BN,rel)),exist_ok=True)
        open(os.path.join(BN,rel),'w',encoding='utf8').write(bn)
    print(('OK ' if not probs else 'ISSUES ')+rel+f'  bangla={r:.2f} size-vs-en={g:.1f}x'+('' if not probs else ' (not written)'))
    for p in probs: print('   -',p)
