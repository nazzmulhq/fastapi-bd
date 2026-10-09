"""Build the Bangla docs as a self-contained site (assets local, root-relative)."""
import os,sys,shutil,subprocess,yaml
SP=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO=os.path.join(SP,'repo'); os.chdir(REPO); sys.path.insert(0,os.path.join(REPO,'scripts'))
import docs
cfg_path=docs.stage_zensical_docs('bn')
cfg=yaml.unsafe_load(open(cfg_path,encoding='utf8'))
strip=lambda p:p.lstrip('/')
cfg['theme']['logo']=strip(cfg['theme']['logo']); cfg['theme']['favicon']=strip(cfg['theme']['favicon'])
cfg['extra_css']=[strip(p) for p in cfg['extra_css']]
cfg['extra_javascript']=[strip(p) for p in cfg['extra_javascript']]
cfg['site_url']=os.environ.get('BN_SITE_URL','http://localhost:8080/')
alts=cfg.get('extra',{}).get('alternate',[])
new=[{'link':'/','name':'bn - বাংলা'}]
for a in alts:
    l=a['link']; new.append({'link':'https://fastapi.tiangolo.com'+l,'name':a['name']})
cfg['extra']['alternate']=new
patched=os.path.join(SP,'patched_src')
if os.path.isdir(os.path.join(patched,'fastapi')):
    py=cfg['plugins']['mkdocstrings']['handlers']['python']; py['paths']=[patched]
open(cfg_path,'w',encoding='utf8').write(yaml.dump(cfg,sort_keys=False,width=200,allow_unicode=True))
site=os.path.join(os.path.dirname(cfg_path),cfg['site_dir']); shutil.rmtree(site,ignore_errors=True)
subprocess.run(['zensical','build','--config-file',os.path.basename(cfg_path)],check=True,cwd=os.path.dirname(cfg_path))
out=os.path.join(SP,'site_bn'); shutil.rmtree(out,ignore_errors=True); shutil.copytree(site,out)
print('built ->',out)
