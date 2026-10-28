"""Prepare English Pydantic AI docs for the Bangla site.

Reads the pydantic-ai repo (.build/src/pai, sparse checkout) as DATA only (no code from it is executed),
re-implements what the upstream docs build does (model alias placeholders, `pip/uv-add` and `py-cli`
command tabs, ```snippet``` file includes with fragments, front matter titles), rewrites links to
pydantic.dev/docs/ai pages into local links, converts Material syntax to this site's syntax
(tools/mkconv.py) and writes:
  .build/en_ext/pydantic-ai/<path>.md   prepared English pages (the "EN" side for eprep/efinish)
  .build/en_ext/pydantic-ai/img         assets
  .build/en_ext/pydantic-ai.nav.json    nav tree [[title, rel | children]]
  .build/en_ext/pydantic-ai.urls.json   rel -> official English URL on pydantic.dev
  .build/patched_pai/                   package sources for mkdocstrings, docstring doc-links made site-absolute
Run with: python -I tools/ai_prep.py
"""
import os, sys, re, json, shutil, posixpath
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import SP
import yaml
from mkconv import material_to_site

REPO = os.path.join(SP, 'src/pai')
DOCS = os.path.join(REPO, 'docs')
NAME = 'pydantic-ai'
OUT = os.path.join(SP, 'en_ext', NAME)
BASE = 'https://pydantic.dev/docs/ai/'
GH = 'https://github.com/pydantic/pydantic-ai/blob/main/'
# allow_inspection False: griffe must only parse these sources statically, never import them
MK_DEFAULTS = {'inherited_members': False, 'show_if_no_docstring': False, 'allow_inspection': False,
               'docstring_options': {'ignore_init_summary': True}, 'show_root_heading': True}
HARNESS = os.path.join(SP, 'src/harness')
FENCE = re.compile(r'^(\s*)(`{3,}|~{3,})(.*)$')


def load_nav():
    data = yaml.safe_load(open(os.path.join(DOCS, 'navigation.yml'), encoding='utf8'))
    pages, slug_to_path = [], {}

    def walk(items):
        res = []
        for it in items:
            if 'section' in it:
                kids = walk(it.get('contents', []))
                if kids: res.append([it['section'], kids])
            elif 'page' in it and it.get('path'):
                p, slug = it['path'], it.get('slug', '')
                pages.append((p, slug)); res.append([it['page'], p])
                slug_to_path[slug.strip('/')] = p
                for a in it.get('aliases') or []:
                    slug_to_path.setdefault(a.strip('/'), p)
        return res
    nav = walk(data['navigation'])
    for r in data.get('redirects') or []:
        tgt = slug_to_path.get(r['to'].strip('/'))
        if tgt: slug_to_path.setdefault(r['from'].strip('/'), tgt)
    return nav, pages, slug_to_path


ALIASES = json.load(open(os.path.join(DOCS, 'model_aliases/aliases.json'), encoding='utf8'))


def aliases(md):
    def rep(m):
        key, name = m.group(1), m.group(2)
        val = ALIASES.get(key)
        if val is None: return m.group(0)
        return val.split(':', 1)[1] if name else val
    return re.sub(r'\{\{ *([a-z0-9-]+:[a-z0-9-]+)(\.name)? *\}\}', rep, md)


def fence_end(lines, i):
    f = FENCE.match(lines[i]).group(2)
    for j in range(i + 1, len(lines)):
        if re.match(r'^\s*' + re.escape(f[0]) + '{' + str(len(f)) + r',}\s*$', lines[j]): return j
    return len(lines) - 1


def command_tabs(md):
    """```bash fences whose lines are `pip/uv-add ...` or `py-cli ...` -> pip / uv content tabs (Material syntax)"""
    lines = md.split('\n'); out = []; i = 0
    while i < len(lines):
        m = FENCE.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        e = fence_end(lines, i); body = lines[i + 1:e]
        if any(re.match(r'^\s*(pip/uv-add|py-cli)\b', b) for b in body):
            ind, f, info = m.group(1), m.group(2), m.group(3)
            def conv(tool):
                res = []
                for b in body:
                    s = b[len(ind):] if b.startswith(ind) else b.lstrip()
                    if s.startswith('pip/uv-add '): s = ('pip install ' if tool == 'pip' else 'uv add ') + s[len('pip/uv-add '):]
                    elif s.startswith('py-cli '): s = s[len('py-cli '):] if tool == 'pip' else 'uv run ' + s[len('py-cli '):]
                    res.append(s)
                return res
            for tool in ('pip', 'uv'):
                out += [f'{ind}=== "{tool}"', '', f'{ind}    {f}{info}'] + [f'{ind}    {x}' if x else '' for x in conv(tool)] + [f'{ind}    {f}', '']
            i = e + 1; continue
        out += lines[i:e + 1]; i = e + 1
    return '\n'.join(out)


LANG = {'.py': 'python', '.html': 'html', '.ts': 'typescript', '.js': 'javascript', '.json': 'json', '.toml': 'toml', '.yaml': 'yaml', '.yml': 'yaml', '.css': 'css', '.sh': 'bash'}


def snippet_text(path, fragments):
    full = os.path.join(REPO, path.lstrip('/'))
    if not os.path.exists(full): return None
    src = open(full, encoding='utf8').read().split('\n')
    if not fragments:  # whole file, fragment markers removed
        res = []
        for l in src:
            m = re.search(r'\s*### \[/?[^\]]*\]\s*$', l)
            if m:
                if l[:m.start()].strip(): res.append(l[:m.start()].rstrip())
                continue
            res.append(l)
        return '\n'.join(res).strip('\n')
    want = set(fragments.split()); active = set(); res = []
    for l in src:
        m = re.search(r'### \[(/?)([^\]]*)\]\s*$', l)
        content = l[:m.start()].rstrip() if m else l
        opening = m and not m.group(1)
        names = set(m.group(2).split(',')) if m else set()
        if opening: active |= names
        if (active & want) and (content.strip() or not m): res.append(content)
        if m and m.group(1): active -= names
    # dedent common indentation
    ind = min((len(x) - len(x.lstrip()) for x in res if x.strip()), default=0)
    return '\n'.join(x[ind:] for x in res).strip('\n')


def snippets(md):
    def rep(m):
        ind, attrs = m.group(1), m.group(2)
        path = re.search(r'path="([^"]+)"', attrs).group(1)
        frag = re.search(r'fragment="([^"]*)"', attrs)
        title = re.search(r'title="([^"]*)"', attrs)
        text = snippet_text(path, frag.group(1) if frag else None)
        if text is None:
            return f'{ind}[`{path}`]({GH}{path.lstrip("/")})'
        lang = LANG.get(os.path.splitext(path)[1], '')
        t = title.group(1) if title else path.lstrip('/').replace('examples/', '', 1)
        body = '\n'.join((ind + x) if x else '' for x in text.split('\n'))
        return f'{ind}```{lang} title="{t}"\n{body}\n{ind}```'
    # single-line form ```snippet {...}``` and two-line form ```snippet {...}\n```
    md = re.sub(r'^( *)```snippet (\{[^\n}]*\})```[ \t]*$', rep, md, flags=re.M)
    md = re.sub(r'^( *)```snippet (\{[^\n}]*\})[ \t]*\n\1```[ \t]*$', rep, md, flags=re.M)
    return md


def site_url(p):
    """docs path -> site-absolute URL of our page"""
    p = p[:-3]
    if p == 'index': return f'/{NAME}/'
    if p.endswith('/index'): p = p[:-6]
    return f'/{NAME}/{p}/'


def localize_links(md, rel, page_set, slug_to_path):
    here = posixpath.dirname(rel)
    def to_rel(target, frag):
        return posixpath.relpath(target, here or '.') + (frag or '')
    def ext(m):
        slug, frag = m.group(1).strip('/'), m.group(2) or ''
        tgt = slug_to_path.get(slug)
        if tgt and tgt in page_set: return f']({to_rel(tgt, frag)})'
        return m.group(0)
    md = re.sub(r'\]\(https://pydantic\.dev/docs/ai/([^)#\s]*?)/?(#[^)\s]*)?\)', ext, md)
    def internal(m):
        target, frag = m.group(1), m.group(2) or ''
        if re.match(r'^[a-z]+:', target): return m.group(0)
        full = posixpath.normpath(posixpath.join(here, target))
        if full in page_set: return m.group(0)
        if full.startswith('../'): return m.group(0)
        return f']({GH}docs/{full}{frag})'
    return re.sub(r'\]\(([^)#\s]+\.md)(#[^)\s]*)?\)', internal, md)


def public_trace(md):
    """custom `/// public-trace | url` blocks (embedded Logfire trace) -> an info box with a link"""
    def rep(m):
        ind, url, title = m.group(1), m.group(2), m.group(3) or 'Logfire trace'
        return f'{ind}/// info | Logfire trace\n\n{ind}[{title}]({url})\n\n{ind}///'
    return re.sub(r"^( *)/// public-trace \| (\S+)\n(?:\1    title: '(.*?)'\n)?\1///", rep, md, flags=re.M)


def _harness_has(dotted):
    """static check that a pydantic_ai_harness object exists in the checked-out harness sources"""
    root = os.path.join(HARNESS, 'pydantic_ai_harness')
    parts = dotted.split('.')[1:]
    obj = parts[-1] if parts else ''
    mod = parts[:-1]
    base = os.path.join(root, *mod)
    files = []
    if os.path.isdir(base):  # a package: the name must be defined or re-exported in its __init__
        files = [os.path.join(base, '__init__.py')] if os.path.isfile(os.path.join(base, '__init__.py')) else []
    elif os.path.isfile(base + '.py'):
        files = [base + '.py']
    elif os.path.isdir(root) and not mod:
        files = [os.path.join(root, '__init__.py')]
    if not files: return False
    o = re.escape(obj)
    pat = re.compile(r'^\s*(?:class|def|async def)\s+' + o + r'\b|^' + o + r'\s*[:=]|^\s*(?:from\s+\S+\s+)?import\b[^\n]*\b' + o + r'\b|^\s+' + o + r',?\s*(?:#.*)?$', re.M)
    return any(pat.search(open(f, encoding='utf8').read()) for f in files)


def missing_api(md, url):
    """`::: pydantic_ai_harness...` blocks for objects that are not in the public harness sources -> link to the official page"""
    lines = md.split('\n'); out = []; i = 0
    while i < len(lines):
        m = re.match(r'^( *)::: (pydantic_ai_harness[\w.]*)\s*$', lines[i])
        if m and not _harness_has(m.group(2)):
            ind = m.group(1); j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].startswith(ind + '    ')):
                if not lines[j].strip() and (j + 1 >= len(lines) or not lines[j + 1].startswith(ind + '    ')): break
                j += 1
            out += [f'{ind}/// info | API reference', '', f'{ind}The API reference for `{m.group(2)}` is available in the [official documentation]({url}).', '', f'{ind}///']
            i = j; continue
        out.append(lines[i]); i += 1
    return '\n'.join(out)


def front_matter(md):
    fm = {}
    m = re.match(r'^---\n(.*?)\n---\n', md, re.S)
    if m:
        try: fm = yaml.safe_load(m.group(1)) or {}
        except Exception: fm = {}
        md = md[m.end():]
    return fm, md


def patch_source(slug_to_path, page_set):
    dst = os.path.join(SP, 'patched_pai')
    shutil.rmtree(dst, ignore_errors=True)
    for pkg_dir, pkg in [('pydantic_ai_slim', 'pydantic_ai'), ('pydantic_graph', 'pydantic_graph'), ('pydantic_evals', 'pydantic_evals')]:
        shutil.copytree(os.path.join(REPO, pkg_dir, pkg), os.path.join(dst, pkg), ignore=shutil.ignore_patterns('__pycache__'))
    if os.path.isdir(os.path.join(HARNESS, 'pydantic_ai_harness')):  # separate repo, documented in the harness/ pages
        shutil.copytree(os.path.join(HARNESS, 'pydantic_ai_harness'), os.path.join(dst, 'pydantic_ai_harness'), ignore=shutil.ignore_patterns('__pycache__'))
    def rel_md(m):
        path, frag = m.group(1), m.group(2) or ''
        target = posixpath.normpath(path.lstrip('./') if not path.startswith('../') else path[3:])
        while target.startswith('../'): target = target[3:]
        if target in page_set: return f']({site_url(target)}{frag})'
        return f']({GH}docs/{target}{frag})'
    def abs_ai(m):
        slug, frag = m.group(1).strip('/'), m.group(2) or ''
        tgt = slug_to_path.get(slug)
        return f']({site_url(tgt)}{frag})' if tgt and tgt in page_set else m.group(0)
    # **kwargs: Unpack[SomeTypedDict] where the TypedDict comes from a third-party package that is not
    # available to the docs build (e.g. temporalio) crashes griffe-typingdoc: annotate those kwargs as Any instead
    local = ('pydantic_ai', 'pydantic_graph', 'pydantic_evals', 'pydantic_ai_harness', 'pydantic', 'pydantic_core', 'typing',
             'typing_extensions', 'collections', 'dataclasses')
    for root, _, files in os.walk(dst):
        for f in files:
            if not f.endswith('.py'): continue
            fp = os.path.join(root, f); t = open(fp, encoding='utf8').read()
            if 'Unpack[' not in t: continue
            ext_names = set()
            for mod, names in re.findall(r'^\s*from\s+([\w.]+)\s+import\s+\(?([^)\n]*(?:\n[^)]*)?)\)?', t, re.M):
                if mod.split('.')[0] not in local and not mod.startswith('.'):
                    ext_names |= set(re.findall(r'\b(\w+)\b(?:\s+as\s+\w+)?', names)) - {'as', 'import'}
            t2 = re.sub(r'(\*\*\w+:\s*)Unpack\[(\w+)\]', lambda m: m.group(1) + 'Any' if m.group(2) in ext_names else m.group(0), t)
            if t2 != t: open(fp, 'w', encoding='utf8').write(t2)
    n = 0
    for root, _, files in os.walk(dst):
        for f in files:
            if f.endswith(('.py', '.pyi')):
                fp = os.path.join(root, f); t = open(fp, encoding='utf8').read()
                t2, k1 = re.subn(r'\]\(((?:\.\./|\./)*[A-Za-z0-9_/.-]+\.md)(#[^)]*)?\)', rel_md, t)
                t2, k2 = re.subn(r'\]\(https://pydantic\.dev/docs/ai/([^)#\s]*?)/?(#[^)\s]*)?\)', abs_ai, t2)
                if k1 or k2: open(fp, 'w', encoding='utf8').write(t2); n += k1 + k2
    print('patched doc links in sources:', n)


def main():
    nav, pages, slug_to_path = load_nav()
    page_set = {p for p, _ in pages}
    patch_source(slug_to_path, page_set)
    titles = {}
    def collect(items):
        for t, v in items:
            if isinstance(v, list): collect(v)
            else: titles.setdefault(v, t)
    collect(nav)
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT, exist_ok=True)
    urls = {}
    for rel, slug in pages:
        md = open(os.path.join(DOCS, rel), encoding='utf8').read()
        fm, md = front_matter(md)
        md = aliases(md)
        md = snippets(md)
        md = command_tabs(md)
        md = public_trace(md)
        md = localize_links(md, rel, page_set, slug_to_path)
        if not re.match(r'^\s*# ', md):
            md = f'# {fm.get("title") or titles.get(rel, rel)}\n\n' + md.lstrip('\n')
        url = BASE + (slug.strip('/') + '/' if slug.strip('/') else '')
        md = missing_api(md, url)
        dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf8').write(material_to_site(md, MK_DEFAULTS))
        urls[f'{NAME}/{rel}'] = url
    for d in ['img']:
        if os.path.isdir(os.path.join(DOCS, d)):
            shutil.copytree(os.path.join(DOCS, d), os.path.join(OUT, d), dirs_exist_ok=True)
    json.dump(nav, open(os.path.join(SP, f'en_ext/{NAME}.nav.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(urls, open(os.path.join(SP, f'en_ext/{NAME}.urls.json'), 'w'), indent=1)
    print('pages', len(pages))


if __name__ == '__main__':
    main()
