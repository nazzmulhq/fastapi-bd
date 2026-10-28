"""Print English page with code placeholders + the source of included code files (for explanations)."""
import sys,os,json,re,subprocess
sys.path.insert(0,os.path.dirname(__file__))
from common import *
rel=sys.argv[1]
EWORK=os.path.join(SRC,'ework')
t=open(en_path(rel),encoding='utf8').read()
lines=t.split('\n');mapping={};n=0;out=[];last=0
ext=is_ext(rel)
spans=list(blocks(t))
if ext:  # also ::: mkdocstrings blocks (with their options) become placeholders
    i=0
    while i<len(lines):
        if lines[i].startswith(':::') and not any(s<=i<=e for s,e,_ in spans):
            j=i+1
            while j<len(lines) and (lines[j].startswith('    ') or (not lines[j].strip() and j+1<len(lines) and lines[j+1].startswith('    '))): j+=1
            spans.append((i,j-1,lines[i:j])); i=j
        else: i+=1
    # raw-HTML paragraphs and badge rows: keep verbatim via placeholders
    i=0
    while i<len(lines):
        if (i==0 or not lines[i-1].strip()) and lines[i].strip() and not any(s<=i<=e for s,e,_ in spans):
            j=i
            while j<len(lines) and lines[j].strip(): j+=1
            para=lines[i:j]
            if len(para)>=25 and all(x.lstrip().startswith('|') for x in para):
                spans.append((i,j-1,para)); i=j; continue
            codeitems=[x for x in para if re.match(r'^\s*[*-] `[^`]+`\s*$',x)]
            if len(para)>=15 and len(codeitems)>=0.85*len(para) and all(re.match(r'^\s*[*-] ',x) for x in para):
                spans.append((i,j-1,para)); i=j; continue
            if len(para)>=5 and all(re.match(r'^\s*[*-] \[[^\]]+\]\([^)]+\)',x) and len(re.sub(r'\[[^\]]+\]\([^)]+\)','',x))<25 for x in para):
                spans.append((i,j-1,para)); i=j; continue
            if (para[0].lstrip().startswith('<') and not para[0].lstrip().startswith('<!--') and not para[0].lstrip().startswith('<br')) or all(x.lstrip().startswith('[![') for x in para):
                if para[0].lstrip().startswith(('<form','<div','<iframe','<p ','<p>','<table','<a ','<img','<center','<details','<span','<script','<style','<section','<video','<picture','<figure')) or all(x.lstrip().startswith('[![') for x in para):
                    k=j
                    if para[0].lstrip().startswith('<form') and not any('</form>' in x for x in para):
                        while k<len(lines) and '</form>' not in lines[k-1]: k+=1
                    spans.append((i,k-1,lines[i:k])); i=k; continue
            i=j
        else: i+=1
    spans.sort()
for s,e,bl in spans:
    out+=lines[last:s]
    if (not ext and (has_comment(bl) or len(bl)<=4)) or (ext and len(bl)<=3 and bl[0].lstrip().startswith(('```','~~~'))): out+=bl
    else:
        n+=1;key=f'⟦CODE{n}⟧'
        ind=bl[0][:len(bl[0])-len(bl[0].lstrip())]
        mapping[key]=json.dumps(bl)
        out.append(ind+key)
    last=e+1
out+=lines[last:]
os.makedirs(os.path.dirname(os.path.join(EWORK,rel)),exist_ok=True)
json.dump(mapping,open(os.path.join(EWORK,rel+'.json'),'w'))
print('\n'.join(out))
if ext and '--nocode' not in sys.argv:
    for k,v in mapping.items():
        bl=json.loads(v)
        if bl[0].lstrip().startswith(('```','~~~')):
            print(f'\n##### {k}'); print('\n'.join(bl))
if '--code' in sys.argv:
    base=os.path.dirname(os.path.join(EN,rel))
    seen=set()
    for m in re.finditer(r'\{\*\s*(\S+)\s*(.*?)\*\}|\{!>?\s*(\S+?)\s*!\}',t):
        if m.group(3): m=re.match(r'(.*)()',m.group(3))
        p=os.path.join(SP,'repo',re.sub(r'^(\.\./)+','',m.group(1)))
        if p in seen or not os.path.exists(p): continue
        seen.add(p)
        src=open(p,encoding='utf8').read().rstrip('\n').split('\n')
        print(f'\n##### CODE {m.group(1)} {m.group(2)}')
        for i,l in enumerate(src,1): print(f'{i:3} {l if len(l)<200 else l[:120]+" ...[truncated]"}')
