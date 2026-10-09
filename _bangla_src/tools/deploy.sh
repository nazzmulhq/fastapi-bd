#!/bin/bash
# Build the Bangla site and deploy it to the project root (served by python -m http.server 8080)
set -e
SRC=/Users/nazmulhaque/Desktop/fastapi/_bangla_src
ROOT=/Users/nazmulhaque/Desktop/fastapi
SP=${BN_SP:-/private/tmp/claude-501/-Users-nazmulhaque-Desktop-fastapi/be144999-a451-4d94-9f2b-4d8452f63251/scratchpad}
cd "$SRC"
"$SP/venv/bin/python" tools/build_bn.py > "$SP/build.log" 2>&1 || { tail -30 "$SP/build.log"; exit 1; }
grep -iE "warn|error" "$SP/build.log" || true
rsync -a --delete --exclude '_backup_old_site' --exclude '_bangla_src' --exclude '.git' --exclude '.gitignore' "$SP/site_bn/" "$ROOT/"
python3 "$SRC/tools/localize_links.py" "$ROOT"
python3 "$SRC/tools/linkcheck.py" "$ROOT"
echo deployed
