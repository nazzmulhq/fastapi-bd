import os,re,sys,glob,urllib.parse,collections
root=sys.argv[1]
bad=collections.Counter(); ex={}
for f in glob.glob(os.path.join(root,'**/*.html'),recursive=True):
    if '_backup_old_site' in f or '_bangla_src' in f: continue
    t=open(f,encoding='utf8',errors='ignore').read()
    for m in re.finditer(r'(?:href|src)="([^"#?]*)[^"]*"',t):
        u=m.group(1)
        if not u or re.match(r'^[a-z]+:',u) or u.startswith('//'): continue
        if u.startswith('/'): p=os.path.join(root,urllib.parse.unquote(u.lstrip('/')))
        else: p=os.path.normpath(os.path.join(os.path.dirname(f),urllib.parse.unquote(u)))
        if os.path.isdir(p): p=os.path.join(p,'index.html')
        if not os.path.exists(p): bad[u]+=1; ex.setdefault(u,os.path.relpath(f,root))
print('broken',len(bad))
for u,c in bad.most_common(30): print(c,u,'  in',ex[u])
