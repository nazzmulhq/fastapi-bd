import ast,glob,os,json,re,inspect,shutil,sys
sys.path.insert(0,os.path.dirname(__file__)); from paths import *
OUT=os.path.join(SP,'patched_src')
src=json.load(open(os.path.join(SRC,'ds/source.json'),encoding='utf8'))
s2=os.path.join(SRC,'ds/source2.json')
use2=os.path.exists(s2) and '--fastapi-only' not in sys.argv
if use2: src.update(json.load(open(s2,encoding='utf8')))
bn={}
files=sorted(glob.glob(os.path.join(SRC,'ds/bn_*.txt')))+(sorted(glob.glob(os.path.join(SRC,'ds/bn2_*.txt'))) if use2 else [])
for f in files:
    t=open(f,encoding='utf8').read()
    for m in re.finditer(r'^=== (\d+)\n(.*?)(?=^=== \d+\n|\Z)',t,re.S|re.M):
        bn[m.group(1)]=m.group(2).strip('\n')
mp={}; errs=[]
for k,v in src.items():
    b=bn.get(k)
    if b is None: errs.append((k,'missing')); continue
    ph=re.findall(r'⟦C(\d+)⟧',b)
    if sorted(map(int,ph))!=list(range(1,len(v['codes'])+1)): errs.append((k,'placeholders',ph,len(v['codes']))); continue
    b=re.sub(r'⟦C(\d+)⟧',lambda m:v['codes'][int(m.group(1))-1],b)
    mp[v['en']]=b
if errs: print('ERRORS',errs); sys.exit(1)
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
shutil.copytree(os.path.join(REPO,'fastapi'),os.path.join(OUT,'fastapi'))
if use2:
    for pkg in ['starlette','httpx']:
        shutil.copytree(os.path.join(SITE_PKGS,pkg),os.path.join(OUT,pkg),ignore=shutil.ignore_patterns('__pycache__'))
def margin(val):
    lines=val.expandtabs().split('\n')[1:]
    ind=[len(l)-len(l.lstrip()) for l in lines if l.strip()]
    return ' '*(min(ind) if ind else 0)
def literal(orig,new):
    m=margin(orig)
    tail=orig[orig.rfind('\n')+1:] if '\n' in orig and not orig[orig.rfind('\n')+1:].strip() else ''
    body='\n'.join((m+l if l.strip() else '') for l in new.split('\n'))
    val='\n'+body+'\n'+tail
    esc=val.replace('\\','\\\\').replace('"""','\\"\\"\\"')
    return '"""'+esc+'"""'
count=0; used=set()
for f in sorted(glob.glob(os.path.join(OUT,'**/*.py'),recursive=True)):
    text=open(f,encoding='utf8').read()
    tree=ast.parse(text)
    nodes=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and getattr(node.func,'id',None) in ('Doc','deprecated') and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
            nodes.append(node.args[0])
        if isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
            nodes.append(node.value)
    lines=text.encode('utf8').split(b'\n')
    reps=[]
    for n in nodes:
        k=inspect.cleandoc(n.value)
        if k in mp:
            reps.append((n.lineno-1,n.col_offset,n.end_lineno-1,n.end_col_offset,literal(n.value,mp[k]),k))
    reps.sort(key=lambda r:(r[0],r[1]),reverse=True)
    for l1,c1,l2,c2,lit,k in reps:
        pre=lines[l1][:c1]; post=lines[l2][c2:]
        lines[l1:l2+1]=(pre+lit.encode('utf8')+post).split(b'\n')
        count+=1; used.add(k)
    out=b'\n'.join(lines).decode('utf8')
    ast.parse(out)
    open(f,'w',encoding='utf8').write(out)
print('replaced',count,'unique used',len(used),'of',len(mp))
