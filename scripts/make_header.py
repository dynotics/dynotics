"""header card. ascii portrait on the left, neofetch-style info block on the right.

portrait is the 230x107 render with the softer tonal curve, the sharp one carved
my nasolabial folds into strokes. drawn at native cell size and then scaled into
the left column, so the glyph rhythm stays put no matter how wide the column is.
"""
from itertools import groupby
from PIL import Image
import colorsys
import html
import pathlib

CARD_W = 985
PAD = 16
P_X, P_COL_W = 22, 376      # portrait column. narrow so the shoulder stops short of the info column
I_X, I_W = 446, CARD_W - 446 - 22
FS, LH = 13, 22             # info block font size and line height
COLS_I = 66                 # info block width in characters

# palette, all pulled off the shrimp pfp so the card matches it
CARD = '#faf7f4'            # a hair off the avatar's shell circle
TEXT = '#3f2f2c'            # darkened rose -> body text
LABEL = '#bd5c63'           # the shrimp's outline -> keys
VALUE = '#2f6f6b'           # deep seafoam off the bubbles -> values
DIM = '#c9b8b0'             # pale salmon -> leaders and rules
INK = '#4b5159'             # for portrait pixels too grey to carry a hue

COLS_P = 230
CELL_W, CELL_H = 2.4, 4.8   # native cell of the render i picked
SRC = pathlib.Path(__file__).resolve().parent / 'portrait_wide.png'
OUT = pathlib.Path(__file__).resolve().parent.parent / 'header.svg'

src = Image.open(SRC).convert('RGB')
rows = int(src.height / src.width * COLS_P * CELL_W / CELL_H)
small = src.resize((COLS_P, rows), Image.LANCZOS)
NAT_W, NAT_H = COLS_P * CELL_W, rows * CELL_H
SCALE = P_COL_W / NAT_W
P_H = NAT_H * SCALE

# dark -> light. \/| repeats six times so midtones spread across strokes of the
# same weight instead of jumping a step every shade
RAMP = "@M#W%8&$*\\/|\\/|\\/|\\/|\\/|\\/|)(1{}[]?+~<>!;:,."

LINES = [
    ('title', 'dylanchin'),
    ('kv', 'Role', "CS student @ NYU '28"),
    ('kv', 'Location', 'Brooklyn, New York'),
    ('kv', 'Orgs', 'NYU HSRN / Urban Arts / StuyCS'),
    ('kv', 'Focus', 'Full-Stack, Real-Time Systems, XR, Game Dev'),
    ('blank',),
    ('kv', 'Languages', 'C#, TypeScript, Python, C++, Java'),
    ('kv', 'Frameworks', 'Unity, React, Next.js, Astro, Tailwind'),
    ('blank',),
    ('section', 'Contact'),
    ('kv', 'Email', 'dylantychin@gmail.com'),
    ('kv', 'Portfolio', 'dynotics.github.io'),
    ('kv', 'LinkedIn', 'linkedin.com/in/dylan-chin-8964ba284'),
    ('kv', 'GitHub', 'github.com/dynotics'),
    ('blank',),
    ('kv', 'Avatar', 'drawn by me'),
]


def tone(r, g, b):
    """luma, floor lifted off pure black, gamma so the face doesn't blow out"""
    v = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    v = (v - 0.06) / 0.94
    return max(0.0, min(1.0, v)) ** 1.25


def portrait_rows():
    """(char, colour) per cell. colour is None where the cell is blank"""
    out = []
    for ry in range(rows):
        row = []
        for cx in range(COLS_P):
            r, g, b = small.getpixel((cx, ry))
            v = tone(r, g, b)
            if v > 0.965:
                row.append((' ', None))
                continue
            ch = RAMP[min(int((v ** 1.05) * (len(RAMP) - 1)), len(RAMP) - 1)]
            if max(r, g, b) - min(r, g, b) > 28:
                # saturate hard, the ascii grid eats a lot of the colour
                h_, s_, v_ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                s_ = min(1.0, s_ * 1.9)
                col = '#%02x%02x%02x' % tuple(
                    int(c * 255) for c in colorsys.hsv_to_rgb(h_, s_, v_ * 0.92))
            else:
                col = INK
            row.append((ch, col))
        out.append(row)
    return out


def spans(row):
    """collapse a row into runs of one colour, one tspan each"""
    out = []
    for col, cells in groupby(row, key=lambda c: c[1]):
        text = html.escape(''.join(ch for ch, _ in cells))
        out.append(text if col is None else f'<tspan fill="{col}">{text}</tspan>')
    return ''.join(out)


def leader(n):
    """dotted run between a key and its value. never shorter than two dots"""
    return f'<tspan class="d">{"." * max(n, 2)}</tspan>'


def info_line(ln):
    kind = ln[0]
    if kind == 'title':
        return (f'<tspan class="b">{ln[1]}</tspan> '
                f'<tspan class="d">{"─" * (COLS_I - len(ln[1]) - 1)}</tspan>')
    if kind == 'section':
        return (f'<tspan class="d">─</tspan> <tspan class="b">{ln[1]}</tspan> '
                f'<tspan class="d">{"─" * (COLS_I - len(ln[1]) - 3)}</tspan>')
    if kind == 'kv':
        k, v = ln[1], ln[2]
        return (f'<tspan class="d">.</tspan> <tspan class="l">{k}:</tspan> '
                f'{leader(COLS_I - len(k) - len(v) - 5)} '
                f'<tspan class="v">{html.escape(v)}</tspan>')
    raise ValueError(f'unknown line kind: {kind}')


def build():
    info_h = len(LINES) * LH
    H = int(max(P_H, info_h) + PAD * 2)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{H}" viewBox="0 0 {CARD_W} {H}" '
           f'font-family="Consolas,\'Liberation Mono\',\'DejaVu Sans Mono\',Menlo,monospace">',
           '<style>text,tspan{white-space:pre;}'
           f'.i{{font-size:{FS}px;fill:{TEXT};}} .l{{fill:{LABEL};}} '
           f'.v{{fill:{VALUE};}} .d{{fill:{DIM};}} .b{{font-weight:bold;}}'
           '</style>',
           f'<rect width="{CARD_W}" height="{H}" fill="{CARD}"/>']

    # draw the portrait at native size, then scale the whole group into its column
    ty = (H - P_H) / 2
    out.append(f'<g transform="translate({P_X},{ty:.2f}) scale({SCALE:.5f})" font-size="{CELL_H}px">')
    for i, row in enumerate(portrait_rows()):
        y = round((i + 1) * CELL_H, 2)
        out.append(f'<text x="0" y="{y}" textLength="{NAT_W}" lengthAdjust="spacingAndGlyphs" '
                   f'xml:space="preserve">{spans(row)}</text>')
    out.append('</g>')

    # textLength on every line is what keeps the leaders lining up. the browser
    # squeezes each line to exactly I_W whatever font it ends up with
    iy = (H - info_h) / 2 + FS
    for i, ln in enumerate(LINES):
        if ln[0] == 'blank':
            continue
        y = round(iy + i * LH, 2)
        out.append(f'<text class="i" x="{I_X}" y="{y}" textLength="{I_W}" lengthAdjust="spacingAndGlyphs" '
                   f'xml:space="preserve">{info_line(ln)}</text>')

    out.append('</svg>')
    return '\n'.join(out)


if __name__ == '__main__':
    OUT.write_text(build())
    print(f'header.svg  {OUT.stat().st_size // 1024} KB')
    print(f'{COLS_P}x{rows}, scale {SCALE:.3f}, portrait {P_COL_W}x{P_H:.0f}')
