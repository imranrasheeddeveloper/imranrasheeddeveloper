"""Animated contribution chart: a swarm of git-command cursors paints the
last year of GitHub contributions in red, then types out the stats.

Usage: GITHUB_TOKEN=... python3 scripts/make_contrib.py assets/contrib.svg [login]
Locally it falls back to `gh auth token`.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request

from swarm_svg import Scene, text_width, RED, WHITE, PINK, ROSE, DEEP, CORAL, MUTED, MONO, SANS

OUT = sys.argv[1] if len(sys.argv) > 1 else 'assets/contrib.svg'
LOGIN = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('GH_LOGIN', 'imranrasheeddeveloper')

QUERY = '''query($login:String!){user(login:$login){contributionsCollection{
  contributionCalendar{totalContributions weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}'''

LEVEL = {'NONE': 0, 'FIRST_QUARTILE': 1, 'SECOND_QUARTILE': 2, 'THIRD_QUARTILE': 3, 'FOURTH_QUARTILE': 4}
FILL = ['#17171b', '#4a0a14', '#8f1223', '#d0142f', '#ff2d46']


def token():
    tok = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if tok:
        return tok
    return subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()


def fetch():
    body = json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode()
    req = urllib.request.Request('https://api.github.com/graphql', data=body, headers={
        'Authorization': f'bearer {token()}', 'Content-Type': 'application/json', 'User-Agent': 'swarm-contrib'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if 'errors' in data:
        raise SystemExit(f'GraphQL error: {data["errors"]}')
    return data['data']['user']['contributionsCollection']['contributionCalendar']


def stats(days):
    active = [d for d in days if d['contributionCount'] > 0]
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d['contributionCount'] > 0 else 0
        longest = max(longest, cur)
    best = max((d['contributionCount'] for d in days), default=0)
    return len(active), longest, best


def build(cal):
    weeks = cal['weeks']
    days = [d for w in weeks for d in w['contributionDays']]
    total = cal['totalContributions']
    active, longest, best = stats(days)

    W, H = 1200, 430
    cell, gap = 15, 4
    pitch = cell + gap
    gx = (W - len(weeks) * pitch + gap) // 2 + 20
    gy = 176
    s = Scene(W, H, build_end=6.6)

    names = [('git push', RED), ('git pull', WHITE), ('git commit', PINK), ('git merge', ROSE), ('git rebase', DEEP), ('git fetch', CORAL)]
    cs = [s.cursor(f'g{i}', n, c) for i, (n, c) in enumerate(names)]
    s.cursor('h', 'git log', WHITE)
    s.heading(40, 118, '05 / ACTIVITY', 'Contributions, built live', 0.3, by='h')

    # Empty grid drawn as one selection box, then all empty cells fade in.
    grid_w, grid_h = len(weeks) * pitch - gap, 7 * pitch - gap
    t_grid = s.box(gx - 10, gy - 10, grid_w + 20, grid_h + 20, 0.6, 0.8, by=cs[0], fill='none', stroke='none', label=True)
    empty = []
    for wi, w in enumerate(weeks):
        for d in w['contributionDays']:
            empty.append(f'<rect x="{gx + wi * pitch}" y="{gy + d["weekday"] * pitch}" width="{cell}" height="{cell}" rx="3" fill="{FILL[0]}" stroke="#222227"/>')
    s.static(''.join(empty), t_grid)

    # Month + weekday labels
    labels, last_month = [], None
    for wi, w in enumerate(weeks):
        m = dt.date.fromisoformat(w['contributionDays'][0]['date']).strftime('%b')
        if m != last_month and wi < len(weeks) - 2:
            labels.append(f'<text x="{gx + wi * pitch}" y="{gy - 14}" font-family="{MONO}" font-size="11" fill="{MUTED}">{m}</text>')
            last_month = m
    for i, dname in ((1, 'Mon'), (3, 'Wed'), (5, 'Fri')):
        labels.append(f'<text x="{gx - 12}" y="{gy + i * pitch + 11}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">{dname}</text>')
    s.static(''.join(labels), t_grid + 0.1)

    # Active cells: split the year into one band of weeks per cursor; each
    # cursor zig-zags through its band and pops every active cell it reaches.
    active_cells = [(wi, d) for wi, w in enumerate(weeks) for d in w['contributionDays'] if d['contributionCount'] > 0]
    band = max(1, -(-len(weeks) // len(cs)))
    t_paint0, budget = t_grid + 0.2, 3.6
    for ci, c in enumerate(cs):
        mine = [(wi, d) for wi, d in active_cells if ci * band <= wi < (ci + 1) * band]
        mine.sort(key=lambda p: (p[0], p[1]['weekday'] if p[0] % 2 == 0 else -p[1]['weekday']))
        if not mine:
            s.move(c, t_paint0 + ci * 0.15, gx + ci * band * pitch + 30, gy + grid_h + 40)
            continue
        step = min(0.24, budget / len(mine))
        t = t_paint0 + ci * 0.12
        for wi, d in mine:
            lvl = LEVEL.get(d['contributionLevel'], 1) or 1
            cx, cy = gx + wi * pitch + cell / 2, gy + d['weekday'] * pitch + cell / 2
            glow = f'<rect x="-10" y="-10" width="20" height="20" rx="5" fill="{RED}" opacity="0.25"/>' if lvl == 4 else ''
            inner = f'{glow}<rect x="{-cell / 2}" y="{-cell / 2}" width="{cell}" height="{cell}" rx="3" fill="{FILL[lvl]}"/>'
            s.pop(cx, cy, inner, t, by=c, ripple=(lvl >= 3))
            t += step

    # Legend
    lx = gx + grid_w - 5 * pitch - 40
    legend = [f'<text x="{lx - 8}" y="{gy + grid_h + 26}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">Less</text>']
    for i, f in enumerate(FILL):
        legend.append(f'<rect x="{lx + i * pitch}" y="{gy + grid_h + 15}" width="{cell}" height="{cell}" rx="3" fill="{f}" stroke="#222227"/>')
    legend.append(f'<text x="{lx + 5 * pitch + 4}" y="{gy + grid_h + 26}" font-family="{MONO}" font-size="11" fill="{MUTED}">More</text>')
    s.static(''.join(legend), t_grid + 0.3)

    # Stats row
    t_stats = t_paint0 + budget + 0.3
    items = [(f'{total:,}', 'contributions · last year'), (f'{active}', 'active days'),
             (f'{longest}', 'day longest streak'), (f'{best}', 'on the busiest day')]
    sx, sy, sw = gx, gy + grid_h + 72, (grid_w - 30) / 4
    for i, (num, label) in enumerate(items):
        c = cs[i]
        x = sx + i * sw
        t1, _ = s.typed(x, sy, num, t_stats + i * 0.18, size=36, fill=RED, weight=800, by=c, dur=0.35)
        s.typed(x + 2, sy + 26, label, t1, size=14, fill=MUTED, mono=True, by=c, dur=0.5, caret=False)

    desc = f'{total} contributions in the last year · {active} active days · longest streak {longest} days · best day {best}.'
    return s.render(f'GitHub contributions of {LOGIN}', desc, glow=(0.5, 0.0))


if __name__ == '__main__':
    svg = build(fetch())
    os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
    with open(OUT, 'w') as f:
        f.write(svg)
    print('wrote', OUT, f'{len(svg) // 1024} KB')
