# s7252: tag every session's run window with the host power state (AC vs battery Low Power Mode).
# Why: s7249-s7251 found that battery = pmset powermode 1 (Low Power Mode) costs x1.36-1.44 CPU per gfx task, so any
# ABSOLUTE timing verdict (ms/task, flat 30/s, headroom, presents/s) measured on battery is not an AC verdict.
# Same-run A/B deltas between arms are still valid (both arms share the clock cap), absolute thresholds are not.
# Source of power state: `pmset -g log` ("Using AC" / "Using Batt" on Assertions/Sleep/Wake lines; retains ~1 week).
# Session window: (previous `iter:` commit time, this session's first `iter: sNNNN` commit time].
# s7252 CAVEAT (measured): battery is NECESSARY, not sufficient. 11-09 18:58 battery (s7046 H12ke12) vs 11-09 16:11 AC (s7042
#   S42L12), same L12 16:9 dd6 recipe: CPU/task ratio 1.00-1.05 = no throttle, while 11-12 afternoon battery read x1.36-1.44.
#   So a tagged session's absolute timing only falls if tools/s7251_clock_ratio.py on a same-recipe AC pair reads >~1.2.
# usage: python3 tools/s7252_power_tag.py [--all] [--since 2026-11-06]
#   default prints sessions with battery overlap whose PORTING-STATE entry carries a timing verdict.
import re, subprocess, sys
from datetime import datetime

def ts(s): return datetime.strptime(s[:19], '%Y-%m-%d %H:%M:%S')

def power_timeline():
    out = subprocess.run(['pmset', '-g', 'log'], capture_output=True, text=True).stdout
    ev = []
    for l in out.splitlines():
        m = re.match(r'(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) [-+]\d{4} .*Using (AC|Batt)', l)
        if m: ev.append((ts(m[1]), m[2]))
    ev.sort()
    return ev

def state_overlap(ev, a, b):
    """seconds of [a,b] on Batt / total, using the last known state before each point; None if before log start."""
    if not ev or a < ev[0][0]: return None
    st = [s for t, s in ev if t <= a][-1]
    t0, batt = a, 0.0
    for t, s in ev:
        if t <= a: continue
        if t >= b: break
        if st == 'Batt': batt += (t - t0).total_seconds()
        t0, st = t, s
    if st == 'Batt': batt += (b - t0).total_seconds()
    tot = max((b - a).total_seconds(), 1)
    return batt / tot

TIMING = re.compile(r'ms per gfx task|ms/task|flat[- ]30|headroom|presents/s|sd_cpu|\d+(\.\d+)? ms task|holds? 60|fps\b|/s on screen|gap', re.I)

def main():
    since = '2026-11-06'
    if '--since' in sys.argv: since = sys.argv[sys.argv.index('--since') + 1]
    show_all = '--all' in sys.argv
    ev = power_timeline()
    log = subprocess.run(['git', 'log', '--reverse', f'--since={since}', '--format=%ci|%s'], capture_output=True, text=True).stdout
    commits = [(ts(l[:19]), l.split('|', 1)[1]) for l in log.splitlines() if '|' in l]
    first = {}; prev_t = None; win = {}
    for t, s in commits:
        m = re.match(r'iter: s(\d+)', s)
        if m and m[1] not in first and prev_t is not None:
            first[m[1]] = t; win[m[1]] = (prev_t, t)
        prev_t = t
    ps = open('PORTING-STATE.md', encoding='utf-8', errors='replace').read()
    ent = {}
    for m in re.finditer(r'^## Session (\d+) .*?(?=^## Session |\Z)', ps, re.M | re.S): ent[m[1]] = m[0]
    n_b = 0
    print('session  window(start..end)             batt  timing  title')
    for sid, (a, b) in win.items():
        f = state_overlap(ev, a, b)
        body = ent.get(sid, '')
        tim = len(TIMING.findall(body))
        title = body.split('\n', 1)[0][len(f'## Session {sid} '):][:90]
        if f is None: tag = '  ?'
        else: tag = f'{f:4.2f}'
        if f and f > 0: n_b += 1
        if show_all or (f and f > 0 and tim):
            print(f's{sid:5} {a:%m-%d %H:%M}..{b:%H:%M}  {tag}  {tim:5}   {title}')
    print(f'# {len(win)} sessions since {since}; {n_b} overlap battery (Low Power Mode); log starts {ev[0][0] if ev else "?"}')

if __name__ == '__main__':
    main()
