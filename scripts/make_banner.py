"""Generate an animated (SMIL) SVG banner: a swarm of cursors builds Imran's card.
Everything runs on one shared 14s loop so all animations stay in sync."""
import sys

T = 14.0
OUT = sys.argv[1]

RED, WHITE, PINK, ROSE, DEEP = '#ff2d46', '#f5f5f6', '#ff7a8a', '#ffb3bc', '#e0112b'
BG, SURF, BORDER, MUTED = '#0a0a0b', '#131316', '#2a2a30', '#a1a1aa'
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
FADE_OUT, GONE = 12.8, 13.4


def kt(points):
    """points: [(t, value)] -> padded (keyTimes, values) covering 0..T."""
    pts = sorted(points, key=lambda p: p[0])
    if pts[0][0] > 0:
        pts.insert(0, (0, pts[0][1]))
    if pts[-1][0] < T:
        pts.append((T, pts[-1][1]))
    # strictly increasing key times
    out, last = [], -1
    for t, v in pts:
        t = max(t, last + 0.001) if out else t
        out.append((min(t, T), v)); last = t
    out[-1] = (T, out[-1][1])
    return ';'.join(f'{t / T:.4f}' for t, _ in out), ';'.join(str(v) for _, v in out), len(out)


def anim(attr, points, calc='linear'):
    k, v, n = kt(points)
    extra = ''
    if calc == 'spline':
        extra = ' keySplines="' + ';'.join(['0.45 0 0.2 1'] * (n - 1)) + '"'
    return f'<animate attributeName="{attr}" dur="{T}s" repeatCount="indefinite" calcMode="{calc}" keyTimes="{k}" values="{v}"{extra}/>'


def anim_t(kind, points, calc='linear'):
    k, v, n = kt(points)
    extra = ''
    if calc == 'spline':
        extra = ' keySplines="' + ';'.join(['0.45 0 0.2 1'] * (n - 1)) + '"'
    return f'<animateTransform attributeName="transform" type="{kind}" dur="{T}s" repeatCount="indefinite" calcMode="{calc}" keyTimes="{k}" values="{v}"{extra}/>'


def show(t_on, t_off=FADE_OUT, fade=0.25):
    """opacity: hidden until t_on, visible until t_off."""
    return anim('opacity', [(0, 0), (t_on, 0), (t_on + fade, 1), (t_off, 1), (t_off + 0.01, 1)])


defs, body, overlay = [], [], []
clip_id = 0


def typed(x, y, text, length, t0, t1, size, fill, weight=400, family=SANS, spacing=0, caret=None):
    """Text revealed one character at a time, with a caret riding the edge."""
    global clip_id
    clip_id += 1
    cid = f'c{clip_id}'
    n = len(text)
    steps = [(0, 0), (t0, 0)]
    for i in range(1, n + 1):
        steps.append((t0 + (t1 - t0) * i / n, round(length * i / n + 4, 1)))
    asc = size * 1.0
    defs.append(f'<clipPath id="{cid}"><rect x="{x - 2}" y="{y - asc}" height="{size * 1.35}" width="0">{anim("width", steps, "discrete")}</rect></clipPath>')
    ls = f' letter-spacing="{spacing}"' if spacing else ''
    body.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}"{ls} '
                f'textLength="{length}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{cid})">{esc(text)}</text>')
    if caret:
        cx = [(0, x), (t0, x)] + [(t0 + (t1 - t0) * i / n, round(x + length * i / n + 2, 1)) for i in range(1, n + 1)]
        overlay.append(f'<rect y="{y - size * 0.82}" width="2" height="{size * 0.95}" fill="{caret}">'
                       f'{anim("x", cx, "discrete")}'
                       f'{anim("opacity", [(0, 0), (t0, 0), (t0 + .01, 1), (t1 + .5, 1), (t1 + .51, 0)], "discrete")}</rect>')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')


def drawn_box(x, y, w, h, t0, t1, color, rx=16, fill=SURF, stroke=BORDER, label=True):
    """Dashed selection box dragged out, then the real card fades in."""
    body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5">{show(t1, fade=0.3)}</rect>')
    grow_w = [(0, 0), (t0, 0), (t1, w)]
    grow_h = [(0, 0), (t0, 0), (t1, h)]
    vis = anim('opacity', [(0, 0), (t0, 0), (t0 + .01, 1), (t1 + .15, 1), (t1 + .45, 0)])
    overlay.append(f'<rect x="{x}" y="{y}" width="0" height="0" fill="{color}" fill-opacity="0.07" stroke="{color}" stroke-width="1.5" stroke-dasharray="6 5">'
                   f'{anim("width", grow_w, "spline")}{anim("height", grow_h, "spline")}{vis}</rect>')
    for hx, hy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        pos = [(0, f'{x} {y}'), (t0, f'{x} {y}'), (t1, f'{x + w * hx} {y + h * hy}')]
        overlay.append(f'<g>{anim_t("translate", pos, "spline")}<rect x="-4" y="-4" width="8" height="8" fill="#fff" stroke="{color}" stroke-width="1.5">{vis}</rect></g>')
    if label:
        txt = f'{w} × {h}'
        lw = len(txt) * 7.2 + 14
        pos = [(0, f'{x} {y}'), (t0, f'{x} {y}'), (t1, f'{x + w / 2 - lw / 2} {y + h + 10}')]
        overlay.append(f'<g>{anim_t("translate", pos, "spline")}<g>{vis}<rect width="{lw}" height="20" rx="4" fill="{color}"/>'
                       f'<text x="{lw / 2}" y="14" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#0a0a0b">{txt}</text></g></g>')


def ripple(cx, cy, t, color):
    overlay.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="none" stroke="{color}" stroke-width="2">'
                   f'{anim("r", [(0, 4), (t, 4), (t + .45, 20)])}'
                   f'{anim("opacity", [(0, 0), (t, 0), (t + .01, 1), (t + .45, 0)])}</circle>')


def chip(x, y, text, t, red=False):
    w = round(len(text) * 7.4 + 26)
    cx, cy = x + w / 2, y + 14
    fill = '#2a0a10' if red else '#16161a'
    stroke = '#7a1a26' if red else '#33333a'
    color = '#ff8a97' if red else '#d4d4d8'
    body.append(f'<g transform="translate({cx} {cy})"><g>'
                f'{anim_t("scale", [(0, 0), (t, 0), (t + .16, 1.12), (t + .26, 1)], "linear")}'
                f'<rect x="{-w / 2}" y="-14" width="{w}" height="28" rx="14" fill="{fill}" stroke="{stroke}"/>'
                f'<text y="4.5" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{color}">{esc(text)}</text></g></g>')
    ripple(cx, cy, t, RED)
    return w, (cx, cy)


ARROW = 'M2 1.5V18.5L6.6 14.3L9.6 20.6L12.5 19.3L9.6 13.1H16Z'
PEN = 'M2.5 19.5L4 14L15.5 2.5a2.1 2.1 0 0 1 3 3L7 17Z'


def cursor(name, color, path, pen_window=None):
    """path: [(t, x, y)] waypoints; cursor visible from first waypoint to fade-out."""
    dark = color in (WHITE, ROSE, '#ffd6db')
    tc = '#0a0a0b' if dark else '#fff'
    stroke = '#0a0a0b' if dark else '#fff'
    pts = [(t, f'{x} {y}') for t, x, y in path]
    lw = len(name) * 7 + 16
    t_on = path[0][0]
    arrow_vis = pen_vis = ''
    if pen_window:
        a, b = pen_window
        arrow_vis = anim('opacity', [(0, 1), (a, 1), (a + .01, 0), (b, 0), (b + .01, 1)], 'discrete')
        pen_vis = anim('opacity', [(0, 0), (a, 0), (a + .01, 1), (b, 1), (b + .01, 0)], 'discrete')
    pen = (f'<path d="{PEN}" transform="translate(-2.5 -19.5)" fill="{color}" stroke="{stroke}" stroke-width="1.4" stroke-linejoin="round" opacity="0">{pen_vis}</path>'
           if pen_window else '')
    overlay.append(
        f'<g>{anim_t("translate", pts, "spline")}<g>{show(t_on, fade=0.2)}'
        f'<path d="{ARROW}" transform="translate(-2 -1.5)" fill="{color}" stroke="{stroke}" stroke-width="1.4" stroke-linejoin="round" filter="url(#sh)">{arrow_vis}</path>'
        f'{pen}'
        f'<rect x="14" y="17" width="{lw}" height="20" rx="6" fill="{color}"/>'
        f'<text x="{14 + lw / 2}" y="31" text-anchor="middle" font-family="{SANS}" font-size="11" font-weight="700" fill="{tc}">{name}</text>'
        f'</g></g>')


# ---------------- scene ----------------
W, H = 1200, 440
# 1. Main card dragged out by Node (red)
drawn_box(40, 40, 1120, 360, 0.6, 1.7, RED)
ripple(40, 40, 0.6, RED)

# 2. Name: guides + typing by React (white)
overlay.append(f'<line x1="0" x2="{W}" y1="106" y2="106" stroke="{WHITE}" stroke-dasharray="4 4" opacity="0">{anim("opacity", [(0, 0), (2.0, 0), (2.1, .7), (3.5, .7), (3.8, 0)])}</line>')
overlay.append(f'<line x1="90" x2="90" y1="70" y2="180" stroke="{WHITE}" stroke-dasharray="4 4" opacity="0">{anim("opacity", [(0, 0), (2.0, 0), (2.1, .7), (3.5, .7), (3.8, 0)])}</line>')
typed(90, 150, 'IMRAN RASHEED', 500, 2.2, 3.4, 60, WHITE, 800, caret=WHITE, spacing=1)

# 3. Subtitle + mono line by Python (pink)
typed(90, 200, 'Senior Software Engineer (Full Stack)', 470, 3.0, 4.1, 26, RED, 600, caret=PINK)
typed(92, 236, 'AI / LLM EVALUATION & AGENT TOOLING', 370, 4.3, 5.0, 14, MUTED, 500, MONO, caret=PINK)

# 4. Pen line by Docker (rose)
overlay_line_t0, overlay_line_t1 = 4.6, 5.4
body.append(f'<line x1="90" y1="262" x2="90" y2="262" stroke="{RED}" stroke-width="2" stroke-linecap="round">'
            f'{anim("x2", [(0, 90), (overlay_line_t0, 90), (overlay_line_t1, 640)], "spline")}'
            f'{anim("opacity", [(0, 0), (overlay_line_t0, 0), (overlay_line_t0 + .05, 1)])}</line>')

# 5. Chips row 1 (React pops) and row 2 (Python pops)
row1 = [('NestJS', 0), ('React', 0), ('Vue', 0), ('Python', 0), ('Docker', 0), ('AWS', 0), ('SWE-Bench+', 1), ('MCP', 1)]
row2 = [('TypeScript', 0), ('Laravel', 0), ('PostgreSQL', 0), ('Function Calling', 1), ('Claude Code', 1)]
x, t = 90, 3.9
r1_pts = []
for text, red in row1:
    w, c = chip(x, 288, text, t, bool(red))
    r1_pts.append((t, c)); x += w + 10; t += 0.27
x, t = 90, 5.3
r2_pts = []
for text, red in row2:
    w, c = chip(x, 328, text, t, bool(red))
    r2_pts.append((t, c)); x += w + 10; t += 0.3

# 6. Side card by Node: stats
drawn_box(820, 96, 290, 250, 2.3, 3.1, RED, rx=14, fill='#160a0d', stroke='#5c1520')
body.append(f'<text x="850" y="186" font-family="{SANS}" font-size="74" font-weight="800" fill="{RED}" textLength="86" lengthAdjust="spacingAndGlyphs">8+'
            f'{anim("opacity", [(0, 0), (3.5, 0), (3.7, 1)])}</text>')
ripple(890, 160, 3.5, RED)
typed(852, 214, 'YEARS ENGINEERING · SINCE 2018', 230, 3.8, 4.4, 11, MUTED, 500, MONO, caret=RED)
body.append(f'<line x1="850" x2="1080" y1="232" y2="232" stroke="#3a1a20">{anim("opacity", [(0, 0), (4.4, 0), (4.6, 1)])}</line>')
typed(850, 264, 'Team Lead @ Turing', 180, 4.6, 5.2, 19, WHITE, 600, caret=RED)
typed(850, 290, 'LLM & coding-agent eval tooling', 220, 5.3, 5.9, 13, MUTED, 400, caret=RED)
typed(850, 322, '● Open to remote roles', 170, 6.0, 6.5, 13, '#ff8a97', 600, caret=RED)

# ---------------- cursors ----------------
# Node (red): main card, side card, side texts
cursor('Node', RED, [
    (0.3, 20, 10), (0.6, 40, 40), (1.7, 1160, 400), (2.0, 1000, 300), (2.3, 820, 96), (3.1, 1110, 346),
    (3.45, 890, 160), (3.8, 852, 218), (4.4, 1082, 218), (4.6, 850, 268), (5.2, 1030, 268),
    (5.3, 850, 294), (5.9, 1070, 294), (6.0, 850, 326), (6.5, 1020, 326),
    (7.4, 1010, 372), (9.5, 1040, 360), (11.5, 1000, 380), (12.8, 1020, 370)])
# React (white): name, then chips row 1
react = [(1.6, 400, -20), (2.0, 84, 104), (2.2, 92, 152), (3.4, 592, 152)]
for tt, (cx, cy) in r1_pts:
    react.append((tt - 0.12, cx, cy + 2))
react += [(6.4, 700, 300), (8.5, 740, 280), (10.5, 690, 300), (12.8, 720, 290)]
cursor('React', WHITE, react)
# Python (pink): subtitle, mono line, chips row 2
python = [(2.5, 640, 470), (3.0, 92, 202), (4.1, 562, 202), (4.3, 94, 238), (5.0, 464, 238)]
for tt, (cx, cy) in r2_pts:
    python.append((tt - 0.12, cx, cy + 2))
python += [(7.0, 760, 350), (9.2, 790, 362), (11.2, 760, 345), (12.8, 775, 355)]
cursor('Python', PINK, python)
# Docker (rose): pen line
cursor('Docker', ROSE, [
    (3.9, 1000, 470), (4.5, 90, 262), (5.4, 640, 262), (6.2, 600, 230), (8.8, 640, 245), (10.8, 610, 235), (12.8, 630, 240)],
    pen_window=(4.5, 5.45))
# Laravel (deep red): wanders in to inspect
cursor('Laravel', DEEP, [(5.6, 1220, 120), (6.3, 1085, 62), (8.0, 1070, 78), (10.0, 1090, 66), (12.8, 1078, 72)])

# ---------------- assemble ----------------
fade_all = anim('opacity', [(0, 1), (FADE_OUT, 1), (GONE, 0), (T - 0.01, 0)])
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Imran Rasheed: Senior Software Engineer (Full Stack)</title>
<desc id="d">A swarm of multiplayer cursors builds Imran Rasheed's profile card live: AI / LLM Evaluation &amp; Agent Tooling, 8+ years, Team Lead at Turing.</desc>
<defs>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#ffffff" fill-opacity="0.07"/></pattern>
<radialGradient id="glow" cx="0.85" cy="0" r="0.7"><stop offset="0" stop-color="{RED}" stop-opacity="0.22"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<filter id="sh" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.6"/></filter>
{''.join(defs)}
</defs>
<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#glow)"/>
<g>{fade_all}
{''.join(body)}
{''.join(overlay)}
</g>
</svg>
'''
open(OUT, 'w').write(svg)
print('wrote', OUT, len(svg), 'bytes')
