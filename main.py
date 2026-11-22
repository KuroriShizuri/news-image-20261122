#!/usr/bin/env python3
"""THE WORLD TODAY -- Sunday 22 November 2026.

A 1024x1024 JPEG newspaper front page, drawn entirely with Pillow.
Stdlib + PIL only. Deterministic: no randomness, no timestamps, no
network access. Run with ``python3 main.py``; writes entry.png next
to this script.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

# ---- palette ---------------------------------------------------------
PAPER = (247, 241, 222)      # cream newsprint
PANEL = (250, 246, 232)      # slightly lighter cream for story cells
INK = (26, 24, 20)           # near-black
RED = (178, 34, 34)          # accent red
RED_DARK = (139, 26, 26)
GREY = (96, 92, 82)          # subhead grey-brown
NIGHT = (26, 35, 64)         # hero night sky
NIGHT_DEEP = (16, 22, 44)
SKYLINE = (38, 48, 84)
WINDOW = (255, 214, 130)
ORANGE = (255, 122, 26)
GOLD = (255, 176, 32)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

_font_cache = {}


def font(path, size):
    """Cached TrueType font loader with a Pillow-default fallback."""
    key = (path, size)
    if key not in _font_cache:
        try:
            _font_cache[key] = ImageFont.truetype(path, size)
        except (OSError, IOError):
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def text_w(draw, text, fnt):
    """Pixel width of *text* in font *fnt*."""
    left, _top, right, _bottom = draw.textbbox((0, 0), text, font=fnt)
    return right - left


def text_h(draw, text, fnt):
    """Pixel height of *text* in font *fnt*."""
    _left, top, _right, bottom = draw.textbbox((0, 0), text, font=fnt)
    return bottom - top


def fit_font(draw, text, path, size, max_w):
    """Largest font size <= *size* that fits *text* inside *max_w*."""
    s = size
    while s > 8 and text_w(draw, text, font(path, s)) > max_w:
        s -= 1
    return font(path, s)


def centre(draw, cx, y, text, fnt, fill=INK):
    """Draw *text* centred on x=cx at height y.

    Returns the distance from y to the bottom of the glyphs (the
    textbbox bottom, not the bbox height): PIL draws glyphs offset
    below y by the bbox top, so advancing by the height alone would
    overlap the next line.
    """
    w = text_w(draw, text, fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    _left, _top, _right, bottom = draw.textbbox((0, 0), text, font=fnt)
    return bottom


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit *max_w*."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centre_block(draw, cx, y, lines, fnt, fill=INK, leading=4):
    """Draw centred lines stacked from y; returns the bottom y."""
    for line in lines:
        h = centre(draw, cx, y, line, fnt, fill)
        y += h + leading
    return y


def diamond(draw, cx, cy, r, fill=RED):
    """Small filled diamond ornament centred at (cx, cy)."""
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)],
                 fill=fill)


def red_rule(draw, x0, x1, y):
    """Double red rule with three diamonds, as used under the date line."""
    draw.line([(x0, y), (x1, y)], fill=RED, width=2)
    draw.line([(x0, y + 5), (x1, y + 5)], fill=RED, width=1)
    mid = (x0 + x1) // 2
    diamond(draw, mid, y + 2, 6)
    diamond(draw, mid - 22, y + 2, 4)
    diamond(draw, mid + 22, y + 2, 4)


def burst(draw, cx, cy, r, fill=GOLD, spikes=12):
    """Jagged explosion burst: alternating long/short radial spikes."""
    pts = []
    for i in range(spikes * 2):
        ang = math.pi * i / spikes - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)
    draw.ellipse([cx - r * 0.34, cy - r * 0.34, cx + r * 0.34, cy + r * 0.34],
                 fill=(255, 240, 180))
    draw.ellipse([cx - r * 0.16, cy - r * 0.16, cx + r * 0.16, cy + r * 0.16],
                 fill=(255, 255, 255))


# ---- hero illustration ----------------------------------------------
def draw_hero(draw, x0, y0, x1, y1):
    """Night skyline with five diagonal missiles and two explosions."""
    draw.rectangle([x0, y0, x1, y1], fill=NIGHT)
    # faint stars, fixed positions for determinism
    stars = [(70, 12), (150, 30), (260, 10), (340, 26), (430, 8),
             (520, 28), (610, 12), (700, 30), (790, 10), (880, 26),
             (110, 44), (470, 48), (660, 46), (840, 44), (210, 52)]
    for sx, sy in stars:
        draw.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2],
                     fill=(220, 225, 255))
    # distant skyline, then nearer skyline with lit windows
    base = y1
    far = [(0, 62, 90, 128), (100, 48, 170, 128), (180, 70, 250, 128),
           (260, 44, 340, 128), (350, 66, 430, 128), (440, 50, 520, 128),
           (530, 68, 610, 128), (620, 46, 700, 128), (710, 64, 790, 128),
           (800, 50, 880, 128)]
    for bx, by, ex, _ey in far:
        draw.rectangle([x0 + bx, y0 + by, x0 + ex, base], fill=NIGHT_DEEP)
    near = [(20, 88, 110), (130, 74, 205), (220, 92, 300), (315, 76, 400),
            (415, 90, 500), (515, 72, 600), (615, 88, 700), (715, 74, 795),
            (810, 90, 890)]
    for bx, by, ex in near:
        draw.rectangle([x0 + bx, y0 + by, x0 + ex, base], fill=SKYLINE)
        # lit windows in a fixed staggered pattern
        wx = bx + 10
        while wx < ex - 8:
            wy = by + 10
            while wy < 122:
                if ((wx // 14) + (wy // 16)) % 3 != 0:
                    draw.rectangle([x0 + wx, y0 + wy, x0 + wx + 5,
                                    y0 + wy + 7], fill=WINDOW)
                wy += 16
            wx += 16
    # five missiles flying up-right on orange trails
    for i in range(5):
        tx = x0 + 60 + i * 170
        ty = y0 + 108 - (i % 2) * 8
        hx = tx + 150
        hy = ty - 62
        draw.line([(tx, ty), (hx, hy)], fill=ORANGE, width=7)
        draw.line([(tx, ty), (hx, hy)], fill=(255, 200, 120), width=2)
        # missile body: small grey dart at the head of the trail
        draw.polygon([(hx, hy), (hx - 26, hy + 4), (hx - 20, hy + 12),
                      (hx + 4, hy + 10)], fill=(200, 205, 215))
        draw.polygon([(hx - 8, hy + 2), (hx - 20, hy - 8), (hx - 14, hy + 4)],
                     fill=(160, 165, 180))
    # two explosion bursts low over the skyline
    burst(draw, x0 + 190, y0 + 100, 20)
    burst(draw, x0 + 590, y0 + 102, 18)


def draw_masthead(draw):
    """Masthead, date line, hero art, hero headline and subhead."""
    cx = W // 2
    y = 26
    h = centre(draw, cx, y, "THE WORLD TODAY",
               font(SERIF_BOLD, 82), INK)
    y += h + 10
    # thin black rules flanking the date line, kept clear of the text
    date_fnt = font(SERIF, 27)
    date_w = text_w(draw, "Sunday 22 November 2026", date_fnt)
    mid_y = y + 22
    draw.line([(36, mid_y), (cx - date_w // 2 - 20, mid_y)], fill=INK,
              width=1)
    draw.line([(cx + date_w // 2 + 20, mid_y), (988, mid_y)], fill=INK,
              width=1)
    centre(draw, cx, y, "Sunday 22 November 2026", date_fnt, INK)
    y += 40
    red_rule(draw, 36, 988, y)
    y += 14
    hero_y0 = y
    hero_y1 = y + 168
    draw_hero(draw, 36, hero_y0, 988, hero_y1)
    draw.rectangle([36, hero_y0, 988, hero_y1], outline=INK, width=2)
    y = hero_y1 + 16
    # hero headline, shrunk to fit one line if needed
    fnt = fit_font(draw, "RUSSIAN MISSILES LAND IN POLAND",
                   SERIF_BOLD, 45, 952)
    h = centre(draw, cx, y, "RUSSIAN MISSILES LAND IN POLAND", fnt, INK)
    y += h + 8
    centre(draw, cx, y,
           "NATO calls it a grave violation; Poland says deliberate provocation",
           font(SERIF_ITALIC, 25), INK)
    y += 30
    red_rule(draw, 36, 988, y)
    return y + 16


# ---- grid-story illustrations ---------------------------------------
def draw_markets(draw, x0, y0, x1, y1):
    """Falling bar chart with a red downward trend arrow."""
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))
    draw.rectangle([x0, y0, x1, y1], outline=GREY, width=1)
    base = y1 - 12
    bars = [(18, 46, (150, 150, 150)), (58, 78, RED), (98, 40, (150, 150, 150)),
            (138, 62, RED), (178, 80, RED), (218, 52, (150, 150, 150))]
    for bx, bh, col in bars:
        draw.rectangle([x0 + bx, base - bh, x0 + bx + 28, base], fill=col)
    draw.line([(x0 + 8, base), (x1 - 8, base)], fill=INK, width=2)
    # red trend line falling left to right, ending in an arrowhead
    pts = [(x0 + 12, y0 + 22), (x0 + 70, y0 + 34), (x0 + 130, y0 + 28),
           (x0 + 190, y0 + 44), (x0 + 250, y0 + 62)]
    draw.line(pts, fill=RED, width=4)
    ax, ay = x0 + 262, y0 + 66
    draw.polygon([(ax, ay), (ax - 18, ay - 10), (ax - 14, ay + 2),
                  (ax - 20, ay + 8)], fill=RED)


def draw_middle_east(draw, x0, y0, x1, y1):
    """Desert sunset: sun, jet silhouette, dunes, small explosion."""
    # vertical sunset gradient in fixed bands
    bands = [(255, 196, 130), (250, 170, 110), (240, 140, 90),
             (228, 115, 75), (214, 96, 66)]
    bh = (y1 - y0) // len(bands) + 1
    for i, col in enumerate(bands):
        draw.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh], fill=col)
    draw.ellipse([x0 + 118, y0 + 14, x0 + 162, y0 + 58], fill=(255, 232, 170))
    # dunes
    draw.rectangle([x0, y1 - 26, x1, y1], fill=(196, 154, 96))
    draw.arc([x0 + 8, y1 - 52, x0 + 92, y1 + 2], 180, 360,
             fill=(120, 84, 52), width=3)
    draw.arc([x0 + 190, y1 - 48, x0 + 268, y1 + 4], 180, 360,
             fill=(120, 84, 52), width=3)
    # jet silhouette crossing the sun
    draw.polygon([(x0 + 96, y0 + 52), (x0 + 196, y0 + 46),
                  (x0 + 210, y0 + 52), (x0 + 150, y0 + 62),
                  (x0 + 128, y0 + 76), (x0 + 118, y0 + 60)],
                 fill=(40, 36, 44))
    draw.polygon([(x0 + 150, y0 + 48), (x0 + 168, y0 + 30),
                  (x0 + 176, y0 + 50)], fill=(40, 36, 44))
    burst(draw, x0 + 238, y0 + 74, 12, fill=ORANGE, spikes=10)


def draw_ukraine(draw, x0, y0, x1, y1):
    """Damaged apartment block: grey tower, lit windows, smoke, blast."""
    draw.rectangle([x0, y0, x1, y1], fill=(240, 236, 224))
    draw.rectangle([x0, y0, x1, y1], outline=GREY, width=1)
    # tower block
    draw.rectangle([x0 + 78, y0 + 10, x0 + 168, y1 - 14], fill=(120, 118, 112))
    for r in range(4):
        for c in range(3):
            wx = x0 + 90 + c * 28
            wy = y0 + 18 + r * 20
            col = WINDOW if (r + c) % 2 == 0 else (52, 50, 48)
            draw.rectangle([wx, wy, wx + 16, wy + 12], fill=col)
    # ground line and rubble
    draw.line([(x0 + 10, y1 - 14), (x1 - 10, y1 - 14)], fill=INK, width=3)
    draw.polygon([(x0 + 190, y1 - 14), (x0 + 214, y1 - 52),
                  (x0 + 238, y1 - 14)], fill=(90, 88, 84))
    # smoke cloud
    for sx, sy, sr in [(212, 28, 14), (232, 22, 18), (250, 32, 12)]:
        draw.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr,
                      y0 + sy + sr], fill=(105, 100, 95))
    # orange blast triangles at the tower base
    draw.polygon([(x0 + 176, y1 - 14), (x0 + 192, y1 - 52),
                  (x0 + 206, y1 - 14)], fill=ORANGE)
    draw.polygon([(x0 + 202, y1 - 14), (x0 + 214, y1 - 42),
                  (x0 + 226, y1 - 14)], fill=ORANGE)


def draw_latin_america(draw, x0, y0, x1, y1):
    """Seismograph trace above cracked dry ground."""
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))
    draw.rectangle([x0, y0, x1, y1], outline=GREY, width=1)
    mid = (y0 + y1) // 2
    # jagged red seismograph line, fixed amplitudes
    amps = [0, -4, 3, -8, 6, -14, 10, -20, 14, -10, 4, -16, 8, -4, 2,
            -6, 12, -18, 8, -4, 0, -3, 5, -7, 3, 0]
    pts = []
    for i, a in enumerate(amps):
        pts.append((x0 + 8 + i * 10, mid - 26 + a))
    draw.line(pts, fill=RED, width=2)
    # cracked earth band
    draw.rectangle([x0, mid + 8, x1, y1], fill=(214, 186, 138))
    draw.line([(x0, mid + 8), (x1, mid + 8)], fill=(120, 84, 52), width=2)
    cracks = [[(40, 0), (58, 14), (52, 28), (66, 34)],
              [(120, 0), (108, 16), (122, 30), (112, 36)],
              [(200, 0), (214, 12), (206, 26), (220, 32)]]
    for crack in cracks:
        pts = [(x0 + px, mid + 10 + py) for px, py in crack]
        draw.line(pts, fill=(74, 56, 36), width=3)


def draw_world_court(draw, x0, y0, x1, y1):
    """Scales of justice with a gavel."""
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))
    draw.rectangle([x0, y0, x1, y1], outline=GREY, width=1)
    cx = (x0 + x1) // 2
    top = y0 + 16
    bot = y1 - 14
    gold = (176, 138, 66)
    bronze = (120, 88, 44)
    # central pillar, crossbeam and base
    draw.line([(cx, top + 8), (cx, bot - 8)], fill=bronze, width=5)
    draw.line([(cx - 78, top + 12), (cx + 78, top + 12)], fill=bronze,
              width=4)
    draw.rectangle([cx - 34, bot - 8, cx + 34, bot], fill=bronze)
    draw.ellipse([cx - 7, top - 2, cx + 7, top + 12], fill=gold)
    # two hanging pans
    for side in (-1, 1):
        px = cx + side * 78
        draw.line([(px, top + 12), (px - 24, top + 52)], fill=bronze, width=2)
        draw.line([(px, top + 12), (px + 24, top + 52)], fill=bronze, width=2)
        draw.line([(px, top + 12), (px, top + 52)], fill=bronze, width=2)
        draw.arc([px - 26, top + 44, px + 26, top + 68], 0, 180,
                 fill=gold, width=3)
        draw.line([(px - 26, top + 56), (px + 26, top + 56)], fill=gold,
                  width=3)
    # gavel resting at lower right
    draw.line([(cx + 84, bot - 30), (cx + 116, bot - 14)], fill=bronze,
              width=4)
    draw.rectangle([cx + 108, bot - 30, cx + 128, bot - 16], fill=bronze)


def draw_weather(draw, x0, y0, x1, y1):
    """Cyclone spiral over a stormy sea, small houses on the shore."""
    draw.rectangle([x0, y0, x1, y1], fill=(214, 228, 240))
    # dark storm clouds
    for sx, sy, sr in [(70, 22, 26), (110, 16, 30), (150, 24, 24)]:
        draw.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr,
                      y0 + sy + sr], fill=(72, 80, 96))
    # cyclone: concentric red arcs
    ccx, ccy = x0 + 178, y0 + 48
    for i, r in enumerate([10, 18, 26, 34]):
        draw.arc([ccx - r, ccy - r, ccx + r, ccy + r], 200 - i * 30,
                 200 - i * 30 + 250, fill=RED, width=4)
    draw.ellipse([ccx - 5, ccy - 5, ccx + 5, ccy + 5], fill=ORANGE)
    # sea with wave lines
    draw.rectangle([x0, y0 + 66, x1, y1], fill=(52, 110, 164))
    for wy in (72, 82, 90):
        for wx in range(6, 260, 44):
            draw.arc([x0 + wx, y0 + wy, x0 + wx + 34, y0 + wy + 12],
                     180, 360, fill=(200, 225, 245), width=2)
    # three small houses with red roofs on the shore
    for hx in (196, 224, 252):
        draw.rectangle([x0 + hx, y1 - 24, x0 + hx + 18, y1 - 8],
                       fill=(250, 244, 228))
        draw.polygon([(x0 + hx - 2, y1 - 24), (x0 + hx + 9, y1 - 36),
                      (x0 + hx + 20, y1 - 24)], fill=RED)


STORIES = [
    ("MARKETS", "WALL STREET IN CORRECTION",
     "S&P 500 down 3.7%, Nasdaq erases 2026 gains", draw_markets),
    ("MIDDLE EAST", "IRAN STRIKES US BASE IN KUWAIT",
     "Gulf attacks widen; tankers hit off Oman", draw_middle_east),
    ("UKRAINE", "MISSILE HITS KRYVYI RIH",
     "2 killed, 60 wounded in Zelenskyy's hometown", draw_ukraine),
    ("LATIN AMERICA", "QUAKE SHAKES PERU",
     "Magnitude 6.9 tremor in the Andes", draw_latin_america),
    ("WORLD COURT", "COURT: MYANMAR GENOCIDE",
     "World Court rules on the Rohingya", draw_world_court),
    ("WEATHER", "CYCLONE AKVAN HITS INDIA",
     "300,000 evacuated from Odisha coast", draw_weather),
]


def draw_grid(draw, y_top):
    """Two rows of three story cells; returns the bottom y."""
    margin, gutter = 36, 16
    cell_w = (W - 2 * margin - 2 * gutter) // 3
    cell_h = 232
    row_gap = 12
    for idx, (kicker, headline, subhead, art) in enumerate(STORIES):
        row, col = divmod(idx, 3)
        x0 = margin + col * (cell_w + gutter)
        x1 = x0 + cell_w
        y0 = y_top + row * (cell_h + row_gap)
        y1 = y0 + cell_h
        draw.rectangle([x0, y0, x1, y1], fill=PANEL, outline=INK, width=1)
        # illustration panel
        ix0, iy0, ix1, iy1 = x0 + 10, y0 + 10, x1 - 10, y0 + 104
        art(draw, ix0, iy0, ix1, iy1)
        draw.rectangle([ix0, iy0, ix1, iy1], outline=INK, width=1)
        cy = (x0 + x1) // 2
        ty = iy1 + 8
        h = centre(draw, cy, ty, kicker, font(SANS_BOLD, 14), RED)
        ty += h + 4
        # headline, shrunk to fit one line inside the cell
        fnt = fit_font(draw, headline, SERIF_BOLD, 19, cell_w - 16)
        h = centre(draw, cy, ty, headline, fnt, INK)
        ty += h + 3
        # short red underline under the headline
        hw = text_w(draw, headline, fnt)
        draw.line([(cy - hw / 2 + 8, ty), (cy + hw / 2 - 8, ty)],
                  fill=RED, width=2)
        ty += 8
        lines = wrap(draw, subhead, font(SERIF, 16), cell_w - 24)
        centre_block(draw, cy, ty, lines, font(SERIF, 16), GREY, leading=2)
    return y_top + 2 * cell_h + row_gap


# ---- page assembly ----------------------------------------------------
def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    # outer double border framing the whole front page
    draw.rectangle([10, 10, W - 11, H - 11], outline=INK, width=1)
    draw.rectangle([16, 16, W - 17, H - 17], outline=INK, width=1)
    grid_bottom = draw_grid(draw, draw_masthead(draw))
    # footer line centred in the space left below the grid
    fy = grid_bottom + 12
    centre(draw, W // 2, fy, "THE WORLD TODAY  •  SUNDAY 22 NOVEMBER 2026",
           font(SERIF, 15), GREY)
    img.save(OUT, "JPEG", quality=92)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
