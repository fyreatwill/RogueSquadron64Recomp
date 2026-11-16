#!/usr/bin/env python3
"""s7431 class CN: default-on stderr volume per tag, per 10 s window, from a timestamped runlog
(lines "<ms>\t<text>" written by tools/s7431_stderr_volume.sh).
Verdicts: H-perframe = a non-control tag present in every one of the last W windows at >= MINR lines/window
(flat, unbudgeted in flight); H-burst = a tag writing > BURST bytes inside one second; else H-capped.
Positive control: the planted CONTROL tag (default [fbhash, ROGUESQ_FB_HASH=1, one line per frame) must classify
persistent, else exit 3. Exit 0 H-capped, 1 found, 3 control fail.
usage: s7431_stderr_volume.py RUNLOG [--control '[fbhash'] [--last 6] [--minr 5] [--burst 102400] [--from-s T]"""
import re, sys, argparse, collections
ap = argparse.ArgumentParser(); ap.add_argument('log'); ap.add_argument('--control', default='[fbhash')
ap.add_argument('--last', type=int, default=6); ap.add_argument('--minr', type=int, default=5)
ap.add_argument('--burst', type=int, default=102400); ap.add_argument('--top', type=int, default=20)
ap.add_argument('--capped', type=float, default=None, help='expect the s7431 cap at this lines/s rate: control = planted tag fired but is held to <= rate*10+2 lines per window; pass iff flight non-control rate < --maxflight B/10s')
ap.add_argument('--maxflight', type=int, default=30000)
a = ap.parse_args()
def tag(t):
    m = re.match(rb'\s*(\[[^\]\s#]{1,40})', t)
    if m: return m.group(1).decode('latin1')
    m = re.match(rb'\s*([A-Za-z_][\w.\-]{0,24})', t)
    return m.group(1).decode('latin1') if m else '<other>'
win = collections.defaultdict(lambda: collections.Counter()); wl = collections.defaultdict(lambda: collections.Counter())
sec = collections.defaultdict(lambda: collections.Counter()); tot = collections.Counter(); totl = collections.Counter()
first = {}; tmax = 0; flight = None
for raw in open(a.log, 'rb'):
    ms, _, t = raw.partition(b'\t')
    try: ms = int(ms)
    except ValueError: continue
    k = tag(t); n = len(t); w = ms // 10000
    win[k][w] += n; wl[k][w] += 1; sec[k][ms // 1000] += n; tot[k] += n; totl[k] += 1; first.setdefault(k, ms); tmax = max(tmax, ms)
    if flight is None and (t.startswith(b'[initMission]') or (t.startswith(b'[autopilot] fire') and re.search(rb' t=(\d+)', t) and int(re.search(rb' t=(\d+)', t).group(1)) >= 95)):
        flight = ms
W = tmax // 10000; last = list(range(W - a.last, W))  # complete windows only
def persistent(k): return all(wl[k][w] >= a.minr for w in last)
print(f"run {tmax/1000:.0f}s, flight_from={flight/1000 if flight is not None else None}s, total {sum(tot.values())} B, last windows {last}")
print(f"{'bytes':>9} {'lines':>7} {'lastW_B/10s':>11} {'maxsec_B':>9} first_s  tag")
for k, v in tot.most_common(a.top):
    lb = sum(win[k][w] for w in last) // max(1, len(last))
    print(f"{v:9d} {totl[k]:7d} {lb:11d} {max(sec[k].values()):9d} {first[k]/1000:7.1f}  {k}{'  PERSISTENT' if persistent(k) else ''}")
ctl = [k for k in tot if k.startswith(a.control)]
fr = sum(win[k][w] for k in tot if not k.startswith(a.control) for w in last) // max(1, len(last))
print(f"FLIGHT_RATE {fr} B/10s non-control (last {len(last)} windows); stderr-cap lines: {totl.get('[stderr-cap', 0)}")
if a.capped is not None:
    cl = max((max(wl[k][w] for w in last) for k in ctl), default=-1)
    ok = cl >= 0 and totl[ctl[0]] > 200 and cl <= a.capped * 10 + 2
    print(f"CONTROL {'PASS' if ok else 'FAIL'} capped arm: {a.control} total {[totl[k] for k in ctl]} max lines/window in flight {cl}")
    if not ok: sys.exit(3)
    print(f"VERDICT {'H-capped-by-s7431' if fr < a.maxflight else 'H-still-loud'}"); sys.exit(0 if fr < a.maxflight else 1)
ok = any(persistent(k) for k in ctl)
print(f"CONTROL {'PASS' if ok else 'FAIL'} ({a.control}: {[(k, totl[k]) for k in ctl]})")
if not ok: sys.exit(3)
per = [k for k in tot if persistent(k) and not k.startswith(a.control)]
bur = [k for k in tot if max(sec[k].values()) > a.burst and not k.startswith(a.control)]
for k in per: print(f"PERFRAME {k} {sum(wl[k][w] for w in last)//len(last)} lines/10s {sum(win[k][w] for w in last)//len(last)} B/10s")
for k in bur: print(f"BURST {k} max {max(sec[k].values())} B in 1 s at t={max(sec[k], key=sec[k].get)}s")
v = 'H-perframe' if per else ('H-burst' if bur else 'H-capped')
print(f"VERDICT {v}{'+H-burst' if per and bur else ''}"); sys.exit(0 if v == 'H-capped' else 1)
