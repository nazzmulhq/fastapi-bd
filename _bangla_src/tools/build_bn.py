import os,sys,shutil,subprocess,yaml,glob,time
T0=time.time()
def TIMING(msg): print(f'[{time.time()-T0:7.1f}s] {msg}',flush=True)
subprocess.run([sys.executable,'-I',os.path.join(os.path.dirname(os.path.abspath(__file__)),'patch_venv.py')],check=True)  # griffe-typingdoc fixes
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from paths import *
os.chdir(REPO); sys.path.insert(0,os.path.join(REPO,'scripts'))
# sync sources
bn_docs=os.path.join(REPO,'docs/bn/docs'); shutil.rmtree(bn_docs,ignore_errors=True)
shutil.copytree(os.path.join(SRC,'docs'),bn_docs,ignore=shutil.ignore_patterns('_extra','pydantic','pydantic-ai'))
shutil.copy(os.path.join(SRC,'llm-prompt.md'),os.path.join(REPO,'docs/bn/llm-prompt.md'))
# PATCH_VARIANTS: translate the hard-coded English labels of markdown_include_variants (Bangla build only)
import markdown_include_variants._main as _miv
_p=_miv.__file__; _t=open(_p,encoding='utf8').read()
for _a,_b in [('🤓 Other versions and variants','🤓 অন্যান্য সংস্করণ ও ধরন'),
              ('"/// tip",','"/// tip | পরামর্শ",'),
              ('Prefer to use the `Annotated` version if possible.','সম্ভব হলে `Annotated` সংস্করণটি ব্যবহার করুন।'),
              (' - non-Annotated"',' - Annotated ছাড়া"')]:
    _t=_t.replace(_a,_b)
open(_p,'w',encoding='utf8').write(_t)
TIMING('synced sources')
import docs
TIMING('imported docs.py')
cfg_path=docs.stage_zensical_docs('bn')
stage=os.path.dirname(cfg_path)
TIMING('staged')
cfg=yaml.unsafe_load(open(cfg_path,encoding='utf8'))
# extra Bangla-only pages: _extra/<rel>.md, inserted into nav after an anchor page
extra_dir=os.path.join(SRC,'docs/_extra')
extra_nav=yaml.safe_load(open(os.path.join(extra_dir,'nav.yml'),encoding='utf8')) if os.path.exists(os.path.join(extra_dir,'nav.yml')) else []
for item in extra_nav or []:
    dst=os.path.join(stage,cfg.get('docs_dir','content'),item['page'])
    os.makedirs(os.path.dirname(dst),exist_ok=True)
    shutil.copy(os.path.join(extra_dir,item['page']),dst)
    def ins(nav):
        for i,x in enumerate(nav):
            if x==item['after'] or (isinstance(x,dict) and list(x.values())[0]==item['after']):
                nav.insert(i+1,item['page']); return True
            if isinstance(x,dict):
                v=list(x.values())[0]
                if isinstance(v,list) and ins(v): return True
        return False
    if not ins(cfg['nav']): print('nav anchor not found for',item)
# external doc sets (Pydantic, Pydantic AI): pages under docs/<name>/ (Bangla) or .build/en_ext/<name>/ (prepared English)
import json
content=os.path.join(stage,cfg.get('docs_dir','content'))
bn_banner=open(os.path.join(SRC,'docs/translation-banner.md'),encoding='utf8').read()
MISSING="""/// note | 🌐 এই পেজের সহজ বাংলা সংস্করণ এখনো তৈরি হচ্ছে

আপাতত নিচে মূল ইংরেজি লেখাটি দেখানো হচ্ছে। এই অংশের অন্য পেজগুলোতে সহজ বাংলা ব্যাখ্যা পাবেন।

[অফিসিয়াল ইংরেজি পেজ](ENGLISH_VERSION_URL)

///"""
SEC_BN={'Get Started':'শুরু করুন','Concepts':'মূল ধারণা','API Documentation':'API ডকুমেন্টেশন','Internals':'ভেতরের কাঠামো',
        'Examples':'উদাহরণ','Error Messages':'এরর বার্তা','Integrations':'ইন্টিগ্রেশন','Dev Tools':'ডেভেলপার টুল',
        'Production Tools':'প্রোডাকশন টুল',
        # Pydantic AI
        'Overview':'পরিচিতি','Core Concepts':'মূল ধারণা','Models & Providers':'মডেল ও প্রোভাইডার','Tools & Toolsets':'টুল ও টুলসেট',
        'Production':'প্রোডাকশন','Durable Execution':'টেকসই এক্সিকিউশন','Capabilities':'ক্যাপাবিলিটি','Harnesses':'হার্নেস',
        'Execution Environments':'এক্সিকিউশন পরিবেশ','Tools & Native Abilities':'টুল ও নেটিভ ক্ষমতা','Web & Research':'ওয়েব ও গবেষণা',
        'Reasoning, Planning & Delegation':'যুক্তি, পরিকল্পনা ও দায়িত্ব ভাগ','Context Management':'কনটেক্সট ব্যবস্থাপনা',
        'Knowledge & Memory':'জ্ঞান ও স্মৃতি','Control & Safety':'নিয়ন্ত্রণ ও নিরাপত্তা','Self-Extension':'নিজেকে বাড়ানো',
        'Execution Runtime':'এক্সিকিউশন রানটাইম','Loop Customization':'লুপ কাস্টমাইজেশন','Realtime (speech-to-speech)':'রিয়েলটাইম (কথা থেকে কথা)',
        'Interfaces':'ইন্টারফেস','UI Event Streams':'UI ইভেন্ট স্ট্রিম','Guides':'গাইড','Getting Started':'শুরু করা',
        'Evaluators':'মূল্যায়নকারী','How-To Guides':'কীভাবে করবেন','Graph Builder':'গ্রাফ বিল্ডার',
        'Conversational Agents':'কথোপকথনের এজেন্ট','Data & Analytics':'ডেটা ও বিশ্লেষণ','Streaming':'স্ট্রিমিং','Realtime':'রিয়েলটাইম',
        'Complex Workflows':'জটিল ওয়ার্কফ্লো','Comparisons':'তুলনা','API Reference':'API রেফারেন্স','Project':'প্রজেক্ট'}
EXT=[('pydantic','Pydantic'),('pydantic-ai','Pydantic AI')]
last_pos=None
ext_counts={}
for name,label in EXT:
    navf=os.path.join(SP,f'en_ext/{name}.nav.json')
    if not os.path.exists(navf): print('skip ext',name); continue
    tree=json.load(open(navf,encoding='utf8')); urls=json.load(open(os.path.join(SP,f'en_ext/{name}.urls.json')))
    en_root=os.path.join(SP,'en_ext',name)
    for d in os.listdir(en_root):
        if os.path.isdir(os.path.join(en_root,d)) and not any(f.endswith('.md') for _,_,fs in os.walk(os.path.join(en_root,d)) for f in fs):
            shutil.copytree(os.path.join(en_root,d),os.path.join(content,name,d),dirs_exist_ok=True)
    nb=ne=0
    def emit(rel):
        global nb,ne
        site_rel=f'{name}/{rel}'; url=urls.get(site_rel,'')
        bnf=os.path.join(SRC,'docs',site_rel)
        if os.path.exists(bnf):
            md=docs.add_markdown_notice(open(bnf,encoding='utf8').read(),bn_banner.replace('ENGLISH_VERSION_URL',url)); nb+=1
        else:
            md=docs.add_markdown_notice(open(os.path.join(en_root,rel),encoding='utf8').read(),MISSING.replace('ENGLISH_VERSION_URL',url)); ne+=1
        dst=os.path.join(content,site_rel); os.makedirs(os.path.dirname(dst),exist_ok=True)
        open(dst,'w',encoding='utf8').write(md)
        return site_rel
    def build(items,top=False):
        out=[]
        for title,v in items:
            if isinstance(v,list): out.append({SEC_BN.get(title,title):build(v)})
            else: out.append(emit(v))
        return out
    sec=build(tree)
    # Welcome page (first page of first section) becomes the tab's index page
    first=sec[0]; (k,v),=first.items(); idx=v.pop(0)
    sec=[idx]+sec
    if last_pos is None:
        last_pos=next((i for i,x in enumerate(cfg['nav']) if isinstance(x,dict) and any('reference/index.md' in str(y) for y in x.values())),len(cfg['nav'])-1)
    last_pos+=1
    cfg['nav'].insert(last_pos,{label:sec})
    ext_counts[name]=(nb,ne)
TIMING(f'ext docs {ext_counts}')
strip=lambda p:p.lstrip('/')
cfg['theme']['logo']=strip(cfg['theme']['logo']); cfg['theme']['favicon']=strip(cfg['theme']['favicon'])
cfg['extra_css']=[strip(p) for p in cfg['extra_css']]
cfg['extra_javascript']=[strip(p) for p in cfg['extra_javascript']]
cfg['site_url']=os.environ.get('BN_SITE_URL','http://localhost:8080/')
alts=cfg.get('extra',{}).get('alternate',[])
new=[{'link':'/','name':'bn - বাংলা'}]
for a in alts: new.append({'link':'https://fastapi.tiangolo.com'+a['link'],'name':a['name']})
cfg['extra']['alternate']=new
patched=os.path.join(SP,'patched_src')
if os.path.isdir(os.path.join(patched,'fastapi')):
    py=cfg['plugins']['mkdocstrings']['handlers']['python']; py['paths']=[patched]
    for extra_path in ['patched_pyd','patched_pai']:
        if os.path.isdir(os.path.join(SP,extra_path)): py['paths'].append(os.path.join(SP,extra_path))
    py.setdefault('inventories',[])
    for inv in ['https://docs.python.org/3/objects.inv','https://typing-extensions.readthedocs.io/en/latest/objects.inv']:
        if inv not in py['inventories']: py['inventories'].append(inv)
open(cfg_path,'w',encoding='utf8').write(yaml.dump(cfg,sort_keys=False,width=200,allow_unicode=True))
site=os.path.join(stage,cfg['site_dir']); shutil.rmtree(site,ignore_errors=True)
TIMING('config written'); subprocess.run([os.path.join(os.path.dirname(sys.executable),'zensical'),'build','--config-file',os.path.basename(cfg_path)],check=True,cwd=stage)
TIMING('zensical done'); out=os.path.join(SP,'site_bn'); shutil.rmtree(out,ignore_errors=True); shutil.copytree(site,out)
TIMING('copied out'); print('built ->',out)
