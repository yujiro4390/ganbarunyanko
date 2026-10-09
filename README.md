# アンバランスでも頑張るにゃんこ（ねこつき公式サイト）静的版

https://ganbarunyanko.com/ （グーペ）を静的サイトに変換し、GitHub Pages で公開しているもの。
公開URL：https://yujiro4390.github.io/ganbarunyanko/ （公開元は docs/）

## 更新のしかた
グーペ側で更新したあと、取り込み直す：

    python3 tools/mirror.py        # docs/ を作り直す（ページ・画像・CSSを取得し、リンクを相対パスに）
    python3 tools/postprocess.py   # お問い合わせ等を外し、テンプレート画像を自作画像で上書き

## 静的版で変えたところ
- お問い合わせページは外した（フォームは静的サイトでは送信できないため）
- 中身のない電話ボタン、グーペ管理画面リンク、壊れたRSSリンクを外した
- グーペのテンプレート画像（theme_hometown の鳥・旗・雲・綿毛・街並み・見出し文字、UI部品、ブログ/Xアイコン）は
  自作画像に差し替えた。鳥は公式キャラクター（tools/characters/）に。作り直しは `python3 tools/make_theme_images.py`
  （同じファイル名・同じサイズで生成し、postprocess.py が docs/ へ上書きする）
- 未対応：レイアウトのCSS（style.css「Goope Style / Town」）と一部のJSはグーペ（GMOペパボ）のテーマのコードのまま
