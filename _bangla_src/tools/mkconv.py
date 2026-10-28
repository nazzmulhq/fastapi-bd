"""Convert Material-for-MkDocs markdown (Pydantic / Pydantic AI docs) to the FastAPI site's syntax.

- `!!! type "Title"` / `??? type "Title"` admonitions -> `/// type | Title` blocks (pymdownx.blocks)
- `=== "Tab"` content tabs -> `/// tab | Tab` blocks
- nesting is handled by giving outer blocks more slashes
- fence attributes `{test="skip" ...}` dropped (hl_lines/title kept), `py` -> `python`
- icon shortcodes (:material-x:, :simple-x:, ...) removed
- every heading gets an explicit `{ #slug }` anchor (same slug Python-Markdown's toc would make)
"""
import re, unicodedata, yaml

ALLOWED = {'note', 'attention', 'caution', 'danger', 'error', 'tip', 'hint', 'warning', 'info', 'check'}
TYPE_MAP = {'abstract': 'info', 'summary': 'info', 'tldr': 'info', 'todo': 'info', 'important': 'attention',
            'success': 'check', 'done': 'check', 'question': 'note', 'help': 'note', 'faq': 'note',
            'failure': 'error', 'fail': 'error', 'missing': 'error', 'bug': 'danger', 'example': 'tip',
            'quote': 'note', 'cite': 'note', 'experimental': 'warning', 'api': 'info', 'seealso': 'info',
            'version-added': 'info', 'deprecated': 'warning'}

OPEN = re.compile(r'^(\s*)(!!!|\?\?\?\+?)\s*([\w-]+)((?:\s+[\w-]+)*)(?:\s+(?:"(.*?)"|\'(.*?)\'))?\s*$')
TAB = re.compile(r'^(\s*)===(\+?)\s+"(.*?)"\s*(?:\{[^}]*\})?\s*$')  # optional trailing {#anchor} is dropped
FENCE = re.compile(r'^(\s*)(`{3,}|~{3,})(.*)$')


def _indent(l):
    return len(l) - len(l.lstrip(' '))


def _fence_end(lines, i):
    m = FENCE.match(lines[i]); f = m.group(2)
    j = i + 1
    while j < len(lines):
        if re.match(r'^\s*' + re.escape(f[0]) + '{' + str(len(f)) + r',}\s*$', lines[j]):
            return j
        j += 1
    return len(lines) - 1


def _body(lines, i, k):
    """lines of an indented body starting after line i, for a marker at indent k"""
    j = i + 1
    while j < len(lines):
        l = lines[j]
        if l.strip() and _indent(l) < k + 4:
            break
        j += 1
    while j > i + 1 and not lines[j - 1].strip():
        j -= 1
    return j


def convert(lines):
    """returns (out_lines, depth)"""
    out, depth, i = [], 0, 0
    while i < len(lines):
        l = lines[i]
        if FENCE.match(l):
            e = _fence_end(lines, i); out += lines[i:e + 1]; i = e + 1; continue
        m, t = OPEN.match(l), TAB.match(l)
        if m or t:
            k = _indent(l); ind = ' ' * k
            j = _body(lines, i, k)
            body = [x[k + 4:] if len(x) >= k + 4 else x.lstrip(' ') for x in lines[i + 1:j]]
            while body and not body[0].strip(): body.pop(0)
            inner, d = convert(body)
            sl = '/' * (3 + d)
            if t:
                head = [f'{ind}{sl} tab | {t.group(3)}']
            else:
                marker, typ, mods, title = m.group(2), m.group(3).lower(), m.group(4) or '', m.group(5) if m.group(5) is not None else m.group(6)
                mapped = typ if typ in ALLOWED else TYPE_MAP.get(typ, 'note')
                if title is None and mapped != typ:
                    title = typ.replace('-', ' ').capitalize()
                if marker.startswith('???'):
                    head = [f'{ind}{sl} details' + (f' | {title}' if title else ' | ' + typ.capitalize()),
                            f'{ind}    type: {mapped}']
                    if marker.endswith('+'): head.append(f'{ind}    open: True')
                elif title == '':
                    head = [f'{ind}{sl} {mapped}']  # explicit empty title: keep a plain block
                else:
                    head = [f'{ind}{sl} {mapped}' + (f' | {title}' if title else '')]
            out += head + [''] + [(ind + x) if x.strip() else '' for x in inner] + ['', f'{ind}{sl}']
            depth = max(depth, d + 1)
            i = j
            continue
        out.append(l); i += 1
    return out, depth


def clean_fences(text):
    def fix(m):
        ind, f, rest = m.group(1), m.group(2), m.group(3).strip()
        if not rest:
            return m.group(0)
        mm = re.match(r'^([\w+#.-]*)\s*(\{.*\})?\s*(.*)$', rest)
        lang, attrs, tail = mm.group(1), mm.group(2) or '', mm.group(3)
        if lang in ('py', 'py3'): lang = 'python'
        keep = re.findall(r'(?:hl_lines|title|linenums)="[^"]*"', attrs + ' ' + tail)
        if attrs.startswith('{') and re.search(r'\.\w', attrs) and not lang:
            cls = re.findall(r'\.([\w-]+)', attrs)
            lang = cls[0] if cls else ''
        return f'{ind}{f}{lang}' + (' ' + ' '.join(keep) if keep else '')
    lines = text.split('\n'); out = []; i = 0
    while i < len(lines):
        if FENCE.match(lines[i]):
            e = _fence_end(lines, i)
            out.append(FENCE.sub(fix, lines[i])); out += lines[i + 1:e + 1]; i = e + 1
        else:
            out.append(lines[i]); i += 1
    return '\n'.join(out)


ICON = re.compile(r':(?:material|simple|octicons|fontawesome|fontawesome-[a-z]+|logfire)-[a-z0-9-]+:(?:\{[^}]*\})?\s?')


def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def heading_text(h):
    h = re.sub(r'\s*\{[^}]*#[^}]*\}\s*$', '', h)
    h = re.sub(r'!\[([^\]]*)\]\([^)]*\)', '', h)
    h = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', h)
    h = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', h)
    h = re.sub(r'<[^>]+>', '', h)
    h = h.replace('`', '')
    h = re.sub(r'(\*\*|__|\*)(.+?)\1', r'\2', h)
    return h.strip()


def add_anchors(text):
    lines = text.split('\n'); out = []; seen = {}; i = 0
    while i < len(lines):
        l = lines[i]
        if FENCE.match(l):
            e = _fence_end(lines, i); out += lines[i:e + 1]; i = e + 1; continue
        m = re.match(r'^(#{1,6})\s+(.*?)\s*$', l)
        if m:
            h = m.group(2)
            ex = re.search(r'\{\s*#([\w.:-]+)\s*\}\s*$', h) or re.search(r'\{[^}]*#([\w.:-]+)[^}]*\}\s*$', h)
            if ex:
                slug = ex.group(1); h = h[:ex.start()].rstrip()
            else:
                base = slugify(heading_text(h)) or 'section'
                slug = base; n = 0
                while slug in seen:
                    n += 1; slug = f'{base}_{n}'
            seen[slug] = 1
            out.append(f'{m.group(1)} {h} {{ #{slug} }}')
        else:
            out.append(l)
        i += 1
    return '\n'.join(out)


def mk_options(text, defaults):
    """merge default mkdocstrings options into each ::: block"""
    lines = text.split('\n'); out = []; i = 0
    while i < len(lines):
        l = lines[i]
        m = re.match(r'^(\s*):::\s+(\S+)\s*$', l)
        if not m:
            out.append(l); i += 1; continue
        ind = m.group(1); j = i + 1; opts = {}
        if j < len(lines) and re.match(r'^' + ind + r'    options:\s*$', lines[j]):
            k = j + 1
            while k < len(lines) and (not lines[k].strip() or _indent(lines[k]) > len(ind) + 4):
                k += 1
            while k > j + 1 and not lines[k - 1].strip(): k -= 1
            raw = lines[j + 1:k]
            base = min((_indent(x) for x in raw if x.strip()), default=0)  # upstream indents options by 6 or 8
            body = '\n'.join(x[base:] if x.strip() else '' for x in raw)
            opts = yaml.safe_load(body) or {}
            j = k
        for a, b in defaults.items():
            opts.setdefault(a, b)
        out.append(l)
        out.append(ind + '    options:')
        dumped = yaml.safe_dump(opts, sort_keys=False, default_flow_style=False, width=1000).rstrip('\n')
        out += [ind + '        ' + x for x in dumped.split('\n')]
        i = j
    return '\n'.join(out)


def raw_jinja(text):
    """wrap fenced blocks / lines containing jinja-like syntax so the site's macros plugin leaves them alone"""
    lines = text.split('\n'); out = []; i = 0
    while i < len(lines):
        l = lines[i]
        if FENCE.match(l):
            e = _fence_end(lines, i); blk = lines[i:e + 1]
            if any(re.search(r'\{\{|\{%|\{#', x) for x in blk):
                ind = FENCE.match(l).group(1)
                out += [ind + '{% raw %}'] + blk + [ind + '{% endraw %}']
            else:
                out += blk
            i = e + 1; continue
        if re.search(r'\{\{|\{%|\{#(?! )', l) and '{ #' not in l:
            out.append('{% raw %}' + l + '{% endraw %}')
        else:
            out.append(l)
        i += 1
    return '\n'.join(out)


def mdx_components(text):
    """pydantic.dev (MDX) components -> plain markdown / blocks"""
    def cta(m):
        a = m.group(1)
        href = re.search(r'href="([^"]+)"', a); label = re.search(r'label="([^"]+)"', a)
        return f'[{label.group(1) if label else "Contact"}]({href.group(1) if href else "https://pydantic.dev/contact"}){{ .md-button .md-button--primary }}'
    text = re.sub(r'<EnterpriseSupportCta\b(.*?)/>', cta, text, flags=re.S)
    text = re.sub(r'^[ \t]*<EnterpriseSupport(?:Plan|Areas)\b[^>]*/>[ \t]*\n?', '', text, flags=re.M)
    text = re.sub(r'^[ \t]*</?Steps>[ \t]*\n?', '', text, flags=re.M)
    def col(m):
        ind, title, body = m.group(1), m.group(2), m.group(3).strip('\n')
        return f'{ind}/// details | {title}\n{ind}    type: note\n\n{body}\n\n{ind}///'
    text = re.sub(r'^([ \t]*)<Collapsible title="(.*?)">[ \t]*\n(.*?)^\1</Collapsible>', col, text, flags=re.M | re.S)
    return text


def version_blocks(text):
    """pydantic's custom version-* blocks -> standard admonitions with a descriptive title"""
    names = {'version-added': ('info', 'Added in'), 'version-changed': ('info', 'Changed in'),
             'deprecated-removed': ('warning', 'Deprecated/removed in'), 'deprecated': ('warning', 'Deprecated in')}
    def fix(m):
        ind, sl, kind, ver = m.group(1), m.group(2), m.group(3), (m.group(4) or '').strip()
        typ, label = names[kind]
        return f'{ind}{sl} {typ} | {label} {ver}'.rstrip()
    return re.sub(r'^([ \t]*)(/{3,}) (version-added|version-changed|deprecated-removed|deprecated)(?: *\| *(.*))?[ \t]*$', fix, text, flags=re.M)


def material_to_site(text, mk_defaults=None):
    text = text.replace('\t', '    ')
    text = mdx_components(text)
    text = version_blocks(text)
    text = clean_fences(text)
    text = '\n'.join(convert(text.split('\n'))[0])
    text = ICON.sub('', text)
    text = add_anchors(text)
    if mk_defaults is not None:
        text = mk_options(text, mk_defaults)
    text = raw_jinja(text)
    return text.rstrip('\n') + '\n'
