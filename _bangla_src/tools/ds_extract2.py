import ast,glob,os,json,re,inspect,html,sys
sys.path.insert(0,os.path.dirname(__file__)); from paths import *
SITE=SITE_PKGS
txt=''
for f in glob.glob(os.path.join(SP,'site_bn/reference/**/index.html'),recursive=True):
    t=open(f,encoding='utf8').read(); t=t[t.find('<article'):t.find('</article>')]
    txt+=' '+re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',t)))
norm=lambda s:re.sub(r'\s+',' ',re.sub(r'`','',s)).strip()
found={}
for pkg in ['starlette','httpx']:
    for f in sorted(glob.glob(os.path.join(SITE,pkg,'**/*.py'),recursive=True)):
        tree=ast.parse(open(f,encoding='utf8').read())
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.ClassDef,ast.AsyncFunctionDef,ast.Module)):
                d=ast.get_docstring(node,clean=False)
                if not d: continue
                k=inspect.cleandoc(d)
                first=norm(re.sub(r'\[([^\]]*)\]\([^)]*\)',r'\1',k.split('\n\n')[0]))[:45]
                if len(first)>12 and first in txt:
                    found.setdefault(k,os.path.relpath(f,SITE))
for node in ast.walk(ast.parse(open(os.path.join(SITE,'starlette/status.py'),encoding='utf8').read())):
    if isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
        found.setdefault(inspect.cleandoc(node.value.value),'starlette/status.py')
for node in ast.walk(ast.parse(open(os.path.join(REPO,'fastapi/param_functions.py'),encoding='utf8').read())):
    if isinstance(node,ast.Call) and getattr(node.func,'id',None)=='deprecated' and node.args and isinstance(node.args[0],ast.Constant):
        found.setdefault(inspect.cleandoc(node.args[0].value),'fastapi/param_functions.py')
out={}
with open(os.path.join(SRC,'ds/source2.txt'),'w',encoding='utf8') as fh:
    for i,(k,w) in enumerate(found.items(),1001):
        blocks=[]
        def rep(m): blocks.append(m.group(0)); return f'⟦C{len(blocks)}⟧'
        kk=re.sub(r'```.*?```',rep,k,flags=re.S)
        out[i]={'en':k,'codes':blocks}
        fh.write(f'=== {i} [{w}]\n{kk}\n')
json.dump(out,open(os.path.join(SRC,'ds/source2.json'),'w',encoding='utf8'),ensure_ascii=False)
print(len(out))
