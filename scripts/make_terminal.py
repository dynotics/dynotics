"""terminal banner. the prompt types a line, holds it, clears it, next one.

every colour is sampled off the shrimp pfp, nothing invented:

    #f2ece7  shell       the avatar's background circle -> the typed text
    #dba595  pale salmon                                -> the ~ and the rule
    #d1887c  salmon      the shrimp's body              -> the % prompt
    #bd5c63  deep rose   its outline, the darkest tone  -> the cursor
    #8bc4bf  seafoam     the bubbles                    -> my name

no js, no gif. one clipPath per line, and its width sits at zero outside that
line's slot, so a line hides itself instead of two opacity animations arguing
over who owns the row.
"""
import pathlib

W, H = 985, 92
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'terminal.svg'

# dark strip under the light card so the two read as separate objects
BG = '#241c1b'          # darkened rose -> the strip
USER = '#8bc4bf'        # bubbles -> my name
SALMON = '#d1887c'      # shrimp body -> the % prompt
TEXT = '#f2ece7'        # shell -> the typed text
HIGHLIGHT = '#dba595'   # pale salmon -> the ~ and the rule
ROSE = '#bd5c63'        # outline -> the cursor

PROMPT = 'dylanchin'
FS = 19
ADV = FS * 0.6          # monospace advance. every x below is counted in these
X = 34                  # left margin
Y = H / 2 + 7           # baseline
PER = 3.6               # seconds per line

# beats inside one line's slot, as fractions of PER: typed, held, cleared
TYPED, HELD, GONE = 0.34, 0.80, 0.92

LINES = [
    'real-time systems',
    'XR + graphics',
    'game engines',
    'full-stack',
]


def build():
    total = PER * len(LINES)
    x_tilde = X + (len(PROMPT) + 1) * ADV
    x_pct = x_tilde + 2 * ADV
    x_text = x_pct + 2 * ADV

    def keytimes(ts):
        """seconds -> the 0..1 keyTimes smil wants"""
        return ';'.join(f'{min(max(t / total, 0), 1):.4f}' for t in ts)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" '
         f'font-family="Consolas,\'Liberation Mono\',\'DejaVu Sans Mono\',Menlo,monospace">',
         f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         # hairline rule, echoes the dotted leaders on the card above it
         f'<line x1="{X}" y1="{H-19}" x2="{W-X}" y2="{H-19}" stroke="{HIGHLIGHT}" '
         f'stroke-width="1" opacity="0.26"/>',
         f'<text x="{X}" y="{Y}" font-size="{FS}" font-weight="bold" fill="{USER}" '
         f'xml:space="preserve">{PROMPT}</text>',
         f'<text x="{x_tilde}" y="{Y}" font-size="{FS}" fill="{HIGHLIGHT}">~</text>',
         f'<text x="{x_pct}" y="{Y}" font-size="{FS}" fill="{SALMON}">%</text>']

    # cursor keyframes, collected as each line lays down its own
    cur_t, cur_x = [0.0], [0.0]
    for i, ln in enumerate(LINES):
        s = i * PER
        wfull = len(ln) * ADV
        ts = [0.0, s, s + PER * TYPED, s + PER * HELD, s + PER * GONE, total]
        vs = [0, 0, wfull, wfull, 0, 0]
        if i == 0:
            # first line starts at t=0, so it has no lead-in keyframe to hold
            ts, vs = ts[1:], vs[1:]
        o.append(f'<clipPath id="w{i}"><rect x="{x_text}" y="0" width="0" height="{H}">'
                 f'<animate attributeName="width" values="{";".join(str(round(v,1)) for v in vs)}" '
                 f'keyTimes="{keytimes(ts)}" dur="{total}s" repeatCount="indefinite" '
                 f'calcMode="linear"/></rect></clipPath>')
        o.append(f'<g clip-path="url(#w{i})"><text x="{x_text}" y="{Y}" font-size="{FS}" '
                 f'fill="{TEXT}" xml:space="preserve">{ln}</text></g>')
        cur_t += [s, s + PER * TYPED, s + PER * HELD, s + PER * GONE]
        cur_x += [0, wfull, wfull, 0]
    cur_t.append(total)
    cur_x.append(0)

    # cursor rides the end of the text on the loop clock, blinks on its own
    o.append(f'<g><animateTransform attributeName="transform" type="translate" '
             f'values="{";".join(f"{v:.1f},0" for v in cur_x)}" keyTimes="{keytimes(cur_t)}" '
             f'dur="{total}s" repeatCount="indefinite" calcMode="linear"/>'
             f'<rect x="{x_text}" y="{Y-14}" width="{ADV:.1f}" height="19" fill="{ROSE}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
             f'dur="1.1s" repeatCount="indefinite" calcMode="discrete"/></rect>'
             f'</g>')
    o.append('</svg>')
    return '\n'.join(o)


if __name__ == '__main__':
    OUT.write_text(build())
    print(f'{OUT.name}  {OUT.stat().st_size} bytes')
