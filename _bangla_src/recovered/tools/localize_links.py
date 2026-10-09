import os,re,sys,glob
root=sys.argv[1]; n=0; files=0
A=re.compile(r'<a([^>]*?)href="https://fastapi\.tiangolo\.com/([^"#]*)(#[^"]*)?"([^>]*)>(.*?)</a>',re.S)
for f in glob.glob(os.path.join(root,'**/*.html'),recursive=True):
    if '_backup_old_site' in f: continue
    t=open(f,encoding='utf8').read()
    s,e=t.find('<article'),t.find('</article>')
    if s<0: continue
    art=t[s:e]
    def rep(m):
        global n
        pre,path,frag,post,text=m.groups()
        if 'ইংরেজি সংস্করণ' in text: return m.group(0)
        if not path or re.match(r'^(de|es|fr|hi|ja|ko|pt|ru|tr|uk|zh|zh-hant)/',path): return m.group(0)
        if not os.path.exists(os.path.join(root,path.rstrip('/'),'index.html')): return m.group(0)
        n+=1
        return f'<a{pre}href="/{path}{frag or ""}"{post}>{text}</a>'
    new=A.sub(rep,art)
    if new!=art:
        open(f,'w',encoding='utf8').write(t[:s]+new+t[e:]); files+=1
print('rewrote',n,'links in',files,'files')
