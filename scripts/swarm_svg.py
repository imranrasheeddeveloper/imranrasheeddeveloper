"""Tiny toolkit for animated "swarm build" SVGs (pure SMIL, no scripts).

GitHub renders README images with scripts stripped, but SMIL animations inside
an <img> SVG still play. Every animation in a Scene shares one loop duration T,
so all of them stay in sync: build -> hold -> fade -> repeat.
"""
import random

RED, WHITE, PINK, ROSE, DEEP, CORAL = '#ff2d46', '#f5f5f6', '#ff7a8a', '#ffb3bc', '#e0112b', '#ff5c5c'
BG, SURF, BORDER, MUTED, LIGHT = '#0a0a0b', '#131316', '#2a2a30', '#a1a1aa', '#d4d4d8'
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
CURSOR_COLORS = [RED, WHITE, PINK, ROSE, DEEP, CORAL]
ARROW = 'M2 1.5V18.5L6.6 14.3L9.6 20.6L12.5 19.3L9.6 13.1H16Z'
PEN = 'M2.5 19.5L4 14L15.5 2.5a2.1 2.1 0 0 1 3 3L7 17Z'
SPLINE = '0.45 0 0.2 1'


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def text_width(s, size, weight=400, mono=False):
    """Rough natural width; textLength then pins it exactly in every browser."""
    if mono:
        return round(len(s) * size * 0.6, 1)
    w = 0.0
    for ch in s:
        if ch in "iljtfrI.,:;'|!·()[]/":
            w += 0.31
        elif ch == ' ':
            w += 0.28
        elif ch in 'mwMW@':
            w += 0.86
        elif ch.isupper():
            w += 0.67
        elif ch.isdigit():
            w += 0.56
        elif ch in '⇄↗●→':
            w += 0.9
        else:
            w += 0.53
    w *= size
    if weight >= 600:
        w *= 1.06
    return round(w, 1)


def is_light(color):
    n = int(color[1:], 16)
    return (0.299 * (n >> 16) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255 > 0.62


class Scene:
    def __init__(self, w, h, build_end, hold=5.5, seed=7):
        self.w, self.h = w, h
        self.fade_out = build_end + hold
        self.gone = self.fade_out + 0.6
        self.T = round(self.gone + 0.5, 2)
        self.defs, self.body, self.overlay = [], [], []
        self.paths, self.pens, self.names = {}, {}, {}
        self.n = 0
        self.rng = random.Random(seed)

    # ---------- timing primitives ----------
    def _kt(self, points):
        pts = sorted(points, key=lambda p: p[0])
        if pts[0][0] > 0:
            pts.insert(0, (0, pts[0][1]))
        if pts[-1][0] < self.T:
            pts.append((self.T, pts[-1][1]))
        out, last = [], None
        for t, v in pts:
            t = min(t, self.T)
            if last is not None and t <= last:
                t = last + 0.002
            out.append((t, v))
            last = t
        out = [(t, v) for t, v in out if t <= self.T]
        out[-1] = (self.T, out[-1][1])
        return (';'.join(f'{t / self.T:.4f}' for t, _ in out), ';'.join(str(v) for _, v in out), len(out))

    def anim(self, attr, points, calc='linear'):
        k, v, n = self._kt(points)
        ks = f' keySplines="{";".join([SPLINE] * (n - 1))}"' if calc == 'spline' else ''
        return f'<animate attributeName="{attr}" dur="{self.T}s" repeatCount="indefinite" calcMode="{calc}" keyTimes="{k}" values="{v}"{ks}/>'

    def anim_t(self, kind, points, calc='linear'):
        k, v, n = self._kt(points)
        ks = f' keySplines="{";".join([SPLINE] * (n - 1))}"' if calc == 'spline' else ''
        return f'<animateTransform attributeName="transform" type="{kind}" dur="{self.T}s" repeatCount="indefinite" calcMode="{calc}" keyTimes="{k}" values="{v}"{ks}/>'

    def show(self, t_on, fade=0.25):
        return self.anim('opacity', [(0, 0), (t_on, 0), (t_on + fade, 1)])

    def uid(self, p='i'):
        self.n += 1
        return f'{p}{self.n}'

    # ---------- cursors ----------
    def cursor(self, key, name, color=None):
        if key not in self.paths:
            self.paths[key] = []
            self.pens[key] = []
            self.names[key] = (name, color or CURSOR_COLORS[len(self.names) % len(CURSOR_COLORS)])
        return key

    def move(self, c, t, x, y):
        self.paths[c].append((t, round(x, 1), round(y, 1)))

    # ---------- build actions ----------
    def typed(self, x, y, text, t0, size=16, fill=LIGHT, weight=400, mono=False, spacing=0,
              by=None, dur=None, length=None, caret=True):
        length = length or text_width(text, size, weight, mono)
        n = max(1, len(text))
        dur = dur if dur is not None else min(1.4, max(0.3, n * 0.032))
        t1 = t0 + dur
        cid = self.uid('c')
        steps = [(0, 0), (t0, 0)] + [(t0 + dur * i / n, round(length * i / n + 3, 1)) for i in range(1, n + 1)]
        self.defs.append(f'<clipPath id="{cid}"><rect x="{x - 2}" y="{y - size * 1.05}" height="{size * 1.45}" width="0">'
                         f'{self.anim("width", steps, "discrete")}</rect></clipPath>')
        ls = f' letter-spacing="{spacing}"' if spacing else ''
        fam = MONO if mono else SANS
        self.body.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{fill}"{ls} '
                         f'textLength="{length}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{cid})">{esc(text)}</text>')
        color = self.names[by][1] if by else RED
        if caret:
            cx = [(0, x), (t0, x)] + [(t0 + dur * i / n, round(x + length * i / n + 2, 1)) for i in range(1, n + 1)]
            self.overlay.append(f'<rect y="{y - size * 0.82}" width="2" height="{size * 0.96}" fill="{color}" opacity="0">'
                                f'{self.anim("x", cx, "discrete")}'
                                f'{self.anim("opacity", [(0, 0), (t0, 0), (t0 + .01, 1), (t1 + .35, 1), (t1 + .36, 0)], "discrete")}</rect>')
        if by:
            self.move(by, t0 - 0.02, x, y + 4)
            self.move(by, t1, x + length + 2, y + 4)
        return t1, x + length

    def box(self, x, y, w, h, t0, dur=0.8, by=None, rx=14, fill=SURF, stroke=BORDER, label=True, sw=1.5):
        t1 = t0 + dur
        color = self.names[by][1] if by else RED
        self.body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="0">{self.show(t1, 0.3)}</rect>')
        vis = self.anim('opacity', [(0, 0), (t0, 0), (t0 + .01, 1), (t1 + .15, 1), (t1 + .45, 0)])
        self.overlay.append(
            f'<rect x="{x}" y="{y}" width="0" height="0" fill="{color}" fill-opacity="0.07" stroke="{color}" stroke-width="1.5" stroke-dasharray="6 5" opacity="0">'
            f'{self.anim("width", [(0, 0), (t0, 0), (t1, w)], "spline")}{self.anim("height", [(0, 0), (t0, 0), (t1, h)], "spline")}{vis}</rect>')
        for hx, hy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            pos = [(0, f'{x} {y}'), (t0, f'{x} {y}'), (t1, f'{x + w * hx} {y + h * hy}')]
            self.overlay.append(f'<g>{self.anim_t("translate", pos, "spline")}<rect x="-4" y="-4" width="8" height="8" fill="#fff" stroke="{color}" stroke-width="1.5" opacity="0">{vis}</rect></g>')
        if label:
            txt = f'{round(w)} × {round(h)}'
            lw = len(txt) * 7.2 + 14
            tc = '#0a0a0b' if is_light(color) else '#fff'
            pos = [(0, f'{x} {y}'), (t0, f'{x} {y}'), (t1, f'{x + w / 2 - lw / 2} {y + h + 8}')]
            self.overlay.append(f'<g>{self.anim_t("translate", pos, "spline")}<g opacity="0">{vis}<rect width="{lw}" height="20" rx="4" fill="{color}"/>'
                                f'<text x="{lw / 2}" y="14" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{tc}">{txt}</text></g></g>')
        self.ripple(x, y, t0, color)
        if by:
            self.move(by, t0 - 0.02, x, y)
            self.move(by, t1, x + w, y + h)
        return t1

    def ripple(self, cx, cy, t, color=RED):
        self.overlay.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="none" stroke="{color}" stroke-width="2" opacity="0">'
                            f'{self.anim("r", [(0, 4), (t, 4), (t + .45, 20)])}'
                            f'{self.anim("opacity", [(0, 0), (t, 0), (t + .01, 1), (t + .45, 0)])}</circle>')

    def pop(self, cx, cy, inner, t, by=None, ripple=True):
        """Scale-pop arbitrary SVG markup (drawn centred on 0,0) at time t."""
        self.body.append(f'<g transform="translate({cx} {cy})"><g transform="scale(0)">'
                         f'{self.anim_t("scale", [(0, 0), (t, 0), (t + .16, 1.12), (t + .26, 1)])}{inner}</g></g>')
        if ripple:
            self.ripple(cx, cy, t, self.names[by][1] if by else RED)
        if by:
            self.move(by, t - 0.08, cx + 2, cy + 3)

    @staticmethod
    def chip_w(text, size=13):
        return round(text_width(text, size) + 26)

    def chip(self, x, y, text, t, red=False, size=13, h=28, by=None):
        w = self.chip_w(text, size)
        fill, stroke, color = ('#2a0a10', '#7a1a26', '#ff8a97') if red else ('#16161a', '#33333a', LIGHT)
        inner = (f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="{h / 2}" fill="{fill}" stroke="{stroke}"/>'
                 f'<text y="{size * 0.36}" text-anchor="middle" font-family="{SANS}" font-size="{size}" fill="{color}" '
                 f'textLength="{text_width(text, size)}" lengthAdjust="spacingAndGlyphs">{esc(text)}</text>')
        self.pop(x + w / 2, y + h / 2, inner, t, by)
        return w

    def chips(self, x, y, items, t0, max_w, by=None, step=0.15, size=13, h=28, gap=8):
        """Lay out (text, red) chips with wrapping; returns (t_end, bottom_y)."""
        cx, cy, t = x, y, t0
        for text, red in items:
            w = self.chip_w(text, size)
            if cx + w > x + max_w and cx > x:
                cx, cy = x, cy + h + gap
            self.chip(cx, cy, text, t, red, size, h, by)
            cx += w + gap
            t += step
        return t, cy + h

    def static(self, markup, t):
        self.body.append(f'<g opacity="0">{self.show(t)}{markup}</g>')

    def line(self, x1, y1, x2, y2, t0, dur=0.7, color=RED, width=2, by=None):
        t1 = t0 + dur
        self.body.append(f'<line x1="{x1}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" opacity="0">'
                         f'{self.anim("x2", [(0, x1), (t0, x1), (t1, x2)], "spline")}{self.anim("y2", [(0, y1), (t0, y1), (t1, y2)], "spline")}'
                         f'{self.anim("opacity", [(0, 0), (t0, 0), (t0 + .05, 1)])}</line>')
        if by:
            self.move(by, t0 - 0.02, x1, y1)
            self.move(by, t1, x2, y2)
            self.pens[by].append((t0 - 0.05, t1 + 0.05))
        return t1

    def guides(self, x, y, t_on, t_off, color=WHITE):
        op = self.anim('opacity', [(0, 0), (t_on, 0), (t_on + .1, .7), (t_off, .7), (t_off + .3, 0)])
        self.overlay.append(f'<line x1="0" x2="{self.w}" y1="{y}" y2="{y}" stroke="{color}" stroke-dasharray="4 4" opacity="0">{op}</line>')
        self.overlay.append(f'<line x1="{x}" x2="{x}" y1="{y - 30}" y2="{y + 70}" stroke="{color}" stroke-dasharray="4 4" opacity="0">{op}</line>')

    def heading(self, x, y, kicker, title, t0, by, size=40):
        """Kicker + big title typed along ruler guides."""
        t, _ = self.typed(x, y - size - 8, kicker, t0, size=15, fill=RED, weight=500, mono=True, spacing=1, by=by)
        self.guides(x, y - size * 0.72, t, t + 1.4)
        t, _ = self.typed(x, y, title, t + 0.15, size=size, fill=WHITE, weight=800, by=by, dur=min(1.0, 0.05 * len(title)))
        return t

    # ---------- output ----------
    def _render_cursors(self):
        out = []
        for key, pts in self.paths.items():
            if not pts:
                continue
            name, color = self.names[key]
            pts = sorted(pts, key=lambda p: p[0])
            t_first, fx, fy = pts[0]
            ex, ey = (fx, -30) if fy < self.h / 2 else (fx, self.h + 30)
            t_enter = max(0.05, t_first - 0.5)
            path = [(t_enter, ex, ey)] + pts
            lt, lx, ly = path[-1]
            for k in range(2):
                lt = min(self.fade_out, lt + 1.6)
                lx = min(self.w - 110, max(20, lx + self.rng.uniform(-60, 60)))
                ly = min(self.h - 40, max(20, ly + self.rng.uniform(-35, 35)))
                path.append((lt, round(lx, 1), round(ly, 1)))
            path.append((self.fade_out + 0.4, lx, ly))
            light = is_light(color)
            tc = '#0a0a0b' if light else '#fff'
            stroke = '#0a0a0b' if light else '#fff'
            lw = round(text_width(name, 11, 700) + 16)
            pos = [(t, f'{x} {y}') for t, x, y in path]
            arrow_op = pen = ''
            if self.pens[key]:
                a_pts, p_pts = [(0, 1)], [(0, 0)]
                for a, b in self.pens[key]:
                    a_pts += [(a, 1), (a + .01, 0), (b, 0), (b + .01, 1)]
                    p_pts += [(a, 0), (a + .01, 1), (b, 1), (b + .01, 0)]
                arrow_op = self.anim('opacity', a_pts, 'discrete')
                pen = (f'<path d="{PEN}" transform="translate(-2.5 -19.5)" fill="{color}" stroke="{stroke}" stroke-width="1.4" '
                       f'stroke-linejoin="round" opacity="0">{self.anim("opacity", p_pts, "discrete")}</path>')
            out.append(
                f'<g>{self.anim_t("translate", pos, "spline")}<g opacity="0">{self.show(t_enter, 0.2)}'
                f'<path d="{ARROW}" transform="translate(-2 -1.5)" fill="{color}" stroke="{stroke}" stroke-width="1.4" stroke-linejoin="round" filter="url(#sh)">{arrow_op}</path>'
                f'{pen}<rect x="14" y="17" width="{lw}" height="20" rx="6" fill="{color}"/>'
                f'<text x="{14 + lw / 2}" y="31" text-anchor="middle" font-family="{SANS}" font-size="11" font-weight="700" fill="{tc}">{esc(name)}</text>'
                f'</g></g>')
        return out

    def render(self, title, desc, glow=(0.85, 0.0)):
        fade = self.anim('opacity', [(0, 1), (self.fade_out, 1), (self.gone, 0), (self.T - 0.01, 0)])
        W, H = self.w, self.h
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">{esc(title)}</title>
<desc id="d">{esc(desc)}</desc>
<defs>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#ffffff" fill-opacity="0.07"/></pattern>
<radialGradient id="glow" cx="{glow[0]}" cy="{glow[1]}" r="0.75"><stop offset="0" stop-color="{RED}" stop-opacity="0.2"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<filter id="sh" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.6"/></filter>
{''.join(self.defs)}
</defs>
<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#glow)"/>
<g>{fade}
{''.join(self.body)}
{''.join(self.overlay)}
{''.join(self._render_cursors())}
</g>
</svg>
'''
