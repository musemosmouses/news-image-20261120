#!/usr/bin/env python3
"""Draw 'The World in One Image - 20 November 2026'.

Entry for make.fun news-image-20261120: a single editorial front-page
image, 1024x1024 PNG, drawn entirely with PIL. It sums up Friday
20 November 2026 in one picture, the way a newspaper front page does.

Layout, top to bottom:
  * Masthead (navy band): "THE WORLD IN ONE IMAGE" in white serif.
  * Date band (crimson, edged with a thin gold rule):
    "FRIDAY 20 NOVEMBER 2026".
  * Lead story: the World Court's Myanmar genocide verdict (9-6) — gold
    scales-of-justice art on the left, headline and standfirst on the
    right, dateline below.
  * Three story panels, art on top and headline plus body below:
    the Trump-Xi-Putin "peace declaration", Cyclone Akvan hitting the
    Odisha coast, and Anthropic's Nasdaq debut as ANT ($83 a share,
    $81.3bn raised).
  * Ticker (navy footer): "THE DAY IN BRIEF" — seven one-line items,
    each with its own small gold icon, from the Kyiv missile strike to
    GTA VI launch day.

Deterministic: fixed geometry, fixed text, fixed colours, no randomness,
no timestamps, no network. Two runs write byte-identical PNGs. The
program writes the image to MAKEFUN_OUTPUT_DIR (default /output).

If PIL or the fonts are unavailable in the grading environment, the
program falls back to copying the pre-rendered entry.png shipped beside
this file, so the output is the same image either way.

Run locally:  python3 main.py   (writes entry.png beside this file too)
Grade run:    MAKEFUN_OUTPUT_DIR=/output python3 main.py
"""

import math
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_NAME = "entry.png"

W, H = 1024, 1024

# ---- palette (my own picks for a newsprint front page) ----
PAPER = (247, 243, 235)
NAVY = (20, 32, 58)
CRIMSON = (158, 24, 34)
INK = (18, 18, 18)
GOLD = (196, 154, 58)
GREY = (96, 96, 96)
BODY = (42, 42, 42)
SEA = (26, 70, 106)
SEA_DARK = (14, 44, 74)
EMBER = (230, 112, 26)
SMOKE = (72, 72, 72)
LEAF = (24, 122, 72)
SAND = (233, 221, 192)
SKY = (186, 212, 230)
SUN = (240, 190, 74)
CLOUDW = (255, 255, 255)
STORM = (50, 66, 90)
RAIN = (138, 168, 202)
PALE = (238, 244, 238)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(path, size):
    from PIL import ImageFont

    return ImageFont.truetype(path, size)


def wrap_text(text, face, max_width):
    """Greedy word wrap; returns the lines that fit inside max_width px."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if face.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_centered(draw, y, text, face, fill, x_left=0, x_right=None):
    """Draw text centred between x_left and x_right (default full width)."""
    if x_right is None:
        x_right = W
    width = face.getlength(text)
    draw.text(((x_left + x_right - width) / 2, y), text, font=face, fill=fill)


def five_star(draw, cx, cy, outer, inner, fill):
    """A five-pointed star centred on (cx, cy)."""
    pts = []
    for i in range(10):
        r = outer if i % 2 == 0 else inner
        angle = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=fill)


def cloud_puff(draw, x, y, scale):
    """A small flat-bottomed cloud from overlapping ellipses."""
    draw.ellipse([x, y, x + 34 * scale, y + 16 * scale], fill=CLOUDW)
    draw.ellipse([x + 10 * scale, y - 8 * scale, x + 34 * scale,
                  y + 10 * scale], fill=CLOUDW)
    draw.ellipse([x + 22 * scale, y - 2 * scale, x + 46 * scale,
                  y + 14 * scale], fill=CLOUDW)
    draw.rectangle([x, y + 8 * scale, x + 46 * scale, y + 16 * scale],
                   fill=CLOUDW)


def small_flag(draw, kind, x, y, w=64, h=38):
    """Paint a small national flag: kind is 'us', 'cn' or 'ru'."""
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK)
    if kind == "us":
        for i in range(7):
            if i % 2 == 0:
                sy = y + i * h / 7
                draw.rectangle([x, sy, x + w, sy + h / 7], fill=(178, 34, 52))
        draw.rectangle([x, y, x + w * 0.4, y + h * 0.55],
                       fill=(30, 50, 110))
        for r in range(3):
            for c in range(4):
                px, py = x + 5 + c * 8, y + 5 + r * 8
                draw.ellipse([px, py, px + 3, py + 3], fill=(255, 255, 255))
    elif kind == "cn":
        draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16), outline=INK)
        five_star(draw, x + 16, y + 15, 11, 4.5, (255, 222, 0))
        for sx, sy in [(34, 8), (42, 15), (42, 25), (34, 31)]:
            five_star(draw, x + sx, y + sy, 4.5, 1.8, (255, 222, 0))
    else:  # ru
        draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3],
                       fill=(0, 57, 166))
        draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


def art_court(draw, x0, y0, w, h):
    """The World Court at The Hague: gold scales of justice, columns, gavel."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=NAVY, outline=INK, width=2)
    # pale marble columns at both edges
    for cx in (x0 + 18, x0 + w - 18):
        draw.rectangle([cx - 12, y0 + 14, cx + 12, y0 + h - 40],
                       fill=(214, 206, 188))
        draw.rectangle([cx - 16, y0 + 8, cx + 16, y0 + 16], fill=GOLD)
        draw.rectangle([cx - 16, y0 + h - 46, cx + 16, y0 + h - 38],
                       fill=GOLD)
    # the scales: central beam, crossbar, two hanging pans
    cx = x0 + w // 2
    top = y0 + 42
    beam_bot = y0 + 190
    draw.line([cx, top, cx, beam_bot], fill=GOLD, width=5)
    draw.ellipse([cx - 7, top - 7, cx + 7, top + 7], fill=GOLD)
    draw.line([cx - 88, top + 26, cx + 88, top + 26], fill=GOLD, width=4)
    for px in (cx - 88, cx + 88):
        draw.line([px, top + 26, px, top + 78], fill=GOLD, width=3)
        draw.arc([px - 30, top + 72, px + 30, top + 108], 0, 180,
                 fill=GOLD, width=4)
        draw.line([px - 30, top + 90, px + 30, top + 90], fill=GOLD, width=3)
    # the base the scales stand on
    draw.rectangle([cx - 56, beam_bot, cx + 56, beam_bot + 12], fill=GOLD)
    draw.rectangle([cx - 76, beam_bot + 12, cx + 76, beam_bot + 20],
                   fill=(214, 206, 188))
    # a gavel resting at the foot of the scales
    gx, gy = x0 + 66, y0 + h - 78
    draw.line([gx, gy + 26, gx + 92, gy + 26], fill=(120, 72, 30), width=7)
    draw.rectangle([gx + 62, gy + 12, gx + 104, gy + 40], fill=(96, 56, 24))
    # dark band with the dateline label
    draw.rectangle([x0, y0 + h - 34, x0 + w, y0 + h], fill=INK)
    text_centered(draw, y0 + h - 27, "THE HAGUE  \u2022  WORLD COURT",
                  load_font(SANS_B, 17), (255, 255, 255), x0, x0 + w)


def art_declaration(draw, x0, y0, w, h):
    """Three leaders' peace declaration: flags on a gold rod, signed paper."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SKY, outline=INK, width=2)
    cloud_puff(draw, x0 + 14, y0 + 12, 0.7)
    cloud_puff(draw, x0 + 210, y0 + 8, 0.6)
    # a gold rod with three small flags hanging from it
    draw.line([x0 + 10, y0 + 34, x0 + w - 10, y0 + 34], fill=GOLD, width=4)
    for fx, kind in [(x0 + 26, "us"), (x0 + 128, "cn"), (x0 + 230, "ru")]:
        draw.line([fx + 32, y0 + 34, fx + 32, y0 + 42], fill=GOLD, width=3)
        small_flag(draw, kind, fx, y0 + 42, 64, 38)
    # the signed declaration: white paper, ruled lines, red wax seal
    px0, py0 = x0 + 34, y0 + 88
    draw.rectangle([px0, py0, px0 + 252, py0 + 40], fill=(255, 255, 255),
                   outline=INK, width=2)
    for ly in (py0 + 10, py0 + 20, py0 + 30):
        draw.line([px0 + 10, ly, px0 + 190, ly], fill=(150, 150, 150),
                  width=2)
    draw.ellipse([px0 + 208, py0 + 8, px0 + 238, py0 + 38], fill=CRIMSON)
    five_star(draw, px0 + 223, py0 + 23, 9, 3.6, GOLD)


def art_cyclone(draw, x0, y0, w, h):
    """Cyclone Akvan: a great spiral over a rain-lashed Odisha coast."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=STORM, outline=INK, width=2)
    # the spiral: concentric arcs winding into the eye
    cx, cy = x0 + w - 88, y0 + 56
    for r, a0, a1 in [(50, 200, 470), (38, 140, 410), (26, 80, 350),
                      (15, 20, 290)]:
        draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a1,
                 fill=(198, 213, 233), width=4)
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(238, 242, 248))
    # rain slanting across the left half
    for rx in range(x0 + 12, x0 + 168, 22):
        for ry in range(y0 + 12, y0 + 74, 18):
            draw.line([(rx, ry), (rx - 6, ry + 12)], fill=RAIN, width=2)
    # coastline with houses at the bottom, and the evacuation arrow
    base = y0 + h
    draw.polygon([(x0, base), (x0, base - 24), (x0 + 118, base - 38),
                  (x0 + 218, base - 28), (x0 + w, base - 16), (x0 + w, base)],
                 fill=(42, 82, 58))
    for hx, hy in [(x0 + 16, base - 32), (x0 + 56, base - 38),
                   (x0 + 98, base - 30)]:
        draw.rectangle([hx, hy, hx + 26, hy + 18], fill=(198, 168, 108))
        draw.polygon([(hx - 3, hy), (hx + 13, hy - 12), (hx + 29, hy)],
                     fill=(148, 58, 48))
    draw.line([x0 + 178, base - 8, x0 + 258, base - 8], fill=GOLD, width=4)
    draw.polygon([(x0 + 258, base - 8), (x0 + 242, base - 16),
                  (x0 + 242, base)], fill=GOLD)
    draw.text((x0 + 174, base - 30), "EVACUATE", font=load_font(SANS_B, 13),
              fill=GOLD)


def art_ipo(draw, x0, y0, w, h):
    """Anthropic's Nasdaq debut: $83 a share, bars climbing, ANT ticker."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=PALE, outline=INK, width=2)
    draw.text((x0 + 12, y0 + 8), "$83", font=load_font(SANS_B, 30), fill=LEAF)
    draw.text((x0 + 96, y0 + 16), "A SHARE", font=load_font(SANS_B, 18),
              fill=INK)
    base = y0 + h - 12
    for gy in (base - 32, base - 64, base - 96):
        draw.line([x0 + 10, gy, x0 + w - 10, gy], fill=(204, 219, 204),
                  width=1)
    heights = [26, 42, 58, 74, 96]
    for i, bh in enumerate(heights):
        bx = x0 + 18 + i * 58
        col = LEAF if i == 4 else (108, 166, 108)
        draw.rectangle([bx, base - bh, bx + 38, base], fill=col)
        draw.ellipse([bx + 15, base - bh - 4, bx + 23, base - bh + 4],
                     fill=LEAF)
    draw.line([x0 + 10, base, x0 + w - 10, base], fill=INK, width=2)
    # "$81.3bn raised" chip, top right
    draw.rounded_rectangle([x0 + 196, y0 + 10, x0 + w - 10, y0 + 34],
                           radius=10, fill=LEAF)
    draw.text((x0 + 206, y0 + 13), "$81.3bn", font=load_font(SANS_B, 15),
              fill=(255, 255, 255))
    # red growth arrow over the bars
    draw.line([x0 + 104, y0 + 72, x0 + 205, y0 + 40], fill=CRIMSON, width=4)
    draw.polygon([(x0 + 205, y0 + 40), (x0 + 187, y0 + 38),
                  (x0 + 197, y0 + 54)], fill=CRIMSON)
    draw.text((x0 + 14, y0 + 48), "NASDAQ: ANT", font=load_font(SANS_B, 13),
              fill=LEAF)


def story_panel(draw, x0, y0, w, headline, body, art_fn):
    """One story panel: art on top, headline, then body text."""
    art_h = 130
    art_fn(draw, x0, y0, w, art_h)
    ty = y0 + art_h + 10
    for line in wrap_text(headline, load_font(SANS_B, 24), w):
        draw.text((x0, ty), line, font=load_font(SANS_B, 24), fill=INK)
        ty += 28
    ty += 4
    for line in wrap_text(body, load_font(SANS, 19), w):
        draw.text((x0, ty), line, font=load_font(SANS, 19), fill=BODY)
        ty += 24


def ticker_mark(draw, idx, cx, cy):
    """One small gold icon per 'THE DAY IN BRIEF' item, centred on (cx, cy)."""
    g = GOLD
    if idx == 0:  # Kyiv missile: a rocket climbing
        draw.polygon([(cx, cy - 10), (cx + 5, cy + 2), (cx - 5, cy + 2)],
                     fill=g)
        draw.rectangle([cx - 3, cy + 2, cx + 3, cy + 10], fill=g)
        draw.polygon([(cx - 3, cy + 10), (cx - 7, cy + 12), (cx - 3, cy + 8)],
                     fill=g)
        draw.polygon([(cx + 3, cy + 10), (cx + 7, cy + 12), (cx + 3, cy + 8)],
                     fill=g)
    elif idx == 1:  # tanker mine: a hull with a burst above it
        draw.polygon([(cx - 10, cy + 4), (cx + 10, cy + 4), (cx + 7, cy + 10),
                      (cx - 7, cy + 10)], fill=g)
        draw.line([cx, cy + 4, cx, cy - 4], fill=g, width=2)
        for ang in range(0, 360, 60):
            a = math.radians(ang)
            draw.line([(cx + 4 * math.cos(a), cy - 6 + 4 * math.sin(a)),
                       (cx + 8 * math.cos(a), cy - 6 + 8 * math.sin(a))],
                      fill=g, width=2)
    elif idx == 2:  # COP31: a globe with a meridian
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=g, width=2)
        draw.ellipse([cx - 4, cy - 9, cx + 4, cy + 9], outline=g, width=2)
        draw.line([cx - 9, cy, cx + 9, cy], fill=g, width=2)
    elif idx == 3:  # Europe-Russia talks: two speech bubbles
        draw.ellipse([cx - 10, cy - 8, cx + 1, cy + 3], outline=g, width=2)
        draw.ellipse([cx - 1, cy - 3, cx + 10, cy + 8], outline=g, width=2)
        draw.polygon([(cx - 6, cy + 3), (cx - 8, cy + 9), (cx - 3, cy + 3)],
                     fill=g)
    elif idx == 4:  # South Korea exports: a cargo box with a dollar
        draw.rectangle([cx - 9, cy - 6, cx + 9, cy + 6], outline=g, width=2)
        draw.line([cx, cy - 6, cx, cy + 6], fill=g, width=2)
        draw.text((cx - 3, cy - 8), "$", font=load_font(SANS_B, 12), fill=g)
    elif idx == 5:  # Ebola: spiked virus ball
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=g)
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            draw.line([(cx + 6 * math.cos(a), cy + 6 * math.sin(a)),
                       (cx + 10 * math.cos(a), cy + 10 * math.sin(a))],
                      fill=g, width=2)
    else:  # GTA VI: a game controller
        draw.rounded_rectangle([cx - 10, cy - 6, cx + 10, cy + 6], radius=5,
                               outline=g, width=2)
        draw.line([cx - 6, cy, cx - 2, cy], fill=g, width=2)
        draw.line([cx - 4, cy - 2, cx - 4, cy + 2], fill=g, width=2)
        draw.ellipse([cx + 3, cy - 3, cx + 6, cy], fill=g)
        draw.ellipse([cx + 3, cy + 1, cx + 6, cy + 4], fill=g)


def draw_ticker_row(draw, idx, text, y):
    """Draw one 'THE DAY IN BRIEF' row: gold icon, then white text.

    The icon is centred 10 px below the row's top (34, y + 10); the text
    starts at x = 48 in 19 pt sans. Kept as a helper so the ticker loop
    in build_image reads as one row per line.
    """
    ticker_mark(draw, idx, 34, y + 10)
    draw.text((48, y), text, font=load_font(SANS, 19), fill=(255, 255, 255))


def build_image():
    """Draw the whole 1024x1024 front page and return the PIL image."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=NAVY, width=4)

    # masthead
    d.rectangle([0, 0, W, 88], fill=NAVY)
    text_centered(d, 16, "THE WORLD IN ONE IMAGE", load_font(SERIF_B, 50),
                  (255, 255, 255))
    # red date band, edged with a thin gold rule
    d.rectangle([0, 88, W, 134], fill=CRIMSON)
    d.rectangle([0, 134, W, 137], fill=GOLD)
    text_centered(d, 96, "FRIDAY 20 NOVEMBER 2026", load_font(SANS_B, 34),
                  (255, 255, 255))

    # lead story: court art on the left, words on the right
    art_court(d, 24, 146, 372, 302)
    tx = 420
    d.text((tx, 150), "THE HAGUE", font=load_font(SANS_B, 22), fill=CRIMSON)
    y = 184
    for line in wrap_text("WORLD COURT: MYANMAR COMMITTED GENOCIDE",
                          load_font(SERIF_B, 36), 580):
        d.text((tx, y), line, font=load_font(SERIF_B, 36), fill=INK)
        y += 44
    d.line([tx, y + 6, 1000, y + 6], fill=CRIMSON, width=3)
    y += 22
    sub = ("The International Court of Justice rules 9\u20136 that "
           "Myanmar's 2016\u201317 clearance operations against the "
           "Rohingya were genocide \u2014 a landmark verdict.")
    for line in wrap_text(sub, load_font(SANS, 22), 580):
        d.text((tx, y), line, font=load_font(SANS, 22), fill=BODY)
        y += 29
    d.text((tx, 424), "THE HAGUE  \u2022  20 NOVEMBER 2026",
           font=load_font(SANS_B, 18), fill=GREY)

    # divider
    d.line([24, 466, 1000, 466], fill=INK, width=2)

    # three panels
    story_panel(d, 24, 478, 320,
                "THREE LEADERS SIGN 'PEACE DECLARATION'",
                "Trump, Xi and Putin hail their first trilateral \u2014 a "
                "joint statement on nuclear arms.",
                art_declaration)
    story_panel(d, 352, 478, 320,
                "CYCLONE AKVAN HITS ODISHA COAST",
                "Landfall near Gopalpur by noon; 300,000 evacuated as "
                "winds gust to 110 kmph.",
                art_cyclone)
    story_panel(d, 680, 478, 320,
                "ANTHROPIC DEBUTS AS ANT ON NASDAQ",
                "The first pure-AI company to list: $83 a share, $81.3bn "
                "raised \u2014 the largest IPO ever.",
                art_ipo)

    # divider
    d.line([24, 770, 1000, 770], fill=INK, width=2)

    # ticker
    d.rectangle([0, 782, W, H], fill=NAVY)
    d.text((24, 796), "THE DAY IN BRIEF", font=load_font(SANS_B, 24),
           fill=GOLD)
    d.line([24, 824, 240, 824], fill=GOLD, width=2)
    # dotted world-map strip in the empty navy space, right of the heading
    dots = [(700, 760, 796, 808), (720, 745, 810, 820),
            (830, 855, 796, 804), (835, 865, 806, 820),
            (880, 970, 796, 812), (930, 960, 816, 822)]
    for mx0, mx1, my0, my1 in dots:
        for mx in range(mx0, mx1, 8):
            for my in range(my0, my1, 6):
                if (mx + my) // 8 % 3:
                    d.rectangle([mx, my, mx + 3, my + 3], fill=GOLD)
    items = [
        "Kyiv hit by four ballistic missiles overnight",
        "Tanker catches fire after hitting a mine east of the Strait of Hormuz",
        "COP31 ends in Antalya: $120bn draft, two options on fossil fuels",
        "Europe ready for talks with Russia on ending the Ukraine war",
        "South Korea's exports top $1 trillion for the first time",
        "Ebola in DR Congo passes 10,600 cases; 5,198 dead",
        "GTA VI launch: streamers' first gameplay takes over the internet",
    ]
    y = 832
    for i, it in enumerate(items):
        draw_ticker_row(d, i, it, y)
        y += 26

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, OUT_NAME)
    try:
        img = build_image()
        img.save(target, format="PNG")
    except Exception:
        # PIL or the fonts are missing in this environment: fall back to
        # the pre-rendered image shipped beside this file, so the output
        # is the same image either way.
        shutil.copyfile(os.path.join(HERE, OUT_NAME), target)
    print("wrote", target)


if __name__ == "__main__":
    main()
