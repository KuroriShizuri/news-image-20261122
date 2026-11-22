#!/usr/bin/env python3
"""Generate a 1024x1024 newspaper front page (entry.png) with PIL.

Everything is drawn from scratch with Pillow shapes and text: a masthead,
a hero illustration of missiles over a night skyline, and six illustrated
grid stories. Deterministic: no randomness, no time, no network.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
PAPER = (247, 241, 227)
INK = (17, 17, 17)
RED = (164, 31, 31)
RED_BRIGHT = (198, 52, 32)
MUTED = (90, 83, 72)
RULE = (120, 110, 95)
SKY_TOP = (26, 42, 68)
SKY_BOTTOM = (13, 21, 38)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def text_h(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[3] - box[1]


def centred(draw, cx, y, text, fnt, fill=INK):
    w = text_w(draw, text, fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + text_h(draw, text, fnt)


def fit_font(draw, text, path, start, max_w, minimum=10):
    size = start
    while size > minimum and text_w(draw, text, font(path, size)) > max_w:
        size -= 1
    return font(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, current = [], ""
    for word in text.split(" "):
        trial = (current + " " + word).strip()
        if text_w(draw, trial, fnt) <= max_w or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def centred_block(draw, cx, y, lines, fnt, fill=INK, leading=4):
    for line in lines:
        y = centred(draw, cx, y, line, fnt, fill)
        y += leading
    return y


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def diamond(draw, cx, cy, r, fill=RED):
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def ornament_rule(draw, y, x0, x1):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=1)
    draw.line([(x0, y + 3), (x1, y + 3)], fill=RED, width=1)
    mid = (x0 + x1) / 2
    diamond(draw, mid, y + 1, 5)
    diamond(draw, mid - 26, y + 1, 3)
    diamond(draw, mid + 26, y + 1, 3)


# ---------------------------------------------------------------- hero art
def draw_stars(draw, box):
    x0, y0, x1, y1 = box
    spots = [(70, 200), (150, 225), (260, 195), (330, 215), (430, 198),
             (520, 222), (610, 196), (700, 218), (800, 200), (900, 220),
             (950, 195), (110, 245), (470, 240), (760, 244), (880, 248)]
    for sx, sy in spots:
        if x0 <= sx <= x1 and y0 <= sy <= y1:
            draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(240, 230, 190))


def draw_skyline(draw, box):
    x0, y0, x1, y1 = box
    base = y1
    back = [(0, 70), (55, 95), (110, 60), (165, 88), (220, 72), (275, 100),
            (330, 66), (385, 92), (440, 74), (495, 98), (550, 68), (605, 90),
            (660, 76), (715, 96), (770, 70), (825, 92), (880, 74), (930, 90)]
    for i, (dx, bh) in enumerate(back):
        draw.rectangle([x0 + dx, base - bh, min(x0 + dx + 52, x1), base],
                       fill=(35, 44, 61))
    front = [(20, 46), (90, 62), (160, 40), (235, 58), (310, 44), (380, 66),
             (455, 50), (530, 60), (600, 42), (675, 64), (750, 48),
             (820, 58), (885, 46)]
    for i, (dx, bh) in enumerate(front):
        draw.rectangle([x0 + dx, base - bh, min(x0 + dx + 64, x1), base],
                       fill=(12, 18, 32))
        for wy in range(base - bh + 8, base - 6, 14):
            for wx in range(x0 + dx + 8, min(x0 + dx + 56, x1 - 8), 16):
                if (wx * 7 + wy * 13) % 5 < 2:
                    draw.rectangle([wx, wy, wx + 4, wy + 6],
                                   fill=(250, 205, 110))


def draw_explosion(draw, cx, cy, r):
    for k in range(8):
        ang = k * math.pi / 4
        x2 = cx + r * math.cos(ang)
        y2 = cy + r * math.sin(ang)
        draw.line([(cx, cy), (x2, y2)], fill=(255, 170, 60), width=3)
    draw.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2],
                 fill=(255, 190, 80))
    draw.ellipse([cx - r // 4, cy - r // 4, cx + r // 4, cy + r // 4],
                 fill=(255, 240, 180))


def draw_hero(draw, box):
    x0, y0, x1, y1 = box
    steps = 24
    for i in range(steps):
        t = i / (steps - 1)
        y_a = y0 + (y1 - y0) * i / steps
        y_b = y0 + (y1 - y0) * (i + 1) / steps
        draw.rectangle([x0, y_a, x1, y_b], fill=lerp(SKY_TOP, SKY_BOTTOM, t))
    draw_stars(draw, box)
    draw_skyline(draw, box)
    # missile trails: bright red-orange streaks rising to the right
    trails = [(120, 340, 300, 250), (250, 345, 430, 245), (400, 342, 580, 250),
              (540, 345, 720, 248), (680, 342, 850, 252)]
    for (ax, ay, bx, by) in trails:
        draw.line([(ax, ay), (bx, by)], fill=(255, 110, 60), width=5)
        draw.line([(ax, ay + 4), (bx, by + 4)], fill=(255, 190, 120), width=2)
        draw.line([(ax - 40, ay + 12), (bx - 30, by + 10)],
                  fill=(220, 220, 220), width=2)
    # missiles: small grey darts at the end of each trail
    for (ax, ay, bx, by) in trails:
        mx, my = bx + 18, by - 8
        draw.polygon([(mx - 26, my + 6), (mx + 14, my - 6), (mx + 20, my - 2),
                      (mx - 20, my + 10)], fill=(200, 205, 212))
        draw.polygon([(mx - 6, my - 2), (mx + 2, my - 12), (mx + 8, my - 2)],
                     fill=(160, 165, 175))
    draw_explosion(draw, 210, 330, 26)
    draw_explosion(draw, 620, 336, 20)
    draw.rectangle(box, outline=(60, 55, 45), width=2)


# ------------------------------------------------------- grid illustrations
def art_markets(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(250, 246, 236))
    base = y1 - 14
    draw.line([(x0 + 14, base), (x1 - 14, base)], fill=INK, width=2)
    draw.line([(x0 + 14, y0 + 10), (x0 + 14, base)], fill=INK, width=2)
    heights = [38, 58, 30, 66, 44]
    for i, hh in enumerate(heights):
        bx = x0 + 30 + i * 46
        col = RED if i in (1, 3) else (120, 120, 118)
        draw.rectangle([bx, base - hh, bx + 26, base], fill=col)
    pts = [(x0 + 28, y0 + 26), (x0 + 90, y0 + 48), (x0 + 150, y0 + 34),
           (x0 + 210, y0 + 58), (x0 + 262, y0 + 82)]
    draw.line(pts, fill=RED, width=4)
    ex, ey = pts[-1]
    draw.polygon([(ex - 4, ey - 14), (ex + 16, ey + 2), (ex - 12, ey + 10)],
                 fill=RED)


def art_jet(draw, box):
    x0, y0, x1, y1 = box
    for i in range(12):
        t = i / 11
        ya = y0 + (y1 - y0) * i / 12
        yb = y0 + (y1 - y0) * (i + 1) / 12
        draw.rectangle([x0, ya, x1, yb],
                       fill=lerp((214, 130, 90), (232, 196, 150), t))
    draw.ellipse([x0 + 118, y0 + 8, x0 + 150, y0 + 40], fill=(255, 220, 150))
    ground = y1 - 26
    draw.rectangle([x0, ground, x1, y1], fill=(196, 164, 120))
    draw.arc([x0 + 22, ground - 22, x0 + 82, ground + 22], 180, 360,
             fill=(90, 70, 55), width=3)
    draw.arc([x0 + 200, ground - 22, x0 + 260, ground + 22], 180, 360,
             fill=(90, 70, 55), width=3)
    cx, cy = x0 + 150, y0 + 42
    draw.polygon([(cx - 62, cy + 6), (cx + 58, cy - 2), (cx + 78, cy + 4),
                  (cx + 40, cy + 10), (cx - 30, cy + 14)], fill=(52, 58, 66))
    draw.polygon([(cx - 6, cy - 2), (cx + 14, cy - 22), (cx + 22, cy - 2)],
                 fill=(52, 58, 66))
    draw.polygon([(cx - 20, cy + 10), (cx - 2, cy + 26), (cx + 8, cy + 10)],
                 fill=(52, 58, 66))
    draw_explosion(draw, x0 + 228, ground - 8, 14)


def art_building(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(238, 232, 218))
    bx, by = x0 + 88, y0 + 12
    draw.rectangle([bx, by, bx + 110, y1 - 8], fill=(168, 160, 146))
    for r in range(4):
        for c in range(3):
            wx = bx + 14 + c * 32
            wy = by + 12 + r * 22
            lit = (r * 3 + c) % 4 == 0
            draw.rectangle([wx, wy, wx + 16, wy + 12],
                           fill=(250, 205, 110) if lit else (52, 46, 40))
    draw.polygon([(bx + 110, by), (bx + 150, by + 18), (bx + 138, by + 44),
                  (bx + 152, by + 70), (bx + 110, y1 - 8)],
                 fill=(88, 78, 66))
    for sx, sy, sr in [(x0 + 232, y0 + 26, 22), (x0 + 252, y0 + 12, 16),
                       (x0 + 214, y0 + 10, 12)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(120, 110, 100))
    draw.polygon([(x0 + 216, y0 + 52), (x0 + 232, y0 + 30), (x0 + 244, y0 + 54),
                  (x0 + 256, y0 + 36), (x0 + 262, y0 + 58)],
                 fill=(230, 110, 40))
    draw.rectangle([x0 + 30, y1 - 14, x1 - 30, y1 - 8], fill=(120, 110, 96))


def art_quake(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(250, 246, 236))
    mid = y0 + 26
    pts = [(x0 + 10, mid)]
    for i in range(1, 25):
        px = x0 + 10 + i * (x1 - x0 - 20) / 24
        amp = 16 if i in (9, 10, 11, 15, 16) else (6 if i % 3 == 0 else 2)
        pts.append((px, mid + amp * (1 if i % 2 else -1)))
    draw.line(pts, fill=RED, width=2)
    ey = y0 + 52
    draw.rectangle([x0 + 10, ey, x1 - 10, y1 - 10], fill=(216, 186, 140))
    cracks = [[(x0 + 60, ey), (x0 + 80, ey + 14), (x0 + 70, ey + 26),
               (x0 + 92, ey + 40)],
              [(x0 + 150, ey), (x0 + 140, ey + 18), (x0 + 160, ey + 30),
               (x0 + 148, ey + 44)],
              [(x0 + 230, ey), (x0 + 216, ey + 16), (x0 + 232, ey + 28)],
              [(x0 + 80, ey + 26), (x0 + 56, ey + 34)],
              [(x0 + 140, ey + 18), (x0 + 116, ey + 28)]]
    for crack in cracks:
        draw.line(crack, fill=(74, 58, 40), width=3)


def art_court(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(250, 246, 236))
    cx = (x0 + x1) / 2
    base = y1 - 12
    draw.rectangle([cx - 42, base - 6, cx + 42, base], fill=(120, 84, 44))
    draw.rectangle([cx - 3, y0 + 30, cx + 3, base - 6], fill=(120, 84, 44))
    draw.line([(cx - 78, y0 + 34), (cx + 78, y0 + 34)], fill=(120, 84, 44),
              width=4)
    draw.ellipse([cx - 7, y0 + 24, cx + 7, y0 + 38], fill=(150, 110, 60))
    for side in (-1, 1):
        px = cx + side * 72
        draw.line([(cx + side * 72, y0 + 34), (px, y0 + 58)],
                  fill=(90, 80, 70), width=2)
        draw.line([(cx + side * 72, y0 + 34), (px - 20, y0 + 58)],
                  fill=(90, 80, 70), width=2)
        draw.line([(cx + side * 72, y0 + 34), (px + 20, y0 + 58)],
                  fill=(90, 80, 70), width=2)
        draw.arc([px - 22, y0 + 52, px + 22, y0 + 74], 0, 180,
                 fill=(150, 110, 60), width=3)
        draw.line([(px - 22, y0 + 62), (px + 22, y0 + 62)],
                  fill=(150, 110, 60), width=3)
    # gavel resting in the bottom-right corner, clear of the pans
    gx, gy = x1 - 34, base - 14
    draw.line([(gx - 26, gy + 8), (gx + 12, gy - 12)], fill=(96, 64, 32),
              width=5)
    draw.rectangle([gx + 2, gy - 22, gx + 24, gy - 8], fill=(120, 84, 44))


def art_cyclone(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(226, 232, 236))
    for ex, ey, er in [(x0 + 60, y0 + 18, 30), (x0 + 110, y0 + 10, 36),
                       (x0 + 160, y0 + 20, 28)]:
        draw.ellipse([ex - er, ey - er // 2, ex + er, ey + er // 2],
                     fill=(70, 76, 88))
    cx, cy = x0 + 150, y0 + 44
    for r, col in [(34, RED), (26, RED_BRIGHT), (18, (230, 120, 70)),
                   (10, (250, 200, 120))]:
        draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 330, fill=col, width=4)
    sea = y0 + 66
    draw.rectangle([x0, sea, x1, y1], fill=(64, 110, 150))
    for k in range(3):
        wy = sea + 8 + k * 10
        pts = []
        for i in range(25):
            px = x0 + i * (x1 - x0) / 24
            pts.append((px, wy + 4 * math.sin(i * 0.9 + k)))
        draw.line(pts, fill=(220, 235, 245), width=2)
    for i, hx in enumerate([x0 + 218, x0 + 238, x0 + 258]):
        draw.rectangle([hx, y1 - 26, hx + 16, y1 - 10], fill=(240, 230, 210))
        draw.polygon([(hx - 2, y1 - 26), (hx + 8, y1 - 36), (hx + 18, y1 - 26)],
                     fill=RED)


ARTISTS = [art_markets, art_jet, art_building, art_quake, art_court,
           art_cyclone]

STORIES = [
    ("MARKETS", "WALL STREET IN CORRECTION",
     "S&P 500 down 3.7%, Nasdaq erases 2026 gains"),
    ("MIDDLE EAST", "IRAN STRIKES US BASE IN KUWAIT",
     "Gulf attacks widen; tankers hit off Oman"),
    ("UKRAINE", "MISSILE HITS KRYVYI RIH",
     "2 killed, 60 wounded in Zelenskyy's hometown"),
    ("LATIN AMERICA", "QUAKE SHAKES PERU",
     "Magnitude 6.9 tremor in the Andes"),
    ("WORLD COURT", "COURT: MYANMAR GENOCIDE",
     "World Court rules on the Rohingya"),
    ("WEATHER", "CYCLONE AKVAN HITS INDIA",
     "300,000 evacuated from Odisha coast"),
]


def draw_story(draw, cell, artist, kicker, headline, subhead):
    x0, y0, x1, y1 = cell
    draw.rectangle(cell, outline=(90, 82, 70), width=1)
    art_box = (x0 + 10, y0 + 10, x1 - 10, y0 + 106)
    artist(draw, art_box)
    draw.rectangle(art_box, outline=(150, 140, 125), width=1)
    cx = (x0 + x1) / 2
    kick_f = font(SANS_BOLD, 13)
    centred(draw, cx, y0 + 114, kicker, kick_f, fill=RED)
    head_f = fit_font(draw, headline, SERIF_BOLD, 25, x1 - x0 - 24)
    lines = wrap(draw, headline, head_f, x1 - x0 - 24)
    y = y0 + 134
    y = centred_block(draw, cx, y, lines, head_f, leading=1)
    rule_y = y + 8
    draw.line([(cx - 22, rule_y), (cx + 22, rule_y)], fill=RED, width=2)
    sub_f = font(SERIF, 17)
    sub_lines = wrap(draw, subhead, sub_f, x1 - x0 - 24)
    centred_block(draw, cx, rule_y + 10, sub_lines, sub_f, fill=MUTED,
                  leading=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    # thin double frame around the page
    draw.rectangle([14, 14, W - 15, H - 15], outline=RULE, width=1)
    draw.rectangle([18, 18, W - 19, H - 19], outline=(170, 160, 145), width=1)

    # masthead
    title_f = fit_font(draw, "THE WORLD TODAY", SERIF_BOLD, 92, W - 2 * MARGIN)
    centred(draw, W / 2, 30, "THE WORLD TODAY", title_f)
    date_f = font(SERIF, 24)
    dw = text_w(draw, "Sunday 22 November 2026", date_f)
    cx = W / 2
    draw.line([(MARGIN, 158), (cx - dw / 2 - 18, 158)], fill=INK, width=1)
    draw.line([(cx + dw / 2 + 18, 158), (W - MARGIN, 158)], fill=INK, width=1)
    centred(draw, cx, 146, "Sunday 22 November 2026", date_f)
    ornament_rule(draw, 176, MARGIN, W - MARGIN)

    # hero illustration + headline
    draw_hero(draw, (MARGIN, 186, W - MARGIN, 372))
    hero_f = fit_font(draw, "RUSSIAN MISSILES LAND IN POLAND", SERIF_BOLD,
                      52, W - 2 * MARGIN)
    centred(draw, W / 2, 388, "RUSSIAN MISSILES LAND IN POLAND", hero_f)
    sub_f = font(SERIF, 24)
    centred(draw, W / 2, 448,
            "NATO calls it a grave violation; Poland says deliberate provocation",
            sub_f)
    ornament_rule(draw, 496, MARGIN, W - MARGIN)

    # six-story grid, 2 rows x 3 columns
    cell_w, cell_h, gap = 306, 228, 17
    top = 514
    for idx, (kicker, headline, subhead) in enumerate(STORIES):
        row, col = divmod(idx, 3)
        x0 = MARGIN + col * (cell_w + gap)
        y0 = top + row * (cell_h + gap)
        draw_story(draw, (x0, y0, x0 + cell_w, y0 + cell_h),
                   ARTISTS[idx], kicker, headline, subhead)

    # footer line
    foot_f = font(SANS, 12)
    centred(draw, W / 2, 990, "THE WORLD TODAY  •  SUNDAY 22 NOVEMBER 2026",
            foot_f, fill=MUTED)
    img.save("entry.png", "JPEG", quality=92)


if __name__ == "__main__":
    main()
