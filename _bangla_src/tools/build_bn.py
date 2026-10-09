import os,sys,shutil,subprocess,yaml,glob,time
T0=time.time()
def TIMING(msg): print(f'[{time.time()-T0:7.1f}s] {msg}',flush=True)
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from paths import *
os.chdir(REPO); sys.path.insert(0,os.path.join(REPO,'scripts'))
# sync sources
bn_docs=os.path.join(REPO,'docs/bn/docs'); shutil.rmtree(bn_docs,ignore_errors=True)
shutil.copytree(os.path.join(SRC,'docs'),bn_docs,ignore=shutil.ignore_patterns('_extra'))
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
open(cfg_path,'w',encoding='utf8').write(yaml.dump(cfg,sort_keys=False,width=200,allow_unicode=True))
site=os.path.join(stage,cfg['site_dir']); shutil.rmtree(site,ignore_errors=True)
TIMING('config written'); subprocess.run([os.path.join(os.path.dirname(sys.executable),'zensical'),'build','--config-file',os.path.basename(cfg_path)],check=True,cwd=stage)
TIMING('zensical done'); out=os.path.join(SP,'site_bn'); shutil.rmtree(out,ignore_errors=True); shutil.copytree(site,out)
TIMING('copied out'); print('built ->',out)
