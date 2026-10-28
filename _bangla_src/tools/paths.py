import os
SRC=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP=os.environ.get('BN_SP','/Users/nazmulhaque/Desktop/fastapi/_bangla_src/.build')
REPO=os.path.join(SP,'repo')
SITE_PKGS=os.path.join(SP,'venv/lib/python3.11/site-packages')
