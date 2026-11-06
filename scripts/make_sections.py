"""Generate the animated profile sections: about, stack, experience, projects.

Usage: python3 scripts/make_sections.py assets/
"""
import os
import sys

from swarm_svg import (Scene, text_width, esc, RED, WHITE, PINK, ROSE, DEEP, CORAL,
                       MUTED, LIGHT, MONO, SANS)

OUT = sys.argv[1] if len(sys.argv) > 1 else 'assets'
os.makedirs(OUT, exist_ok=True)


def save(name, svg):
    with open(os.path.join(OUT, name), 'w') as f:
        f.write(svg)
    print('wrote', name, f'{len(svg) // 1024} KB')


def diamond(color=RED, s=6):
    return f'<rect x="{-s / 2}" y="{-s / 2}" width="{s}" height="{s}" rx="1" fill="{color}" transform="rotate(45)"/>'


# ------------------------------------------------------------------ ABOUT
def about():
    rows = [
        ('ROLE', 'Senior Software Engineer (Full Stack) · 8 years of experience, since 2018'),
        ('NOW', 'Team Lead at Turing, building LLM & coding-agent evaluation tooling'),
        ('FOCUS', 'SWE-Bench+ · function calling · code interpreter · Swift ⇄ Python · MCP'),
        ('STACK', 'Node.js (NestJS) · React · Vue · Python · Laravel · Docker · PostgreSQL · AWS'),
        ('BASED', 'Lahore, Pakistan · Remote, full time · 4+ hrs daily US overlap (EST / PST)'),
        ('WORKFLOW', 'Cursor · GitHub Copilot · Claude Code, every day'),
    ]
    H = 196 + len(rows) * 48 + 40
    s = Scene(1200, H, build_end=2.4 + len(rows) * 0.42 + 1.5)
    cs = [s.cursor(k, n) for k, n in (('a', 'Node'), ('b', 'React'), ('c', 'Python'), ('d', 'Docker'))]
    s.box(30, 24, 1140, H - 48, 0.4, 0.9, by=cs[0])
    s.heading(80, 140, '01 / ABOUT', 'About me', 1.2, by=cs[1])
    y, t = 200, 2.4
    for i, (label, text) in enumerate(rows):
        c = cs[(i + 2) % 4]
        s.pop(86, y - 6, diamond(), t, by=c, ripple=False)
        t1, _ = s.typed(104, y, label, t + 0.1, size=14, fill=RED, weight=600, mono=True, spacing=1, by=c, dur=0.25, caret=False)
        s.typed(240, y, text, t1 + 0.05, size=19, fill=LIGHT, by=c, dur=1.15)
        y += 48
        t += 0.42
    save('about.svg', s.render('About Imran Rasheed', ' · '.join(f'{a}: {b}' for a, b in rows)))


# ------------------------------------------------------------------ STACK
STACK = [
    ('AI / LLM & Agents', [('SWE-Bench+', 1), ('MCP', 1), ('Function calling', 1), ('Code interpreter', 1),
                           ('SFT & RLHF data', 0), ('Agent eval harnesses', 0), ('Ollama', 0), ('Gemini', 0),
                           ('Claude Code', 0), ('Copilot', 0)]),
    ('Languages', [('JavaScript · 8y', 1), ('PHP · 8y', 0), ('SQL · 8y', 0), ('TypeScript · 6y', 1), ('Python · 5y', 1),
                   ('Java · 2y', 0), ('Swift · 2y', 0), ('C++', 0), ('Bash', 0)]),
    ('Backend', [('Node.js', 1), ('NestJS', 1), ('Express', 0), ('Laravel', 1), ('FastAPI', 0), ('GraphQL', 0),
                 ('REST', 0), ('Microservices', 0), ('JWT', 0), ('OAuth 2.0', 0), ('RBAC', 0)]),
    ('Frontend', [('React', 1), ('Vue', 1), ('Next.js', 0), ('Vite', 0), ('Tailwind', 0), ('Redux', 0), ('Vuex', 0),
                  ('Browser extensions', 0)]),
    ('Data & Caching', [('PostgreSQL', 1), ('MySQL', 0), ('MongoDB', 0), ('Redis', 1), ('Prisma', 0), ('Sequelize', 0)]),
    ('DevOps & Cloud', [('Docker', 1), ('Compose', 0), ('AWS', 1), ('Azure', 0), ('GitHub Actions', 0),
                        ('Prometheus', 0), ('Nginx', 0), ('CI/CD', 0)]),
]


def chip_rows(items, max_w, size=13, gap=8):
    rows, cx = 1, 0
    for text, _ in items:
        w = Scene.chip_w(text, size)
        if cx + w > max_w and cx > 0:
            rows, cx = rows + 1, 0
        cx += w + gap
    return rows


def stack():
    colw, gap, x0, top = 366, 21, 30, 170
    inner = colw - 48
    heights = [86 + chip_rows(items, inner) * 36 for _, items in STACK]
    row_h = [max(heights[0:3]), max(heights[3:6])]
    H = top + row_h[0] + gap + row_h[1] + 30
    s = Scene(1200, H, build_end=5.6)
    names = ['Node', 'React', 'Python', 'Docker', 'Laravel', 'Redis']
    s.cursor('h', 'Vue')
    s.heading(40, 120, '02 / STACK', 'Tech stack', 0.4, by='h')
    for i, (title, items) in enumerate(STACK):
        c = s.cursor(f'k{i}', names[i])
        col, row = i % 3, i // 3
        x = x0 + col * (colw + gap)
        y = top + (row_h[0] + gap if row else 0)
        t = 0.9 + i * 0.22
        t = s.box(x, y, colw, row_h[row], t, 0.7, by=c, label=(i % 2 == 0))
        s.pop(x + 30, y + 40, diamond(), t + 0.1, by=c, ripple=False)
        t, _ = s.typed(x + 46, y + 47, title, t + 0.15, size=20, fill=WHITE, weight=700, by=c, dur=0.45)
        s.chips(x + 24, y + 68, items, t + 0.1, inner, by=c, step=0.14)
    desc = '; '.join(f'{t}: ' + ', '.join(n for n, _ in items) for t, items in STACK)
    save('stack.svg', s.render('Tech stack', desc, glow=(0.1, 0.0)))


# ------------------------------------------------------------------ EXPERIENCE
JOBS = [
    ('Senior Full Stack Engineer / Team Lead', 'Turing · Remote', 'Jul 2024 — Present', True,
     ['SWE-Bench+ Tooling', 'SWE-Bench Data', 'Penguin Code Translation', 'Penguin Code Interpreter', 'Penguin GUI',
      'Penguin Function Calling', 'MCP', 'Microsoft Code Evaluation', 'Microsoft Codeforces']),
    ('Full Stack Developer (Frontend Focused)', 'Coregenion GmbH · Remote', 'Feb 2023 — Jun 2024', False, []),
    ('Full Stack Developer', 'Glorek · Lahore, Pakistan', 'Jun 2021 — Dec 2022', False, []),
    ('Backend Engineer (APIs & Cloud Services)', 'ITRID Technologies · Lahore, Pakistan', 'Mar 2018 — May 2021', False, []),
]


def experience():
    x, w, top, gap = 120, 1050, 170, 16
    heights = []
    for job in JOBS:
        h = 100
        if job[4]:
            h += chip_rows([(p, 0) for p in job[4]], w - 56, size=12, gap=6) * 32 + 6
        heights.append(h)
    H = top + sum(heights) + gap * (len(JOBS) - 1) + 40
    s = Scene(1200, H, build_end=5.4)
    s.cursor('h', 'Node')
    s.cursor('pen', 'Docker', ROSE)
    s.heading(40, 120, '03 / EXPERIENCE', "Where I've built", 0.4, by='h')
    s.line(72, top + 10, 72, H - 50, 0.9, 1.6, by='pen')
    names = [('React', WHITE), ('Python', PINK), ('Laravel', DEEP), ('Vue', CORAL)]
    y = top
    for i, (role, co, when, current, programs) in enumerate(JOBS):
        c = s.cursor(f'j{i}', *names[i])
        h = heights[i]
        t = 1.1 + i * 0.45
        s.pop(72, y + 44, f'<circle r="9" fill="#2a0a10" stroke="{RED}" stroke-width="2"/><circle r="3.5" fill="{RED if current else MUTED}"/>',
              t, by=c)
        t = s.box(x, y, w, h, t + 0.15, 0.6, by=c, fill='#160a0d' if current else '#131316',
                  stroke='#5c1520' if current else '#2a2a30', label=(i == 0))
        cw = Scene.chip_w(when, 13)
        s.chip(x + w - 28 - cw, y + 24, when, t + 0.1, red=current, by=c)
        t, _ = s.typed(x + 28, y + 50, role, t + 0.2, size=22, fill=WHITE, weight=700, by=c, dur=0.7)
        t, _ = s.typed(x + 28, y + 78, co, t + 0.05, size=16, fill=RED, weight=500, by=c, dur=0.45)
        if programs:
            s.chips(x + 28, y + 96, [(p, 0) for p in programs], t + 0.1, w - 56, by=c, step=0.11, size=12, h=26, gap=6)
        y += h + gap
    desc = '; '.join(f'{r} at {c} ({w})' for r, c, w, _, _ in JOBS)
    save('experience.svg', s.render('Experience', desc, glow=(0.9, 0.1)))


# ------------------------------------------------------------------ PROJECTS
def icon(label):
    return (f'<rect x="-30" y="-30" width="60" height="60" rx="14" fill="#5c0812" stroke="{RED}" stroke-opacity="0.5"/>'
            f'<text y="5" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="600" fill="{RED}">{esc(label)}</text>')


def featured():
    H = 450
    s = Scene(1200, H, build_end=5.0)
    s.cursor('h', 'Node')
    for k, n in (('a', 'React'), ('b', 'Python'), ('c', 'Docker')):
        s.cursor(k, n)
    s.heading(40, 120, '04 / PROJECTS', 'Featured work', 0.4, by='h')
    t = s.box(30, 160, 1140, 262, 0.9, 0.9, by='a', fill='#160a0d', stroke='#5c1520')
    s.pop(100, 230, icon('SRJ'), t + 0.1, by='a')
    s.chip(150, 216, '● Live product', t + 0.3, red=True, by='a')
    link = 'seekremotejobs.com ↗'
    lw = text_width(link, 16, mono=True)
    s.typed(1130 - lw, 236, link, t + 0.4, size=16, fill=RED, mono=True, by='c', dur=0.6)
    t2, _ = s.typed(70, 310, 'SeekRemoteJobs: AI-Powered Remote Job Aggregation', t + 0.4, size=30, fill=WHITE, weight=800, by='b', dur=1.0)
    t3, _ = s.typed(70, 344, 'Aggregates postings from 40+ top tech career pages into one searchable interface, with AI', t2 + 0.05, size=17, fill=MUTED, by='b', dur=0.9)
    s.typed(70, 368, 'resume parsing, tailoring, ATS scoring, cover letters and job matching.', t3 + 0.02, size=17, fill=MUTED, by='b', dur=0.7)
    s.chips(70, 384, [(n, r) for n, r in (('React + Vite', 1), ('Node.js', 1), ('PostgreSQL', 1), ('Puppeteer', 0), ('Gemini', 0),
                                           ('Groq', 0), ('OAuth 2.0', 0), ('Docker Compose', 0), ('Nginx', 0))],
            t2 + 0.2, 1060, by='c', step=0.14, size=12, h=26, gap=6)
    save('project-seekremotejobs.svg', s.render(
        'SeekRemoteJobs: AI-Powered Remote Job Aggregation',
        'Live full-stack platform aggregating 40+ tech career pages with AI resume tools. React, Vite, Node.js, PostgreSQL, Puppeteer, Gemini, Groq, Docker.'))


SMALL = [
    ('project-modelvault.svg', 'AI', 'Streaming · Ollama', 'ModelVault MiniVault API',
     ['LLM prompt/response API with real-time', 'token streaming, local LLMs via Ollama,', 'Prometheus metrics and a Python CLI.'], 'View on GitHub ↗'),
    ('project-securenest.svg', 'VPN', 'WireGuard', 'SecureNest VPN',
     ['Backend for a secure VPN service:', 'network routing, handshake validation', 'and secure infrastructure bridges.'], 'View on GitHub ↗'),
    ('project-motion-detector.svg', 'C++', 'Computer vision', 'Motion Detector',
     ['Low-level computer-vision utility in', 'C++ for real-time motion detection with', 'careful memory management.'], 'View on GitHub ↗'),
    ('project-portfolio.svg', 'IR', 'Vanilla JS', 'Swarm Portfolio',
     ['This red & black portfolio, rebuilt live', 'by a swarm of cursors on every visit.', 'No framework, no build step.'], 'Open live site ↗'),
]


def small(fname, ic, tag, title, lines, cta, seed):
    W, H = 600, 340
    s = Scene(W, H, build_end=4.2, seed=seed)
    a, b = s.cursor('a', ['Node', 'Vue', 'Redis', 'Laravel'][seed % 4]), s.cursor('b', ['React', 'Python', 'Docker', 'NestJS'][seed % 4])
    s.names['a'] = (s.names['a'][0], [RED, DEEP, CORAL, RED][seed % 4])
    s.names['b'] = (s.names['b'][0], [WHITE, PINK, ROSE, WHITE][seed % 4])
    t = s.box(16, 16, W - 32, H - 32, 0.3, 0.8, by=a)
    s.pop(80, 80, icon(ic), t + 0.1, by=a)
    tw = Scene.chip_w(tag, 13)
    s.chip(W - 48 - tw, 66, tag, t + 0.3, red=True, by=a)
    t2, _ = s.typed(50, 160, title, t + 0.3, size=28, fill=WHITE, weight=800, by=b, dur=0.7)
    y = 198
    for ln in lines:
        t2, _ = s.typed(50, y, ln, t2 + 0.02, size=18, fill=MUTED, by=b, dur=0.55)
        y += 28
    s.typed(50, 298, cta, t2 + 0.1, size=16, fill=RED, weight=500, mono=True, by=a, dur=0.5)
    save(fname, s.render(title, ' '.join(lines)))


if __name__ == '__main__':
    about()
    stack()
    experience()
    featured()
    for i, p in enumerate(SMALL):
        small(*p, seed=i)
