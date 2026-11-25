#!/usr/bin/env python3
"""THE TUESDAY WORLD v2 — renders the 24 Nov 2026 world-news broadsheet.

Draws a 1024x1024 PNG fresh from this program only (no images, no network,
no dates, no randomness). Run: python3 render.py [out.png]  (default entry.png)
Deterministic: two runs produce byte-identical output.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 243, 232)
INK = (20, 20, 20)
PAPER_LINE = (20, 20, 20)
RED = (178, 34, 34)
AMBER = (176, 124, 0)
AMBER_BG = (246, 224, 170)
MUTED = (90, 84, 72)

# One accent colour per region band (index 0..9).
ACCENTS = [
    (31, 93, 140),    # 1 Western Europe — deep blue
    (0, 110, 110),    # 2 Eastern Europe — teal
    (146, 44, 44),    # 3 Middle East — brick red
    (122, 60, 130),   # 4 East Asia — purple
    (24, 122, 62),    # 5 South & Southeast Asia — green
    (176, 110, 0),    # 6 Africa — ochre
    (40, 70, 160),    # 7 North America — royal blue
    (168, 60, 90),    # 8 Latin America — magenta
    (80, 80, 80),     # 9 Markets & Tech — slate
    (110, 60, 20),    # 10 Defence — brown
]

_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/liberation2",
    "/usr/share/fonts",
]


def _find_font(names):
    for d in _FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.isfile(p):
                return p
    return None


_SERIF_BOLD = _find_font(["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"])
_SERIF = _find_font(["DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"])
_SANS_BOLD = _find_font(["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"])
_SANS = _find_font(["DejaVuSans.ttf", "LiberationSans-Regular.ttf"])

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        if path:
            _cache[key] = ImageFont.truetype(path, size)
        else:
            _cache[key] = ImageFont.load_default()
    return _cache[key]


def serif_b(size):
    return font(_SERIF_BOLD, size)


def serif(size):
    return font(_SERIF, size)


def sans_b(size):
    return font(_SANS_BOLD, size)


def sans(size):
    return font(_SANS, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(draw, t, f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_center(draw, cx, y, s, f, fill=INK):
    draw.text((cx - text_w(draw, s, f) / 2, y), s, font=f, fill=fill)


def rr(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- stories
# (headline, claim?) — every headline is a verified 24 Nov 2026 story.
BANDS = [
    ("WESTERN EUROPE", [
        ("Sarkozy corruption case ordered to trial", False),
        ("NATO vows defence against space threat", True),
        ("Germany first to access Ukraine Delta system", False),
    ]),
    ("EASTERN EUROPE", [
        ("Ukraine hits Russian ships; Poland accuses Moscow", True),
        ("Zelensky urges Ukraine-Russia-US-EU talks soon", False),
        ("Zaporizhzhia attack kills 2, wounds 40", False),
        ("Latvia: Ukraine war may hit tipping point", True),
    ]),
    ("MIDDLE EAST", [
        ("Houthis 60 km from Aden, ready to attack", True),
        ("Saudi PIF tower hit in suspected drone attack", True),
        ("Saudi strikes in Yemen: 25 dead or missing", False),
        ("Israel kills Hamas security chief in Gaza", True),
    ]),
    ("EAST ASIA", [
        ("Japan to pay full 2027 ICC contribution", False),
        ("China sentences official to death for spying", False),
        ("S. Korea shelters Ulleungdo as jets approach", False),
    ]),
    ("SOUTH & SOUTHEAST ASIA", [
        ("Hanoi restaurant blast kills at least six", False),
        ("Malaysia to send migrants back to Myanmar", False),
        ("Hasina to return to Bangladesh on Dec 16", False),
        ("Indonesia nominates two VP candidates", False),
    ]),
    ("AFRICA", [
        ("Haftar visits Turkey for the first time", False),
        ("DR Congo hunts missing plane; rebels claim hit", True),
        ("Senegal regains AFCON title after appeal", False),
        ("Ituri fighting traps Ebola responders", False),
    ]),
    ("NORTH AMERICA", [
        ("US drone helps capture El Chapo Isidro", False),
        ("Trump pardons turkeys Freedom and Feathers", False),
        ("Fort Hood shooter Hasan seeks stay", False),
    ]),
    ("LATIN AMERICA", [
        ("25 hostages held at Cartagena supermarket", False),
        ("Car bomb injures 23 in Colombia", False),
        ("Bukele names 3 soldiers killed in Haiti", False),
    ]),
    ("MARKETS & TECH", [
        ("Iraq takes control of Kurdish oilfields", False),
        ("US blacklists Megaspeed over Nvidia scandal", False),
        ("Pentagon rebukes Canada on F-35, spending", False),
    ]),
    ("DEFENCE", [
        ("Turkish helicopter crash kills five", False),
        ("UK sanctions Houthis, four officials", False),
    ]),
]

HEROES = [
    {
        "draw": "scales",
        "lines": ["ICJ: MYANMAR GUILTY", "OF GENOCIDE"],
        "cap": "First time UN court finds a state responsible; 9-6 ruling on Rohingya",
        "accent": (31, 93, 140),
    },
    {
        "draw": "courthouse",
        "lines": ["HUAWEI GUILTY OF", "TRADE-SECRETS THEFT"],
        "cap": "US jury convicts on 10 of 12 counts; acquits on racketeering",
        "accent": (146, 44, 44),
    },
    {
        "draw": "tanker",
        "lines": ["FOUR TANKERS HIT", "MINES IN HORMUZ"],
        "cap": "IRGC claims ship attack; strait closure threat grows",
        "accent": (0, 110, 110),
    },
]

TICKER = "ALSO TODAY — Norway in dialogue with Ukraine on stability · Gaza meningitis epidemic alert after case surge"
DATECHECK = "DATE CHECK — LEFT OUT (OTHER DAYS): Huang reinstated as Nvidia CEO Mon 23 Nov · Sparta II hit Sat 22 Nov · Riemann proof Sat 22 Nov · Peru quake Fri 21 Nov."
FOOTER = "Every story above happened or was first reported on Tuesday 24 November 2026."

# ---------------------------------------------------------------- pictures
# Every picture is drawn from simple bold shapes in ink + one accent colour.
# Each takes the centre (cx, cy) and a size s; it draws inside that square.


def draw_scales(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # post + base
    d.rectangle([cx - 3 * u, cy - 42 * u, cx + 3 * u, cy + 38 * u], fill=ink)
    d.rectangle([cx - 26 * u, cy + 38 * u, cx + 26 * u, cy + 46 * u], fill=ink)
    # beam
    d.line([(cx - 40 * u, cy - 34 * u), (cx + 40 * u, cy - 34 * u)], fill=ink, width=max(2, int(5 * u)))
    d.ellipse([cx - 6 * u, cy - 48 * u, cx + 6 * u, cy - 36 * u], fill=accent)
    # left pan
    d.line([(cx - 40 * u, cy - 34 * u), (cx - 40 * u, cy - 6 * u)], fill=ink, width=max(2, int(3 * u)))
    d.pieslice([cx - 56 * u, cy - 8 * u, cx - 24 * u, cy + 16 * u], 0, 180, fill=accent)
    # right pan
    d.line([(cx + 40 * u, cy - 34 * u), (cx + 40 * u, cy - 6 * u)], fill=ink, width=max(2, int(3 * u)))
    d.pieslice([cx + 24 * u, cy - 8 * u, cx + 56 * u, cy + 16 * u], 0, 180, fill=accent)
    # gavel, bottom right
    d.rectangle([cx + 14 * u, cy + 20 * u, cx + 44 * u, cy + 32 * u], fill=ink)
    d.line([(cx + 29 * u, cy + 32 * u), (cx + 44 * u, cy + 46 * u)], fill=ink, width=max(2, int(4 * u)))


def draw_courthouse(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # pediment
    d.polygon([(cx - 44 * u, cy - 18 * u), (cx + 44 * u, cy - 18 * u), (cx, cy - 44 * u)], fill=ink)
    # columns
    for dx in (-34, -12, 12, 34):
        d.rectangle([cx + dx * u - 4 * u, cy - 16 * u, cx + dx * u + 4 * u, cy + 30 * u], fill=ink)
    # base + steps
    d.rectangle([cx - 48 * u, cy + 30 * u, cx + 48 * u, cy + 40 * u], fill=ink)
    d.rectangle([cx - 52 * u, cy + 40 * u, cx + 52 * u, cy + 46 * u], fill=accent)
    # chip in front (trade-secrets silicon)
    d.rectangle([cx - 13 * u, cy + 6 * u, cx + 13 * u, cy + 28 * u], fill=CREAM, outline=accent, width=max(2, int(3 * u)))
    for dx in (-8, 0, 8):
        d.line([(cx + dx * u, cy + 2 * u), (cx + dx * u, cy + 6 * u)], fill=accent, width=max(2, int(2 * u)))
        d.line([(cx + dx * u, cy + 28 * u), (cx + dx * u, cy + 32 * u)], fill=accent, width=max(2, int(2 * u)))
    d.rectangle([cx - 5 * u, cy + 14 * u, cx + 5 * u, cy + 22 * u], fill=accent)


def draw_court_plain(d, cx, cy, s, ink, accent):
    u = s / 100.0
    d.polygon([(cx - 42 * u, cy - 20 * u), (cx + 42 * u, cy - 20 * u), (cx, cy - 44 * u)], fill=ink)
    for dx in (-30, -10, 10, 30):
        d.rectangle([cx + dx * u - 4 * u, cy - 18 * u, cx + dx * u + 4 * u, cy + 28 * u], fill=ink)
    d.rectangle([cx - 46 * u, cy + 28 * u, cx + 46 * u, cy + 38 * u], fill=ink)
    d.rectangle([cx - 50 * u, cy + 38 * u, cx + 50 * u, cy + 44 * u], fill=accent)


def draw_tanker(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # hull
    d.polygon([(cx - 48 * u, cy - 6 * u), (cx + 48 * u, cy - 6 * u), (cx + 36 * u, cy + 22 * u),
               (cx - 36 * u, cy + 22 * u)], fill=ink)
    # containers
    for i, dx in enumerate((-38, -16, 6, 28)):
        h = 14 * u if i % 2 == 0 else 10 * u
        d.rectangle([cx + dx * u, cy - 6 * u - h, cx + (dx + 18) * u, cy - 6 * u],
                    fill=accent if i % 2 == 0 else ink, outline=CREAM, width=max(1, int(2 * u)))
    # funnel
    d.rectangle([cx + 34 * u, cy - 22 * u, cx + 46 * u, cy - 6 * u], fill=accent)
    # naval mine, upper left
    mx, my = cx - 34 * u, cy - 34 * u
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        d.line([(mx + 10 * u * math.cos(a), my + 10 * u * math.sin(a)),
                (mx + 17 * u * math.cos(a), my + 17 * u * math.sin(a))], fill=ink, width=max(2, int(3 * u)))
    d.ellipse([mx - 10 * u, my - 10 * u, mx + 10 * u, my + 10 * u], fill=ink)
    # waves
    for wy in (30, 40):
        d.arc([cx - 52 * u, cy + wy * u, cx - 20 * u, cy + (wy + 14) * u], 180, 360, fill=accent, width=max(2, int(3 * u)))
        d.arc([cx - 8 * u, cy + wy * u, cx + 24 * u, cy + (wy + 14) * u], 180, 360, fill=accent, width=max(2, int(3 * u)))
        d.arc([cx + 28 * u, cy + wy * u, cx + 52 * u, cy + (wy + 14) * u], 180, 360, fill=accent, width=max(2, int(3 * u)))


def draw_ship(d, cx, cy, s, ink, accent):
    u = s / 100.0
    d.polygon([(cx - 44 * u, cy - 4 * u), (cx + 44 * u, cy - 4 * u), (cx + 30 * u, cy + 20 * u),
               (cx - 30 * u, cy + 20 * u)], fill=ink)
    d.rectangle([cx - 4 * u, cy - 34 * u, cx + 4 * u, cy - 4 * u], fill=ink)
    d.polygon([(cx + 4 * u, cy - 32 * u), (cx + 4 * u, cy - 10 * u), (cx + 26 * u, cy - 10 * u)], fill=accent)
    d.arc([cx - 48 * u, cy + 26 * u, cx - 16 * u, cy + 40 * u], 180, 360, fill=accent, width=max(2, int(3 * u)))
    d.arc([cx + 4 * u, cy + 26 * u, cx + 36 * u, cy + 40 * u], 180, 360, fill=accent, width=max(2, int(3 * u)))
    d.arc([cx + 30 * u, cy + 34 * u, cx + 52 * u, cy + 46 * u], 180, 360, fill=accent, width=max(2, int(3 * u)))


def draw_dunes_pin(d, cx, cy, s, ink, accent):
    u = s / 100.0
    d.arc([cx - 50 * u, cy + 6 * u, cx + 10 * u, cy + 44 * u], 180, 360, fill=ink, width=max(2, int(4 * u)))
    d.arc([cx - 10 * u, cy + 16 * u, cx + 50 * u, cy + 46 * u], 180, 360, fill=ink, width=max(2, int(4 * u)))
    # location pin
    d.ellipse([cx - 12 * u, cy - 44 * u, cx + 12 * u, cy - 20 * u], fill=accent)
    d.polygon([(cx - 10 * u, cy - 26 * u), (cx + 10 * u, cy - 26 * u), (cx, cy - 2 * u)], fill=accent)
    d.ellipse([cx - 5 * u, cy - 38 * u, cx + 5 * u, cy - 28 * u], fill=CREAM)


def draw_column(d, cx, cy, s, ink, accent):
    u = s / 100.0
    d.rectangle([cx - 16 * u, cy - 40 * u, cx + 16 * u, cy - 30 * u], fill=ink)
    d.rectangle([cx - 9 * u, cy - 30 * u, cx + 9 * u, cy + 28 * u], fill=ink)
    d.rectangle([cx - 16 * u, cy + 28 * u, cx + 16 * u, cy + 38 * u], fill=ink)
    d.rectangle([cx - 22 * u, cy + 38 * u, cx + 22 * u, cy + 44 * u], fill=accent)
    d.ellipse([cx - 5 * u, cy - 20 * u, cx + 5 * u, cy - 10 * u], fill=accent)


def draw_burst(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # building
    d.rectangle([cx - 34 * u, cy - 6 * u, cx + 6 * u, cy + 44 * u], fill=ink)
    for wy in (-0, 12, 24):
        d.rectangle([cx - 28 * u, cy + wy * u, cx - 18 * u, cy + (wy + 7) * u], fill=CREAM)
        d.rectangle([cx - 8 * u, cy + wy * u, cx + 2 * u, cy + (wy + 7) * u], fill=CREAM)
    # starburst above the roof
    import math
    bx, by = cx + 22 * u, cy - 26 * u
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line([(bx + 8 * u * math.cos(a), by + 8 * u * math.sin(a)),
                (bx + 20 * u * math.cos(a), by + 20 * u * math.sin(a))], fill=accent, width=max(2, int(3 * u)))
    d.ellipse([bx - 7 * u, by - 7 * u, bx + 7 * u, by + 7 * u], fill=accent)


def draw_plane(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # fuselage
    d.polygon([(cx - 48 * u, cy - 2 * u), (cx + 40 * u, cy - 8 * u), (cx + 52 * u, cy - 2 * u),
               (cx + 40 * u, cy + 6 * u), (cx - 48 * u, cy + 6 * u)], fill=ink)
    # main wing
    d.polygon([(cx - 6 * u, cy - 2 * u), (cx + 10 * u, cy - 30 * u), (cx + 22 * u, cy - 30 * u),
               (cx + 12 * u, cy - 2 * u)], fill=ink)
    # tail wing
    d.polygon([(cx - 46 * u, cy - 2 * u), (cx - 34 * u, cy - 18 * u), (cx - 26 * u, cy - 18 * u),
               (cx - 34 * u, cy - 2 * u)], fill=accent)
    # tail fin
    d.polygon([(cx - 48 * u, cy - 4 * u), (cx - 40 * u, cy - 26 * u), (cx - 32 * u, cy - 26 * u),
               (cx - 36 * u, cy - 4 * u)], fill=accent)
    # windows
    for dx in (-30, -18, -6, 6, 18):
        d.ellipse([cx + dx * u - 2 * u, cy - 4 * u, cx + dx * u + 2 * u, cy + 0 * u], fill=CREAM)
    # motion lines
    for wy in (16, 26):
        d.line([(cx - 50 * u, cy + wy * u), (cx - 20 * u, cy + wy * u)], fill=accent, width=max(2, int(3 * u)))


def draw_drone(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # arms
    d.line([(cx - 34 * u, cy - 24 * u), (cx + 34 * u, cy + 24 * u)], fill=ink, width=max(2, int(4 * u)))
    d.line([(cx + 34 * u, cy - 24 * u), (cx - 34 * u, cy + 24 * u)], fill=ink, width=max(2, int(4 * u)))
    # rotors
    for rx, ry in ((-34, -24), (34, -24), (-34, 24), (34, 24)):
        d.ellipse([cx + rx * u - 12 * u, cy + ry * u - 4 * u, cx + rx * u + 12 * u, cy + ry * u + 4 * u],
                  outline=accent, width=max(2, int(3 * u)))
    # body + camera
    d.rounded_rectangle([cx - 16 * u, cy - 12 * u, cx + 16 * u, cy + 12 * u], radius=int(6 * u), fill=ink)
    d.ellipse([cx - 6 * u, cy - 5 * u, cx + 6 * u, cy + 7 * u], fill=accent)
    d.line([(cx, cy + 12 * u), (cx, cy + 26 * u)], fill=ink, width=max(2, int(3 * u)))


def draw_store_lock(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # storefront
    d.rectangle([cx - 40 * u, cy - 18 * u, cx + 40 * u, cy + 42 * u], fill=ink)
    # awning
    for i in range(5):
        x0 = cx - 44 * u + i * 18 * u
        d.polygon([(x0, cy - 34 * u), (x0 + 18 * u, cy - 34 * u), (x0 + 14 * u, cy - 18 * u),
                   (x0 + 4 * u, cy - 18 * u)], fill=accent if i % 2 == 0 else CREAM,
                  outline=ink)
    # door + window
    d.rectangle([cx - 26 * u, cy + 2 * u, cx - 2 * u, cy + 42 * u], fill=CREAM)
    d.rectangle([cx + 8 * u, cy + 2 * u, cx + 32 * u, cy + 22 * u], fill=CREAM)
    # padlock
    d.arc([cx + 8 * u, cy - 12 * u, cx + 32 * u, cy + 8 * u], 180, 360, fill=accent, width=max(2, int(4 * u)))
    d.rounded_rectangle([cx + 4 * u, cy + 0 * u, cx + 36 * u, cy + 26 * u], radius=int(4 * u), fill=accent)
    d.ellipse([cx + 16 * u, cy + 8 * u, cx + 24 * u, cy + 16 * u], fill=CREAM)


def draw_pumpjack(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # support tower
    d.line([(cx - 26 * u, cy + 44 * u), (cx - 6 * u, cy - 8 * u)], fill=ink, width=max(2, int(4 * u)))
    d.line([(cx + 14 * u, cy + 44 * u), (cx - 6 * u, cy - 8 * u)], fill=ink, width=max(2, int(4 * u)))
    d.line([(cx - 20 * u, cy + 20 * u), (cx + 4 * u, cy + 20 * u)], fill=ink, width=max(2, int(3 * u)))
    # walking beam
    d.line([(cx - 44 * u, cy - 16 * u), (cx + 40 * u, cy - 28 * u)], fill=ink, width=max(2, int(5 * u)))
    # horse head (right end)
    d.polygon([(cx + 40 * u, cy - 28 * u), (cx + 52 * u, cy - 20 * u), (cx + 46 * u, cy - 6 * u),
               (cx + 36 * u, cy - 12 * u)], fill=accent)
    # counterweight (left end)
    d.rectangle([cx - 50 * u, cy - 22 * u, cx - 38 * u, cy - 6 * u], fill=accent)
    # sucker rod
    d.line([(cx + 46 * u, cy - 6 * u), (cx + 46 * u, cy + 44 * u)], fill=ink, width=max(2, int(3 * u)))
    # base
    d.rectangle([cx - 52 * u, cy + 44 * u, cx + 52 * u, cy + 50 * u], fill=ink)


def draw_helicopter(d, cx, cy, s, ink, accent):
    u = s / 100.0
    # main rotor
    d.line([(cx - 52 * u, cy - 34 * u), (cx + 52 * u, cy - 34 * u)], fill=ink, width=max(2, int(4 * u)))
    d.line([(cx, cy - 34 * u), (cx, cy - 22 * u)], fill=ink, width=max(2, int(3 * u)))
    # body
    d.rounded_rectangle([cx - 34 * u, cy - 22 * u, cx + 18 * u, cy + 6 * u], radius=int(10 * u), fill=ink)
    # cockpit window
    d.ellipse([cx + 2 * u, cy - 18 * u, cx + 16 * u, cy - 4 * u], fill=CREAM)
    # tail boom + tail rotor
    d.line([(cx - 34 * u, cy - 12 * u), (cx - 52 * u, cy - 18 * u)], fill=ink, width=max(2, int(4 * u)))
    d.line([(cx - 52 * u, cy - 30 * u), (cx - 52 * u, cy - 6 * u)], fill=accent, width=max(2, int(3 * u)))
    # skids
    d.line([(cx - 26 * u, cy + 14 * u), (cx + 12 * u, cy + 14 * u)], fill=ink, width=max(2, int(3 * u)))
    d.line([(cx - 22 * u, cy + 6 * u), (cx - 22 * u, cy + 14 * u)], fill=ink, width=max(2, int(3 * u)))
    d.line([(cx + 8 * u, cy + 6 * u), (cx + 8 * u, cy + 14 * u)], fill=ink, width=max(2, int(3 * u)))


LEAD_DRAW = [
    draw_court_plain, draw_ship, draw_dunes_pin, draw_column, draw_burst,
    draw_plane, draw_drone, draw_store_lock, draw_pumpjack, draw_helicopter,
]
HERO_DRAW = {"scales": draw_scales, "courthouse": draw_courthouse, "tanker": draw_tanker}

# ---------------------------------------------------------------- layout
MARGIN = 32
warnings = []


def fit_font(draw, s, path, size, max_w):
    f = font(path, size)
    while size > 10 and text_w(draw, s, f) > max_w:
        size -= 2
        f = font(path, size)
    return f


def draw_masthead(d):
    draw_center(d, W // 2, 6, "THE TUESDAY WORLD", serif_b(54), INK)
    f = fit_font(d, "TUESDAY 24 NOVEMBER 2026", _SANS_BOLD, 62, W - 2 * MARGIN)
    draw_center(d, W // 2, 64, "TUESDAY 24 NOVEMBER 2026", f, INK)
    d.line([(MARGIN, 134), (W - MARGIN, 134)], fill=INK, width=2)
    draw_center(d, W // 2, 140, "THE WORLD IN ONE DAY — 37 STORIES, 10 REGIONS",
                sans_b(16), INK)


def draw_heroes(d):
    y0, ph = 160, 224
    pw, gap = 312, 12
    for i, h in enumerate(HEROES):
        x = MARGIN + i * (pw + gap)
        accent = h["accent"]
        d.rectangle([x, y0, x + pw, y0 + ph], outline=INK, width=2)
        d.rectangle([x, y0, x + pw, y0 + 6], fill=accent)
        HERO_DRAW[h["draw"]](d, x + pw // 2, y0 + 62, 100, INK, accent)
        f = serif_b(20)
        draw_center(d, x + pw // 2, y0 + 124, h["lines"][0], f, INK)
        draw_center(d, x + pw // 2, y0 + 146, h["lines"][1], f, INK)
        cap_lines = wrap(d, h["cap"], sans(11.5), pw - 24)
        cy = y0 + 174
        for ln in cap_lines[:2]:
            draw_center(d, x + pw // 2, cy, ln, sans(11.5), MUTED)
            cy += 15


def draw_map(d):
    y0, y1 = 392, 468
    # continent blobs (cx, cy, rx, ry) in strip coordinates
    blobs = [
        (170, 425, 95, 20), (330, 448, 42, 16), (500, 412, 42, 12),
        (545, 442, 52, 20), (720, 420, 130, 18), (890, 452, 38, 9),
    ]
    dot = (130, 124, 112)
    step = 8
    for gx in range(MARGIN, W - MARGIN, step):
        for gy in range(y0 + 6, y1, step):
            inside = False
            for (cx, cy, rx, ry) in blobs:
                if ((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 <= 1.0:
                    inside = True
                    break
            if inside:
                d.ellipse([gx - 1.6, gy - 1.6, gx + 1.6, gy + 1.6], fill=dot)
    pins = [(478, 410), (520, 408), (565, 428), (735, 412), (790, 436),
            (545, 446), (170, 422), (330, 450), (620, 432), (505, 430)]
    for i, (px, py) in enumerate(pins):
        acc = ACCENTS[i]
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=acc, outline=CREAM, width=1)
        num = str(i + 1)
        nf = sans_b(11)
        d.text((px - text_w(d, num, nf) / 2, py - 8), num, font=nf, fill=CREAM)
    draw_center(d, W - MARGIN - 60, y0 + 2, "THE WORLD", sans_b(11), MUTED)


def claim_tag(d, x, y, s="CLAIM"):
    f = sans_b(8)
    tw = text_w(d, s, f) + 8
    rr(d, [x, y, x + tw, y + 12], 3, fill=AMBER_BG, outline=AMBER, width=1)
    d.text((x + 4, y + 1), s, font=f, fill=INK)
    return tw


def draw_bands(d):
    y0 = 476
    row_h, col_w, gap = 90, 472, 16
    for idx, (label, stories) in enumerate(BANDS):
        row, col = divmod(idx, 2)
        x = MARGIN + col * (col_w + gap)
        y = y0 + row * row_h
        acc = ACCENTS[idx]
        # header: number chip + region label
        d.ellipse([x + 2, y + 2, x + 22, y + 22], fill=acc)
        num = str(idx + 1)
        nf = sans_b(12)
        d.text((x + 12 - text_w(d, num, nf) / 2, y + 4), num, font=nf, fill=CREAM)
        d.text((x + 28, y + 4), label, font=sans_b(14.5), fill=acc)
        d.line([(x + 28, y + 23), (x + 28 + text_w(d, label, sans_b(14.5)), y + 23)],
               fill=acc, width=2)
        # lead illustration
        LEAD_DRAW[idx](d, x + 30, y + 56, 56, INK, acc)
        # story lines
        sx = x + 66
        ly = y + 28
        for (headline, claim) in stories:
            f = sans(12.5)
            hw = text_w(d, headline, f)
            if sx + hw > x + col_w - 6:
                warnings.append("OVERFLOW band %d: %r" % (idx + 1, headline))
            d.text((sx, ly), headline, font=f, fill=INK)
            if claim:
                tag_w = text_w(d, "CLAIM", sans_b(8)) + 8
                tx = sx + hw + 4
                if tx + tag_w > x + col_w - 4:
                    tx = x + col_w - 4 - tag_w
                    warnings.append("TAG CLIP band %d: %r" % (idx + 1, headline))
                claim_tag(d, tx, ly + 1)
            ly += 15


def draw_bottom(d):
    # ticker
    d.line([(MARGIN, 932), (W - MARGIN, 932)], fill=INK, width=1)
    tf = sans(13)
    if text_w(d, TICKER, tf) > W - 2 * MARGIN:
        tf = sans(12)
    draw_center(d, W // 2, 938, TICKER, tf, INK)
    # date check box (two lines)
    d.rectangle([MARGIN, 962, W - MARGIN, 996], outline=RED, width=2)
    d.text((MARGIN + 8, 966), "DATE CHECK — LEFT OUT (OTHER DAYS):",
           font=sans_b(11.5), fill=RED)
    d.text((MARGIN + 8, 980),
           "Huang reinstated as Nvidia CEO Mon 23 Nov · Sparta II hit Sat 22 Nov · Riemann proof Sat 22 Nov · Peru quake Fri 21 Nov.",
           font=sans(11.5), fill=INK)
    # footer + claim legend
    draw_center(d, W // 2, 1002, FOOTER + "  CLAIM = as claimed, not independently confirmed.",
                sans(12), MUTED)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_heroes(d)
    draw_map(d)
    draw_bands(d)
    draw_bottom(d)
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s %dx%d %d bytes" % (out, W, H, size))
    if size > 1048576:
        print("WARNING: over 1 MiB")
    for w in warnings:
        print("WARNING: " + w)


if __name__ == "__main__":
    main()
