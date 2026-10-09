import re,os,json,sys
SP=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN=os.path.join(SP,'repo/docs/en/docs')
BN=os.path.join(SP,'repo/docs/bn/docs')
WORK=os.path.join(SP,'work')
FENCE=re.compile(r'^(\s*)(`{3,}|~{3,})(.*)$')
def blocks(text):
    """return list of (start,end,lines) for fenced code blocks (line indices inclusive)"""
    lines=text.split('\n');out=[];i=0
    while i<len(lines):
        m=FENCE.match(lines[i])
        if m:
            ind,f,_=m.groups();j=i+1
            while j<len(lines):
                m2=re.match(r'^\s*('+re.escape(f[0])+'{'+str(len(f))+r',})\s*$',lines[j])
                if m2: break
                j+=1
            out.append((i,j,lines[i:j+1]));i=j+1
        else: i+=1
    return out
COMMENT=re.compile(r'(^\s*//\s?\S)|((^|\s)#\s+[A-Za-z(])')
def has_comment(bl):
    lang=bl[0].strip().strip('`~').strip().split(' ')[0].lower()
    if lang in ('md','markdown','json','html','text','txt','mermaid','jinja','css'): return False
    return any(COMMENT.search(l) for l in bl[1:-1])
def strip_comments(l):
    l=re.sub(r'^\s*//.*$','',l)
    l=re.sub(r'(^|\s)#\s.*$','',l)
    return l.rstrip()
