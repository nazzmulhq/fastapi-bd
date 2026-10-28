"""Prepare English Pydantic (validation) docs for the Bangla site.

Reads the pydantic repo (.build/src/pydantic) as DATA only (no code from it is executed), re-implements the
content the upstream docs hooks generate (json output, org grid, library list, schema table, conversion
table, devtools example, people), converts Material syntax to this site's syntax (tools/mkconv.py) and writes:
  .build/en_ext/pydantic/<rel>.md   prepared English pages (the "EN" side for eprep/efinish)
  .build/en_ext/pydantic/{img,logos} assets
  .build/en_ext/pydantic.nav.json   nav tree [[title, rel | children]]
  .build/en_ext/pydantic.urls.json  rel -> official English URL on pydantic.dev
Run with: python -I tools/pyd_prep.py
"""
import os, sys, re, json, shutil, ast, textwrap, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import SP
import yaml, tomli
from mkconv import material_to_site

REPO = os.path.join(SP, 'src/pydantic')
DOCS = os.path.join(REPO, 'docs')
PLUG = os.path.join(DOCS, 'plugins')
OUT = os.path.join(SP, 'en_ext/pydantic')
BASE = 'https://pydantic.dev/docs/validation/latest/'
MK_DEFAULTS = {'inherited_members': False, 'show_if_no_docstring': False,
               'docstring_options': {'ignore_init_summary': True}, 'show_root_heading': True}


def url_for(rel):
    p = rel[:-3]
    gs = ['why', 'help_with_pydantic', 'enterprise-support', 'install', 'migration', 'version-policy',
          'contributing', 'changelog']
    if p == 'index': return BASE + 'get-started/'
    if p in gs: return BASE + f'get-started/{p}/'
    if p == 'pydantic_people': return BASE + 'pydantic-people/pydantic_people/'
    if p.startswith('api/'):
        n = p[4:]
        if n.startswith('pydantic_core'): return BASE + f'api/pydantic-core/{n}/'
        if n.startswith('pydantic_extra_types'): return BASE + f'api/pydantic-extra-types/{n}/'
        if n == 'pydantic_settings': return BASE + 'api/pydantic_settings/'
        return BASE + f'api/pydantic/{n}/'
    if p.startswith('integrations/'):
        n = p.split('/', 1)[1]
        if n in ('logfire', 'llms', 'aws_lambda'): return BASE + f'integrations/{n}/'
        return BASE + f'integrations/dev-tools/{n}/'
    return BASE + p + '/'


# ---------- re-implemented generated content ----------
def json_output(md):
    """```python {output="json"} blocks whose last statement prints JSON inside a trailing triple-quoted string:
    move that JSON into a separate ```json block (same idea as the upstream hook)."""
    def repl(m):
        start, attrs, code = m.groups()
        def last(m2):
            ind, js = m2.groups()
            try:
                js = textwrap.indent(json.dumps(json.loads(js), indent=2), ind)
            except Exception:
                return m2.group(0)
            return f'\n{ind}```\n\n{ind}JSON output:\n\n{ind}```json\n{js}\n'
        code = re.sub(r'\n( *)"""(.*?)\1"""\n$', last, code, flags=re.S)
        return f'{start}{attrs}{code}{start}\n'
    return re.sub(r'(^ *```)([^\n]*?output="json"[^\n]*?\n)(.+?)\1', repl, md, flags=re.M | re.S)


def toml(name):
    with open(os.path.join(PLUG, name), 'rb') as f:
        return tomli.load(f)


def orgs():
    return toml('orgs.toml')['orgs']


def render_index(md):
    ver = re.search(r'^VERSION ?= (["\'])(.+)\1', open(os.path.join(REPO, 'pydantic/version.py')).read(), re.M).group(2)
    md = re.sub(r'{{ *version *}}', f'Documentation for version: [v{ver}](https://github.com/pydantic/pydantic/releases)', md)
    tiles = ''.join(f'<a href="why/#org-{o["key"]}" title="{o["name"]}"><img src="logos/{o["key"]}_logo.png" alt="{o["name"]}" style="height:48px;width:auto;margin:.4rem .8rem"/></a>' for o in orgs())
    return re.sub(r'{{ *organisations *}}', f'<div style="display:flex;flex-wrap:wrap;align-items:center">{tiles}</div>', md)


def render_why(md):
    libs = '\n'.join('* [`{repo}`](https://github.com/{repo}) {stars:,} stars'.format(**l) for l in toml('using.toml')['libs'])
    md = re.sub(r'{{ *libraries *}}', libs, md)
    dd = '_(Based on the criteria described above)_'
    els = [f'### {o["name"]} {{#org-{o["key"]}}}\n\n{o.get("description") or dd}' for o in orgs()]
    return re.sub(r'{{ *organisations *}}', '\n\n'.join(els), md)


def render_settings(md):
    txt = subprocess.run(['curl', '-sL', '--max-time', '60', 'https://raw.githubusercontent.com/pydantic/pydantic-settings/main/docs/index.md'],
                         capture_output=True, text=True).stdout.strip()
    if not txt:
        raise SystemExit('could not download pydantic-settings docs')
    return re.sub(r'{{ *pydantic_settings *}}', lambda m: txt, md)


def row(cols):
    return f'| {" | ".join(cols)} |\n'


def schema_table(md):
    t = row(['Python type', 'JSON Schema Type', 'Additional JSON Schema', 'Defined in', 'Notes']) + row(['-'] * 5)
    for r in toml('schema_mappings.toml').values():
        add = r['additional']
        if add and not isinstance(add, str): add = json.dumps(add)
        t += row([f'`{r["py_type"]}`', f'`{r["json_type"]}`', f'`{add}`' if add else '', r['defined_in'], r['notes']])
    return re.sub(r'{{ *schema_mappings_table *}}', lambda m: t, md)


def conversion_rows():
    tree = ast.parse(open(os.path.join(PLUG, 'conversion_table.py'), encoding='utf8').read())
    lst = next(n.value for n in tree.body if isinstance(n, ast.AnnAssign) and getattr(n.target, 'id', '') == 'table_rows')
    def tname(node):
        if isinstance(node, ast.Constant): return str(node.value)
        if isinstance(node, ast.Name): return node.id
        if isinstance(node, ast.Attribute): return node.attr
        return ast.unparse(node)
    rows = []
    for c in lst.elts:
        fields = ['field_type', 'input_type', 'python_input', 'json_input', 'strict', 'condition']
        d = {'python_input': False, 'json_input': False, 'strict': False, 'condition': None}
        for i, a in enumerate(c.args):
            d[fields[i]] = tname(a) if i < 2 else ast.literal_eval(a)
        for k in c.keywords:
            d[k.arg] = tname(k.value) if k.arg in ('field_type', 'input_type') else ast.literal_eval(k.value)
        rows.append(d)
    def src(r):
        return 'Python & JSON' if r['python_input'] and r['json_input'] else 'Python' if r['python_input'] else 'JSON' if r['json_input'] else ''
    for r in rows: r['src'] = src(r)
    rows.sort(key=lambda r: ((r['field_type'] or ' ')[0].isupper(), r['field_type'] or ' ', (r['input_type'] or ' ')[0].isupper(), r['input_type'] or ' ', r['src']))
    return rows


def conversion_table(md):
    rows = conversion_rows()
    o, c = '<span style="white-space: nowrap;">', '</span>'
    preds = {'all': lambda r: True, 'json': lambda r: r['json_input'], 'json_strict': lambda r: r['json_input'] and r['strict'],
             'python': lambda r: r['python_input'], 'python_strict': lambda r: r['python_input'] and r['strict']}
    for tid, p in preds.items():
        lines = [row(['Field Type', 'Input', 'Strict', 'Input Source', 'Conditions']).rstrip('\n'), row(['-'] * 5).rstrip('\n')]
        for r in filter(p, rows):
            lines.append(row([f'{o}`{r["field_type"]}`{c}', f'{o}`{r["input_type"]}`{c}', '✓' if r['strict'] else '',
                              f'{o}{r["src"]}{c}', r['condition'] or '']).rstrip('\n'))
        tbl = textwrap.indent('\n'.join(lines), '    ')
        md = re.sub(r'{{ *conversion_table_' + tid + r' *}}', lambda m: tbl, md)
    return md


def devtools(md):
    html = open(os.path.join(PLUG, 'devtools_output.html'), encoding='utf8').read().strip('\n')
    return re.sub(r'{{ *devtools_example *}}', lambda m: f'<div class="highlight">\n<pre><code>{html}</code></pre>\n</div>', md)


def people(md):
    ppl = yaml.safe_load(open(os.path.join(PLUG, 'people.yml'), encoding='utf8'))
    def lst(key, label):
        users = ''.join(
            f'<div class="user"><a href="{u["url"]}" target="_blank"><div class="avatar-wrapper"><img src="{u["avatarUrl"]}"/></div>'
            f'<div class="title">@{u["login"]}</div></a>' + (f'<div class="count">{label}: {u["count"]}</div>' if label else '') + '</div>'
            for u in ppl.get(key, []))
        return f'<div class="user-list user-list-center">{users}</div>'
    for name, key, label in [('experts', 'experts', 'Questions replied'), ('most_active_users', 'last_month_active', 'Questions replied'),
                             ('top_contributors', 'top_contributors', 'Contributions'), ('top_reviewers', 'top_reviewers', 'Reviews'),
                             ('maintainers', 'maintainers', None)]:
        md = re.sub(r'{{ ' + name + ' }}', lambda m, k=key, lb=label: lst(k, lb), md)
    return md


SPECIAL = {'index.md': render_index, 'why.md': render_why, 'concepts/pydantic_settings.md': render_settings,
           'concepts/json_schema.md': schema_table, 'concepts/conversion_table.md': conversion_table,
           'integrations/devtools.md': devtools, 'pydantic_people.md': people}


def page_md(rel):
    if rel == 'changelog.md':
        h = open(os.path.join(REPO, 'HISTORY.md'), encoding='utf8').read()
        h = re.sub(r'(\s)@([\w\-]+)', r'\1[@\2](https://github.com/\2)', h, flags=re.I)
        return h.replace('@@', '@')
    md = open(os.path.join(DOCS, rel), encoding='utf8').read()
    md = json_output(md)
    if rel in SPECIAL:
        md = SPECIAL[rel](md)
    return md


def patch_source():
    """copy of the pydantic sources for mkdocstrings, with docstring doc-links made site-absolute (/pydantic/...)"""
    dst = os.path.join(SP, 'patched_pyd')
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(REPO, 'pydantic'), os.path.join(dst, 'pydantic'), ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(os.path.join(REPO, 'pydantic-core/python/pydantic_core'), os.path.join(dst, 'pydantic_core'), ignore=shutil.ignore_patterns('__pycache__'))
    special = {'usage/types/extra_types/color_types': 'api/pydantic_extra_types_color'}
    def fix(m):
        path, frag = m.group(1), m.group(2) or ''
        parts = path.split('/')
        if path.startswith('../'):
            target = path[3:]
        elif path.startswith('./'):
            target = 'api/' + path[2:]
        else:
            target = 'api/' + path
        target = target[:-3]
        target = special.get(target, target)
        return f'](/pydantic/{target}/{frag})'
    n = 0
    for root, _, files in os.walk(dst):
        for f in files:
            if f.endswith(('.py', '.pyi')):
                fp = os.path.join(root, f); t = open(fp, encoding='utf8').read()
                t2, k = re.subn(r'\]\(((?:\.\./|\./)?[a-z_/.-]+\.md)(#[^)]*)?\)', fix, t)
                if k: open(fp, 'w', encoding='utf8').write(t2); n += k
    print('patched doc links in sources:', n)


def main():
    patch_source()
    class L(yaml.SafeLoader): pass
    L.add_multi_constructor('!', lambda loader, suffix, node: None)
    L.add_multi_constructor('tag:yaml.org,2002:python', lambda loader, suffix, node: None)
    cfg = yaml.load(open(os.path.join(REPO, 'mkdocs.yml'), encoding='utf8'), Loader=L)
    pages = []
    def walk(items):
        res = []
        for it in items:
            if isinstance(it, str):
                res.append([None, it]); pages.append(it); continue
            (title, v), = it.items()
            if isinstance(v, list): res.append([title, walk(v)])
            elif not v.startswith('http'): res.append([title, v]); pages.append(v)
        return res
    nav = walk(cfg['nav'])
    os.makedirs(OUT, exist_ok=True)
    urls = {}
    for rel in pages:
        md = page_md(rel)
        if md.startswith('---\n'):
            md = re.sub(r'^---\n.*?\n---\n', '', md, count=1, flags=re.S)
        if not re.match(r'^\s*# ', md):
            title = next((t for t, r in [(t, r) for t, r in flat(nav)] if r == rel), rel)
            md = f'# {title}\n\n' + md
        dst = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf8').write(material_to_site(md, MK_DEFAULTS))
        urls['pydantic/' + rel] = url_for(rel)
    for d in ['img', 'logos']:
        if os.path.isdir(os.path.join(DOCS, d)):
            shutil.copytree(os.path.join(DOCS, d), os.path.join(OUT, d), dirs_exist_ok=True)
    json.dump(nav, open(os.path.join(SP, 'en_ext/pydantic.nav.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(urls, open(os.path.join(SP, 'en_ext/pydantic.urls.json'), 'w'), indent=1)
    print('pages', len(pages))


def flat(nav):
    for t, v in nav:
        if isinstance(v, list): yield from flat(v)
        else: yield t, v


if __name__ == '__main__':
    main()
