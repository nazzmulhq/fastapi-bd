import ast,glob,os,json,re,inspect,sys
SP=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(SP,'repo'))
uniq={}
def add(s,where):
    k=inspect.cleandoc(s)
    if not k.strip(): return
    uniq.setdefault(k,[]).append(where)
for f in sorted(glob.glob('fastapi/**/*.py',recursive=True)):
    t=ast.parse(open(f).read())
    for node in ast.walk(t):
        if isinstance(node,ast.Call) and getattr(node.func,'id',None)=='Doc' and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
            add(node.args[0].value,f)
        if isinstance(node,(ast.FunctionDef,ast.ClassDef,ast.AsyncFunctionDef,ast.Module)):
            d=ast.get_docstring(node,clean=False)
            if d: add(d,f)
# also deprecated(...) messages? skip
items=sorted(uniq.items(),key=lambda kv:(kv[1][0],kv[0]))
os.makedirs(os.path.join(SP,'ds'),exist_ok=True)
out=[];codes={}
for i,(k,w) in enumerate(items,1):
    blocks=[];
    def rep(m):
        blocks.append(m.group(0)); return f'⟦C{len(blocks)}⟧'
    kk=re.sub(r'```.*?```',rep,k,flags=re.S)
    codes[i]=blocks
    out.append((i,k,kk,w[0]))
json.dump({i:{'en':k,'codes':codes[i]} for i,k,kk,w in out},open(os.path.join(SP,'ds/source.json'),'w'),ensure_ascii=False)
with open(os.path.join(SP,'ds/source.txt'),'w') as fh:
    for i,k,kk,w in out: fh.write(f'=== {i} [{w}]\n{kk}\n')
print(len(out), sum(len(kk) for _,_,kk,_ in out))
