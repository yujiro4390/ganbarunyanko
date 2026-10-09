"""mirror.py の出力（docs/）を GitHub Pages 用に整える。mirror.py の後に毎回実行する。

- お問い合わせ（フォームは静的サイトでは送れない）を外す：メニュー項目・ヘッダーのボタン・ページ本体
- 中身のない電話ボタン（tel:）を外す
- goope の管理画面リンク・壊れたRSSリンク・goope側のGoogleアナリティクスを外す
- グーペのテンプレート画像を自作画像（tools/theme_images/、make_theme_images.py で生成）で上書き
"""
import re, shutil
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / 'docs'

PATTERNS = [
    # メニュー・フッターの「お問い合わせ」項目
    (re.compile(r'<li[^>]*>\s*<a href="[./]*contact/index\.html"[^>]*>.*?</a>\s*</li>', re.S), ''),
    # PCヘッダーのお問い合わせ・電話ボタン
    (re.compile(r'<a href="[./]*contact/index\.html" class="mail_area[^"]*">.*?</a>', re.S), ''),
    (re.compile(r'<div class="shop_tel tel_area[^"]*">.*?</div>', re.S), ''),
    # スマホヘッダーのお問い合わせ・電話ボタン
    (re.compile(r'<a href="[./]*contact/index\.html" class="mail_area_mobile[^"]*">.*?</a>', re.S), ''),
    (re.compile(r'<a href="tel:" class="shop_tel[^"]*">.*?</a>', re.S), ''),
    # その他の本文中のお問い合わせリンクは文字だけ残す
    (re.compile(r'<a href="[./]*contact/index\.html"[^>]*>(.*?)</a>', re.S), r'\1'),
    # goope 管理画面・RSS（静的版には無い）
    (re.compile(r'<div class="powered">.*?</div>', re.S), ''),
    (re.compile(r'<link[^>]*href="/feed\.rss"[^>]*/?>', re.S), ''),
    # goope の短縮URL（写真館へ転送）→ 静的版の写真館
    (re.compile(r'((?:\.\./)*)_assets/r\.goope\.jp/ganbarunyanko/photo'), r'\1photo/index.html'),
    # goope 側の Google アナリティクス
    (re.compile(r'<!-- Global site tag \(gtag\.js\).*?</script>\s*<script>.*?</script>', re.S), ''),
]


def main():
    n = 0
    for f in DOCS.rglob('*.html'):
        s = f.read_text(encoding='utf-8')
        t = s
        for pat, rep in PATTERNS:
            t = pat.sub(rep, t)
        if t != s:
            f.write_text(t, encoding='utf-8'); n += 1
    shutil.rmtree(DOCS / 'contact', ignore_errors=True)
    shutil.rmtree(DOCS / '_assets' / 'r.goope.jp' / 'ganbarunyanko', ignore_errors=True)
    src = Path(__file__).resolve().parent / 'theme_images'
    m = 0
    for f in src.rglob('*.*'):
        dst = DOCS / '_assets' / 'ganbarunyanko.com' / 'img' / f.relative_to(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, dst); m += 1
    print(f'{n} ページを整えた / テンプレート画像 {m} 点を差し替えた')


if __name__ == '__main__':
    main()
