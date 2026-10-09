import os
SRC=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP=os.environ.get('BN_SP','/private/tmp/claude-501/-Users-nazmulhaque-Desktop-fastapi/be144999-a451-4d94-9f2b-4d8452f63251/scratchpad')
REPO=os.path.join(SP,'repo')
SITE_PKGS=os.path.join(SP,'venv/lib/python3.11/site-packages')
