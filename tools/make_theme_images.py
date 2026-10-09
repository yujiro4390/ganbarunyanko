"""グーペのテンプレート（theme_hometown ほか）の画像を、自作の画像に置き換える。

  python3 tools/make_theme_images.py     # tools/theme_images/ に生成（postprocess.py が docs/ へ上書きコピー）

元と同じファイル名・同じ縦横サイズで作るので、CSS・HTMLは触らずに差し替わる。
- 鳥のイラスト → 公式キャラクター（tools/characters/ にある本人提供のにゃんこくんたち）
- 旗・雲・綿毛・街並み・見出し文字・UI部品 → PILで描き直し
"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
CH = HERE / 'characters'
OUT = HERE / 'theme_images'
INK = (60, 60, 60, 255)
BLUE = (100, 185, 245, 255)
MARU = '/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc'


def save(im, rel):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == '.gif':
        im.convert('RGBA').save(p)
    else:
        im.save(p, optimize=True)


def chara(name, box, flip=False):
    """キャラ画像を余白を切って box(w,h) に収める（にゃんこちゃんは反転禁止＝リボンが逆になる）"""
    im = Image.open(CH / name).convert('RGBA')
    im = im.crop(im.getbbox())
    if flip and 'nyankochan' not in name and 'hyojo2' not in name and 'hyojo4' not in name:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im.thumbnail(box, Image.LANCZOS)
    return im


def fit(name, size, flip=False, pad=4):
    c = Image.new('RGBA', size, (0, 0, 0, 0))
    im = chara(name, (size[0] - pad * 2, size[1] - pad * 2), flip)
    c.alpha_composite(im, ((size[0] - im.width) // 2, size[1] - im.height - pad))
    return c


def bird_1():   # 154x154：スライダー横と本文横のちょこんとした飾り → リスちゃん
    save(fit('risu.PNG', (154, 154)), 'theme_hometown/bird_1.png')


def bird_2():   # 247x194：ヘッダー右上の飾り → にゃんこちゃん（反転しない）
    save(fit('nyankochan.PNG', (247, 194)), 'theme_hometown/bird_2.png')


def singing_bird():   # 413x132：サイドの並んだ小鳥 → 4人並び
    c = Image.new('RGBA', (413, 132), (0, 0, 0, 0))
    names = ['nyankokun.PNG', 'nyankochan.PNG', 'kapibara.PNG', 'risu.PNG']
    w = 413 // 4
    for i, n in enumerate(names):
        im = chara(n, (w - 4, 126))
        c.alpha_composite(im, (i * w + (w - im.width) // 2, 132 - im.height - 2))
    save(c, 'theme_hometown/singing_bird.png')


def bubble(d, box, text, font):
    x0, y0, x1, y1 = box
    d.ellipse(box, fill=(255, 255, 255, 255), outline=INK, width=5)
    cx = (x0 + x1) / 2
    d.polygon([(cx - 14, y1 - 8), (cx + 10, y1 - 6), (cx - 4, y1 + 26)], fill=(255, 255, 255, 255))
    d.line([(cx - 14, y1 - 5), (cx - 4, y1 + 26), (cx + 10, y1 - 4)], fill=INK, width=5)
    d.text((cx, (y0 + y1) / 2), text, font=font, fill=INK, anchor='mm')


def pagetop():   # 205x346：ページ上部へ戻るボタン → にゃんこくん＋「Top」吹き出し
    c = Image.new('RGBA', (205, 346), (0, 0, 0, 0))
    im = chara('nyankokun.PNG', (200, 220))
    c.alpha_composite(im, ((205 - im.width) // 2, 346 - im.height - 2))
    d = ImageDraw.Draw(c)
    bubble(d, (40, 6, 190, 106), 'Top', ImageFont.truetype(MARU, 48))
    save(c, 'theme_hometown/pagetop.png')


def flag():   # 286x60：横に繰り返す旗 → 先が丸い旗＋ひも
    c = Image.new('RGBA', (286, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    cols = [(255, 160, 190), (120, 200, 250), (255, 215, 90), (140, 220, 170)]
    w = 286 / 4
    for i, col in enumerate(cols):
        x0 = i * w + 6
        x1 = (i + 1) * w - 6
        cx = (x0 + x1) / 2
        d.polygon([(x0, 4), (x1, 4), (cx + 9, 44), (cx - 9, 44)], fill=col + (255,))
        d.ellipse((cx - 11, 36, cx + 11, 56), fill=col + (255,))
        d.ellipse((cx - 4, 16, cx + 4, 24), fill=(255, 255, 255, 220))   # 白い水玉
    d.line([(0, 4), (286, 4)], fill=(255, 255, 255, 255), width=4)
    save(c, 'theme_hometown/flag.png')


def clouds():   # 2545x2800：背景に散らばる雲
    W, H = 2545, 2800
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    r = random.Random(7)
    for _ in range(14):
        cx, cy = r.uniform(100, W - 400), r.uniform(80, H - 200)
        s = r.uniform(0.6, 1.5)
        lay = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(lay)
        for _ in range(7):
            ox, oy = r.uniform(-130, 130) * s, r.uniform(-25, 15) * s
            rx, ry = r.uniform(70, 120) * s, r.uniform(45, 70) * s
            d.ellipse((cx + ox - rx, cy + oy - ry, cx + ox + rx, cy + oy + ry), fill=255)
        d.rounded_rectangle((cx - 170 * s, cy, cx + 170 * s, cy + 40 * s), radius=int(20 * s), fill=255)
        lay = lay.filter(ImageFilter.GaussianBlur(10 * s))
        white = Image.new('RGBA', (W, H), (255, 255, 255, 0))
        white.putalpha(lay.point(lambda v: int(v * 0.85)))
        c.alpha_composite(white)
    save(c, 'theme_hometown/cloud_02.png')


def fluff():   # 2412x3358：ふわふわ舞う綿毛 → 小さな星と肉球
    W, H = 2412, 3358
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    r = random.Random(11)
    for i in range(10):
        x, y = r.uniform(80, W - 80), r.uniform(80, H - 80)
        s = r.uniform(14, 24)
        if i % 2:
            pts = []
            for k in range(10):
                a = -math.pi / 2 + k * math.pi / 5
                rr = s if k % 2 == 0 else s * 0.45
                pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
            d.polygon(pts, fill=(255, 250, 200, 230))
        else:
            d.ellipse((x - s * 0.6, y - s * 0.2, x + s * 0.6, y + s * 0.8), fill=(255, 255, 255, 220))
            for k, (ox, oy) in enumerate([(-0.75, -0.55), (-0.25, -0.95), (0.25, -0.95), (0.75, -0.55)]):
                rr = s * 0.25
                d.ellipse((x + ox * s - rr, y + oy * s - rr, x + ox * s + rr, y + oy * s + rr), fill=(255, 255, 255, 220))
    save(c, 'theme_hometown/tanpopo.png')


def skyline():   # 1590x232：下部の街並みシルエット → ねこ耳屋根の家並み
    W, H = 1590, 232
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    r = random.Random(3)
    x = 0
    while x < W:
        w = r.randint(70, 140)
        h = r.randint(60, 150)
        top = H - h
        d.rectangle((x, top, x + w, H), fill=BLUE)
        if r.random() < 0.55:   # ねこ耳
            e = min(26, w // 4)
            d.polygon([(x + 6, top + 1), (x + 6 + e * 0.5, top - e), (x + 6 + e, top + 1)], fill=BLUE)
            d.polygon([(x + w - 6 - e, top + 1), (x + w - 6 - e * 0.5, top - e), (x + w - 6, top + 1)], fill=BLUE)
        for wy in range(top + 18, H - 20, 30):   # 窓
            for wx in range(x + 14, x + w - 20, 26):
                if r.random() < 0.6:
                    d.rectangle((wx, wy, wx + 10, wy + 12), fill=(255, 255, 255, 120))
        x += w + r.randint(0, 6)
    save(c, 'theme_hometown/town_blue.png')


def heading(text, size, rel, font_size, deco):
    c = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    f = ImageFont.truetype(MARU, font_size)
    tx = size[0] / 2 + (34 if deco else 0)
    d.text((tx, size[1] / 2), text, font=f, fill=(80, 80, 80, 255), anchor='mm')
    if deco:
        im = chara('hyojo1.PNG', (int(size[1] * 0.9), int(size[1] * 0.9)))
        tw = d.textlength(text, font=f)
        c.alpha_composite(im, (int(tx - tw / 2 - im.width - 8), (size[1] - im.height) // 2))
    save(c, rel)


def slides():   # 1000x500：スライド画像が0枚のときの予備（通常は表示されない）
    for name, top, bottom, ch in [('town.png', (170, 215, 250), (230, 245, 255), 'nyankokun.PNG'),
                                  ('green.png', (200, 235, 200), (245, 250, 235), 'nyankochan.PNG')]:
        c = Image.new('RGBA', (1000, 500))
        d = ImageDraw.Draw(c)
        for y in range(500):
            k = y / 499
            d.line([(0, y), (1000, y)], fill=tuple(int(top[i] * (1 - k) + bottom[i] * k) for i in range(3)) + (255,))
        im = chara(ch, (300, 300))
        c.alpha_composite(im, ((1000 - im.width) // 2, 500 - im.height - 30))
        save(c, f'theme_hometown/{name}')


def small_parts():
    save(Image.new('RGBA', (1, 1), (92, 180, 253, 255)), 'theme_hometown/dot_blue.png')   # フッターの地色（単色）
    # 本文の行ごとの罫線（40pxの行の下に、丸い点が並ぶ点線）
    c = Image.new('RGBA', (6, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((1, 37, 2, 38), fill=(161, 216, 255, 255))
    d.point([(0, 37), (0, 38), (3, 37), (3, 38)], fill=(161, 216, 255, 120))
    save(c, 'theme_hometown/dot_line_blue.png')
    # スライダー操作ボタン（125x50＝上段グレー・下段黒の5つ：前・次・閉じる・再生・一時停止）
    c = Image.new('RGBA', (125, 50), (255, 255, 255, 255))
    d = ImageDraw.Draw(c)
    for row, col in ((0, (150, 150, 150, 255)), (1, (30, 30, 30, 255))):
        cy = 12 + row * 25
        for i in range(5):
            cx = 12 + i * 25
            if i == 0: d.polygon([(cx + 6, cy - 7), (cx - 6, cy), (cx + 6, cy + 7)], fill=col)
            if i == 1: d.polygon([(cx - 6, cy - 7), (cx + 6, cy), (cx - 6, cy + 7)], fill=col)
            if i == 2:
                d.line([(cx - 6, cy - 6), (cx + 6, cy + 6)], fill=col, width=3)
                d.line([(cx - 6, cy + 6), (cx + 6, cy - 6)], fill=col, width=3)
            if i == 3: d.polygon([(cx - 4, cy - 7), (cx + 6, cy), (cx - 4, cy + 7)], fill=col)
            if i == 4:
                d.rectangle((cx - 5, cy - 6, cx - 2, cy + 6), fill=col)
                d.rectangle((cx + 2, cy - 6, cx + 5, cy + 6), fill=col)
    save(c, 'theme_simple2/controls.png')
    c = Image.new('RGBA', (32, 32), (0, 0, 0, 255))
    d = ImageDraw.Draw(c)
    for k in range(8):
        a = k * math.pi / 4
        v = 80 + k * 22
        d.ellipse((16 + 10 * math.cos(a) - 2.5, 16 + 10 * math.sin(a) - 2.5, 16 + 10 * math.cos(a) + 2.5,
                   16 + 10 * math.sin(a) + 2.5), fill=(v, v, v, 255))
    save(c, 'theme_simple2/loading.gif')
    for name, size in (('tt_top.gif', (400, 5)), ('tt_bottom.gif', (400, 5)), ('tt_left.gif', (5, 150))):
        save(Image.new('RGBA', size, (204, 204, 204, 255)), f'tooltip/{name}')


def icons():   # 100x100：ブログ・X（旧Twitter）へのリンクアイコン
    c = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.ellipse((0, 0, 99, 99), fill=(244, 150, 180, 255))
    d.polygon([(30, 70), (34, 56), (62, 28), (72, 38), (44, 66)], fill=(255, 255, 255, 255))   # えんぴつ
    d.polygon([(30, 70), (34, 56), (44, 66)], fill=(255, 225, 170, 255))
    save(c, 'custompage/icon/blog.png')
    c = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.ellipse((0, 0, 99, 99), fill=(20, 20, 20, 255))
    d.text((50, 52), 'X', font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 54), fill=(255, 255, 255, 255), anchor='mm')
    save(c, 'custompage/icon/twitter.png')


if __name__ == '__main__':
    bird_1(); bird_2(); singing_bird(); pagetop(); flag(); clouds(); fluff(); skyline()
    heading('Welcome', (592, 179), 'theme_hometown/welcome.png', 104, True)
    heading('information', (424, 132), 'theme_hometown/information.png', 70, False)
    slides(); small_parts(); icons()
    print('生成', sorted(str(p.relative_to(OUT)) for p in OUT.rglob('*.*')))
