# アンバランスでも頑張るにゃんこ（ねこつき公式サイト）静的版

https://ganbarunyanko.com/ （グーペ）を静的サイトに変換し、GitHub Pages で公開しているもの。
公開URL：https://yujiro4390.github.io/ganbarunyanko/ （公開元は docs/）

## 更新のしかた
グーペ側で更新したあと、取り込み直す：

    python3 tools/mirror.py        # docs/ を作り直す（ページ・画像・CSSを取得し、リンクを相対パスに）
    python3 tools/postprocess.py   # お問い合わせ・電話ボタン・グーペ管理リンク・グーペ側アナリティクスを外す

## 静的版で変えたところ
- お問い合わせページは外した（フォームは静的サイトでは送信できないため）
- 中身のない電話ボタン、グーペ管理画面リンク、壊れたRSSリンクを外した
