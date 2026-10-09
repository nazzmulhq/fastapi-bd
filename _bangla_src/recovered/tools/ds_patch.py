import ast,glob,os,json,re,inspect,shutil,sys
SP=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO=os.path.join(SP,'repo'); OUT=os.path.join(SP,'patched_src')
src=json.load(open(os.path.join(SP,'ds/source.json'),encoding='utf8'))
bn={}
for f in sorted(glob.glob(os.path.join(SP,'ds/bn_*.txt'))):
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
for f in sorted(glob.glob(os.path.join(OUT,'fastapi/**/*.py'),recursive=True)):
    text=open(f,encoding='utf8').read()
    tree=ast.parse(text)
    nodes=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and getattr(node.func,'id',None)=='Doc' and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
            nodes.append(node.args[0])
        if isinstance(node,(ast.FunctionDef,ast.ClassDef,ast.AsyncFunctionDef,ast.Module)) and node.body:
            e=node.body[0]
            if isinstance(e,ast.Expr) and isinstance(e.value,ast.Constant) and isinstance(e.value.value,str):
                nodes.append(e.value)
    lines=text.encode('utf8').split(b'\n')
    reps=[]
    for n in nodes:
        k=inspect.cleandoc(n.value)
        if k in mp:
            reps.append((n.lineno-1,n.col_offset,n.end_lineno-1,n.end_col_offset,literal(n.value,mp[k]),k))
    reps.sort(key=lambda r:(r[0],r[1]),reverse=True)
    for l1,c1,l2,c2,lit,k in reps:
        pre=lines[l1][:c1]; post=lines[l2][c2:]
        new=(pre+lit.encode('utf8')+post).split(b'\n')
        lines[l1:l2+1]=new
        count+=1; used.add(k)
    out=b'\n'.join(lines).decode('utf8')
    t2=ast.parse(out)  # syntax check
    open(f,'w',encoding='utf8').write(out)
# verify
bad=0
for f in sorted(glob.glob(os.path.join(OUT,'fastapi/**/*.py'),recursive=True)):
    tree=ast.parse(open(f,encoding='utf8').read())
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and getattr(node.func,'id',None)=='Doc' and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
            k=inspect.cleandoc(node.args[0].value)
            if k in mp: bad+=1; print('still english',f,k[:60])
print('replaced',count,'unique used',len(used),'of',len(mp),'still-english',bad)
