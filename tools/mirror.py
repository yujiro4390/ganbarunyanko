"""ganbarunyanko.com（goope）を静的サイトとして丸ごと取り込む。

  python3 tools/mirror.py         # docs/ に出力（GitHub Pages の公開元）

- ganbarunyanko.com 内のHTMLページを辿る（admin・外部サイトは辿らない）
- 画像・CSS・JS は ganbarunyanko.com と cdn.goope.jp（＋そのサブドメイン）から取得して docs/_assets/ に保存
- ページ内・CSS内のURLを相対パスに書き換える（/diary → diary/index.html、?page=2 → diary/page-2/index.html）
"""
import hashlib, html, re, sys, time, urllib.parse, urllib.request
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs'
SITE = 'ganbarunyanko.com'
START = f'https://{SITE}/'
ASSET_HOSTS = re.compile(r'(^|\.)goope\.jp$|^' + re.escape(SITE) + '$')
SKIP = re.compile(r'admin\.goope\.jp|^https?://goope\.jp|/feed\.rss')
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15'}
MAX_PAGES = 800

URL_ATTR = re.compile(r'''(?P<pre>\b(?:href|src|data-src|data-original|poster|content)\s*=\s*)(?P<q>["'])(?P<u>[^"']+)(?P=q)''', re.I)
SRCSET = re.compile(r'''(\bsrcset\s*=\s*)(["'])([^"']+)\2''', re.I)
CSS_URL = re.compile(r'''url\(\s*(['"]?)([^'")]+)\1\s*\)''', re.I)
CSS_IMPORT = re.compile(r'''(@import\s+)(['"])([^'"]+)\2''', re.I)   # @import "/style.css"（url()なし）


def fetch(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read(), r.headers.get('Content-Type', '')
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(1 + i)
    print('  失敗', url, err, file=sys.stderr)
    return None, ''


def norm(u, base, attr=''):
    u = html.unescape(u.strip())
    if not u or u.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:')):
        return None
    if attr.lower().startswith('content') and not u.startswith(('http://', 'https://', '/')):
        return None   # meta content= の説明文などはURLではない
    a = urllib.parse.urljoin(base, u)
    p = urllib.parse.urlsplit(a)
    if p.scheme not in ('http', 'https'):
        return None
    path = urllib.parse.quote(urllib.parse.unquote(p.path or '/'), safe='/%:@!$&\'()*+,;=-._~')
    query = urllib.parse.quote(urllib.parse.unquote(p.query), safe='=&%+-._~')
    return urllib.parse.urlunsplit(('https', p.netloc.lower(), path, query, ''))


def is_page(u):
    p = urllib.parse.urlsplit(u)
    if p.netloc != SITE or SKIP.search(u):
        return False
    ext = Path(p.path).suffix.lower()
    return ext in ('', '.html', '.htm')


def is_asset(u):
    p = urllib.parse.urlsplit(u)
    return bool(ASSET_HOSTS.search(p.netloc)) and not is_page(u) and not SKIP.search(u)


def page_path(u):
    p = urllib.parse.urlsplit(u)
    parts = [x for x in p.path.split('/') if x]
    if p.query:
        q = re.sub(r'[^A-Za-z0-9]+', '-', p.query).strip('-')
        parts.append(q)
    return Path(*parts, 'index.html') if parts else Path('index.html')


def asset_path(u):
    p = urllib.parse.urlsplit(u)
    path = p.path.lstrip('/') or 'index'
    if p.query:
        h = hashlib.md5(p.query.encode()).hexdigest()[:8]
        stem, ext = (path.rsplit('.', 1) + [''])[:2] if '.' in Path(path).name else (path, '')
        path = f'{stem}_{h}' + (f'.{ext}' if ext else '')
    return Path('_assets', p.netloc, path)


def rel(target, from_file):
    return Path(urllib.parse.quote(str(Path(*(['..'] * (len(from_file.parts) - 1)), target)) if len(from_file.parts) > 1 else str(target)))


def main():
    pages, assets = {}, {}
    q, seen = deque([START]), {START}
    while q and len(pages) < MAX_PAGES:
        u = q.popleft()
        body, ct = fetch(u)
        time.sleep(0.3)
        if body is None or 'html' not in ct:
            continue
        text = body.decode('utf-8', 'replace')
        pages[u] = text
        print(f'[{len(pages)}] {u}')
        for m in URL_ATTR.finditer(text):
            n = norm(m.group('u'), u, m.group('pre'))
            if n and is_page(n) and n not in seen:
                seen.add(n); q.append(n)
    # 素材を集める（HTML内 → CSS内）
    def collect(text, base):
        found = []
        for m in URL_ATTR.finditer(text):
            if m.group('pre').lower().startswith('content') and not m.group('u').startswith(('http', '/')):
                continue
            found.append(m.group('u'))
        for m in SRCSET.finditer(text):
            found += [c.strip().split(' ')[0] for c in m.group(3).split(',')]
        for m in CSS_URL.finditer(text):
            found.append(m.group(2))
        for m in CSS_IMPORT.finditer(text):
            found.append(m.group(3))
        return [n for n in (norm(x, base) for x in found) if n and is_asset(n)]
    todo = deque()
    for u, t in pages.items():
        todo.extend(collect(t, u))
    while todo:
        a = todo.popleft()
        if a in assets:
            continue
        body, ct = fetch(a)
        assets[a] = (body, ct)
        if body is not None and ('css' in ct or a.split('?')[0].endswith('.css')):
            todo.extend(collect(body.decode('utf-8', 'replace'), a))
    print(f'ページ {len(pages)} / 素材 {len(assets)}')

    def rewrite(text, base, here):
        def sub_u(raw):
            n = norm(raw, base)
            if not n:
                return raw
            if n in pages or (is_page(n) and n.split('?')[0] in pages):
                tgt = page_path(n if n in pages else n.split('?')[0])
            elif n in assets and assets[n][0] is not None:
                tgt = asset_path(n)
            else:
                return raw
            frag = ''
            if '#' in raw:
                frag = '#' + raw.split('#', 1)[1]
            return str(rel(tgt, here)) + frag
        text = URL_ATTR.sub(lambda m: m.group('pre') + m.group('q') + sub_u(m.group('u')) + m.group('q'), text)
        text = SRCSET.sub(lambda m: m.group(1) + m.group(2) + ', '.join(
            ' '.join([sub_u(c.strip().split(' ')[0])] + c.strip().split(' ')[1:]) for c in m.group(3).split(',')) + m.group(2), text)
        text = CSS_URL.sub(lambda m: f'url({m.group(1)}{sub_u(m.group(2))}{m.group(1)})', text)
        text = CSS_IMPORT.sub(lambda m: m.group(1) + m.group(2) + sub_u(m.group(3)) + m.group(2), text)
        return text

    for u, t in pages.items():
        here = page_path(u)
        f = OUT / here
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(rewrite(t, u, here), encoding='utf-8')
    for a, (body, ct) in assets.items():
        if body is None:
            continue
        here = asset_path(a)
        f = OUT / here
        f.parent.mkdir(parents=True, exist_ok=True)
        if 'css' in ct or a.split('?')[0].endswith('.css'):
            f.write_text(rewrite(body.decode('utf-8', 'replace'), a, here), encoding='utf-8')
        else:
            f.write_bytes(body)
    (OUT / '.nojekyll').write_text('')
    print('完了', OUT)


if __name__ == '__main__':
    main()
