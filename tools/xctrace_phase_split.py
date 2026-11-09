#!/usr/bin/env python3
"""s7021: split an xctrace Time Profiler recording of the gfx thread by WIDEWIN=tog3 (or tog) phase, so the RSP blocks and host
functions whose cost GROWS with the cap are named (tools/xctrace_ucode_blocks.py mixes all phases).

Clock alignment, two lines:
 1. coarse prior: (wall, mach) pairs taken by scratch/s7021/clk.py just before xctrace starts + the trace TOC start-date
    -> mach at trace t=0 (error = xctrace attach latency, ~0.1-2 s).
 2. refine: the G1E_TL ring (steady_us, mapped to mach by the run's [s7010-clk] anchor) gives every gfx task's busy interval
    (code 6 task start -> code 7 ucode exit). The xctrace gfx-thread samples that sit inside factor5_ucode* give the same
    signal at 1 ms. Cross-correlate the two over +-WIN ms around the prior; the peak is the offset. Printed: peak score, the
    best score more than 8 ms away (must be clearly lower, else the alignment is ambiguous) and the 0.5 s-shifted score.
Per sample: mach second -> phase (sec % 3 for --phases 3; xor8 for 2, = rs64_tog_odd). Samples within --guard-ms of a
second flip are dropped. Output per phase: covered seconds, gfx-thread ms/s total, in-ucode ms/s, then per RSP block (self,
incl) and per host leaf function: ms/s per phase and delta (mean of p1..pn) - p0. Positive control: the in-ucode-incl
delta (ms/s) / fps must match g5e_cost_by_parity.py's rsp delta (ms/frame) on the same run.
usage: xctrace_phase_split.py <tp.xml> <toc.xml> <xc.txt> <tl.bin.pid> <log-with-anchor> <binary> <ucode.c> <arm.o>
       [--thread 'SP Task'] [--phases 3] [--guard-ms 60] [--win-ms 3000] [--top 25] [--offset-ms X (skip refine)]"""
import re, sys, subprocess, collections, bisect, struct, argparse, datetime
import xml.etree.ElementTree as ET
ap = argparse.ArgumentParser()
for k in ('xml', 'toc', 'xc', 'tl', 'log', 'binary', 'csrc', 'obj'): ap.add_argument(k)
ap.add_argument('--thread', default='Gfx Thread'); ap.add_argument('--phases', type=int, default=3)
ap.add_argument('--guard-ms', type=float, default=60.0); ap.add_argument('--win-ms', type=int, default=3000)
ap.add_argument('--top', type=int, default=25); ap.add_argument('--offset-ms', type=float, default=None)
ap.add_argument('--shift-ms', type=float, default=0.0, help='control: shift the phase clock after alignment')
a = ap.parse_args()

# ---------- samples: (t_ns, frame-id list) for the chosen thread
frames, bts, threads, stimes = {}, {}, {}, {}
load = None; samp = []
for ev, el in ET.iterparse(a.xml, events=("end",)):
    if el.tag == "frame":
        if "ref" in el.attrib: continue
        frames[el.get("id")] = (el.get("name") or "?", int(el.get("addr"), 16))
        b = el.find("binary")
        if b is not None and b.get("name") == "RogueSquadron64Recomp" and load is None: load = b.get("load-addr")
    elif el.tag == "row":
        stel = el.find("sample-time")
        if stel.get("ref"): t = stimes[stel.get("ref")]
        else: t = int(stel.text); stimes[stel.get("id")] = t
        th = el.find("thread"); tid = th.get("ref") or th.get("id")
        if th.get("fmt"): threads[tid] = th.get("fmt")
        if a.thread not in threads.get(tid, ""): el.clear(); continue
        st = el.find("thread-state")
        bt = el.find("tagged-backtrace")
        if bt is None: bt = el.find("backtrace")
        fl = []
        if bt is not None:
            if bt.get("ref"): fl = bts.get(bt.get("ref"), [])
            else:
                inner = bt.find("backtrace") if bt.tag == "tagged-backtrace" else bt
                if inner is not None and inner.get("ref"): fl = bts.get(inner.get("ref"), [])
                else:
                    fl = [f.get("ref") or f.get("id") for f in (inner if inner is not None else bt).iter("frame")]
                    if inner is not None: bts[inner.get("id")] = fl
                bts[bt.get("id")] = fl
        samp.append((t, fl))
        el.clear()
samp.sort(key=lambda s: s[0])
print(f"thread~'{a.thread}' samples={len(samp)} span={(samp[-1][0]-samp[0][0])/1e9:.1f} s")

# ---------- coarse prior
toc = open(a.toc, errors='replace').read()
sd = re.search(r'<start-date>([^<]+)</start-date>', toc).group(1)
w0 = datetime.datetime.fromisoformat(sd.replace('Z', '+00:00')).timestamp()
pair = re.search(r'wall=([\d.]+) mach=(\d+)', open(a.xc).read())
wp, mp = float(pair.group(1)), int(pair.group(2))
mach0_prior = mp + (w0 - wp) * 24e6
print(f"toc start-date {sd} -> prior mach0 {mach0_prior:.0f} (start-date - pre-record pair = {w0 - wp:+.3f} s)")

# ---------- TL busy intervals in mach
m = None
for ln in open(a.log, errors='replace'):
    mm = re.search(r'\[s7010-clk\] steady_us=(-?\d+) mach=(\d+)(?: split=(\w+))?', ln)
    if mm: m = (int(mm.group(1)), int(mm.group(2)), mm.group(3) or 'parity'); break
S, M, split = m
raw = open(a.tl, 'rb').read(); n = len(raw) // 24
ev4 = [(r[0], r[1], r[4]) for r in (struct.unpack_from('<qIIii', raw, i * 24) for i in range(n)) if r[0] != 0 and r[1] in (6, 7, 15)]
ev = sorted((t, c) for t, c, _ in ev4)
G = collections.Counter(sl for _, c, sl in ev4 if c == 15).most_common(1)[0][0]
fsec = collections.Counter(int((M + (t - S) * 24) // 24000000) for t, c, sl in ev4 if c == 15 and sl == G)  # game frames per mach second
mach = lambda t_us: M + (t_us - S) * 24
busy = []; st6 = None
for t, c in ev:
    if c == 6: st6 = t
    elif c == 7 and st6 is not None: busy.append((mach(st6), mach(t))); st6 = None
print(f"TL gfx tasks={len(busy)}")

def is_uc(fl): return any(frames.get(f, ('?', 0))[0].startswith('factor5_ucode') for f in fl)
x_ms = {}  # ms bin (relative to trace t=0) -> in-ucode 0/1
for t, fl in samp: x_ms[int(t // 1_000_000)] = 1 if is_uc(fl) else 0
keys = sorted(x_ms); lo, hi = keys[0], keys[-1]
X = [x_ms.get(k, -1) for k in range(lo, hi + 1)]

def score(off_ms):
    """agreement of TL busy with xctrace in-ucode, mach0 = prior + off_ms."""
    m0 = mach0_prior + off_ms * 24000
    Y = [0] * len(X)
    i0 = bisect.bisect_left(busy, (m0 + lo * 24000 - 24000 * 50,))
    for s, e in busy[i0:]:
        a0 = int((s - m0) / 24000) - lo; a1 = int((e - m0) / 24000) - lo
        if a0 >= len(X): break
        for k in range(max(a0, 0), min(a1 + 1, len(X))): Y[k] = 1
    agree = tot = 0
    for xv, yv in zip(X, Y):
        if xv < 0: continue
        tot += 1; agree += (xv == yv)
    return agree / max(tot, 1)
if a.offset_ms is None:
    coarse = [(score(o), o) for o in range(-a.win_ms, a.win_ms + 1, 4)]
    best = max(coarse)
    fine = [(score(o), o) for o in range(best[1] - 6, best[1] + 7)]
    bs, bo = max(fine)
    far = max(s for s, o in coarse if abs(o - bo) > 8)
    print(f"align: offset {bo:+d} ms score {bs:.3f}; best >8 ms away {far:.3f}; +500 ms {score(bo + 500):.3f}; prior(0) {score(0):.3f}")
else:
    bo = a.offset_ms; print(f"align: fixed offset {bo} ms score {score(bo):.3f}")
mach0 = mach0_prior + bo * 24000 + a.shift_ms * 24000

def phase(t_ns):
    mt = mach0 + t_ns / 1e9 * 24e6; sec = int(mt // 24000000)
    if a.phases == 2: return (sec ^ (sec >> 3)) & 1 if split == 'xor8' else sec & 1
    return sec % a.phases
def flip_ms(t_ns):
    x = (mach0 + t_ns / 1e9 * 24e6) % 24000000; return min(x, 24000000 - x) / 24000.0

# ---------- block map (same method as xctrace_ucode_blocks.py)
def nmsym(path, rx):
    for l in subprocess.run(["nm", path], capture_output=True, text=True).stdout.split("\n"):
        p = l.split()
        if len(p) == 3 and p[1] in "Tt" and re.fullmatch(rx, p[2]): return int(p[0], 16)
fnc = collections.Counter(frames[f][0].split('(')[0] for _, fl in samp for f in fl[:40] if f in frames and frames[f][0].startswith('factor5_ucode'))
mangled = {"factor5_ucode_nmac": "__Z18factor5_ucode_nmacPhj", "factor5_ucode_lean": "__Z18factor5_ucode_leanPhj",
           "factor5_ucode": "__Z13factor5_ucodePhj"}
fnc = collections.Counter({k: v for k, v in fnc.items() if k in mangled}); mangled = mangled[max(fnc, key=fnc.get)] if fnc else None
slide = int(load, 16) - 0x100000000
fbin = nmsym(a.binary, re.escape(mangled)) if mangled else 0; fobj = nmsym(a.obj, re.escape(mangled)) if mangled else 0  # no ucode on this thread
dl = subprocess.run(["dwarfdump", "--debug-line", a.obj], capture_output=True, text=True).stdout.split("\n")
cfile = None; rows = []
for i, l in enumerate(dl):
    mm = re.match(r"file_names\[\s*(\d+)\]:", l)
    if mm and i + 1 < len(dl) and "factor5_ucode_recompiled.c" in dl[i + 1]: cfile = int(mm.group(1))
    mm = re.match(r"(0x[0-9a-f]{16})\s+(\d+)\s+\d+\s+(\d+)", l)
    if mm and int(mm.group(3)) == cfile and int(mm.group(2)) != 0: rows.append((int(mm.group(1), 16), int(mm.group(2))))
rows.sort(); raddr = [r[0] for r in rows]
src = open(a.csrc, errors="replace").read().split("\n")
labs = [(i + 1, mm.group(1)) for i, l in enumerate(src) for mm in [re.match(r"\s*L_([0-9A-F]+):", l)] if mm]
labln = [x[0] for x in labs]
bcache = {}
def block_of(addr):
    if addr in bcache: return bcache[addr]
    k = bisect.bisect_right(raddr, addr - slide - fbin + fobj) - 1
    b = "?"
    if k >= 0:
        j = bisect.bisect_right(labln, rows[k][1]) - 1; b = "L_" + labs[j][1] if j >= 0 else "pre"
    bcache[addr] = b; return b

cn = lambda s: re.sub(r"\(.*", "", s)[:58]
# s7021 v2: per FULL mach second (seconds cut by the trace start/end are dropped: counting them as whole seconds diluted the
# first version's rates). Each key gets a per-second count (1 sample = 1 ms on-CPU). Scene content swings the gfx thread by
# +-100 ms/s between seconds, so phases are compared PAIRED: for --phases 3 every full p0,p1,p2 triple of consecutive seconds
# gives d = (x1 + x2) / 2 - x0 (scene drift over 3 s mostly cancels), reported as mean +- SE over triples; A/A control =
# mean(x2 - x1) over the same triples (both cap 10240 in the s7020 recipe) must be ~0 within its SE.
msec = lambda t: (mach0 + t / 1e9 * 24e6) / 24e6
s_lo = int(msec(samp[0][0])) + 1; s_hi = int(msec(samp[-1][0])) - 1  # full seconds only
per = collections.defaultdict(collections.Counter)  # sec -> key -> samples
for t, fl in samp:
    sec = int(msec(t))
    if not (s_lo <= sec <= s_hi) or flip_ms(t) < a.guard_ms: continue
    C = per[sec]; C['#thread on-cpu'] += 1
    if not fl: continue
    nms = [frames.get(f, ('?', 0))[0] for f in fl]
    C['leaf:' + cn(nms[0])] += 1
    ku = next((i for i, nm in enumerate(nms) if nm.startswith("rsp_dpc_submit_impl")), None)
    if ku is not None: C['#under submit'] += 1; C["sub:" + (cn(nms[ku - 1]) if ku else "(self)")] += 1
    for k, fid in enumerate(fl):
        nm, ad = frames.get(fid, ('?', 0))
        if nm.startswith('factor5_ucode'):
            C['#ucode incl'] += 1; b = block_of(ad - (0 if k == 0 else 1)); C['incl:' + b] += 1
            if k == 0: C['#ucode self'] += 1; C['self:' + b] += 1
            break
P = a.phases; scale = 1.0 / (1 - 2 * a.guard_ms / 1000.0)  # guard removes 2*guard ms of every second
groups = [list(range(s0, s0 + P)) for s0 in range(s_lo, s_hi - P + 2) if (s0 % P) == 0] if P == 3 else \
         [[s0, s0 + 1] for s0 in range(s_lo, s_hi) if phase((s0 * 24e6 - mach0) / 24e6 * 1e9 + 5e8) == 0 and phase(((s0 + 1) * 24e6 - mach0) / 24e6 * 1e9 + 5e8) == 1]
print(f"full seconds {s_lo}..{s_hi} ({s_hi - s_lo + 1}), paired groups={len(groups)} (guard {a.guard_ms} ms, rates x{scale:.3f})")
PF = [False]
def stat(key):
    d = []; aa = []
    for g in groups:
        x = [per[s][key] * scale for s in g]
        if PF[0]: x = [v / max(fsec[s], 1) for s, v in zip(g, x)]  # ms per game frame
        if P == 3: d.append((x[1] + x[2]) / 2 - x[0]); aa.append(x[2] - x[1])
        else: d.append(x[1] - x[0])
    mean = lambda v: sum(v) / len(v)
    se = lambda v: (sum((u - mean(v)) ** 2 for u in v) / (len(v) - 1) / len(v)) ** 0.5 if len(v) > 1 else float('nan')
    base = mean([per[g[0]][key] * scale for g in groups])
    return base, mean(d), se(d), (mean(aa) if aa else float('nan')), (se(aa) if aa else float('nan'))
keys = set().union(*[set(c) for c in per.values()])
print(f"{'key':66s} {'p0':>8s} {'delta':>7s} {'+-SE':>6s}  {'A/A':>6s} {'+-SE':>5s}")
def show(ks):
    for k in ks:
        b, dm, ds, am, asd = stat(k)
        print(f"  {k[:64]:64s} {b:8.3f} {dm:+7.3f} {ds:6.3f}  {am:+6.3f} {asd:5.3f}")
# s7021: per-SECOND deltas are ~0 by construction when the gfx thread is not saturated: extra cells raise per-frame cost and cut
# fps in the same ratio (TL: rsp 13.11 ms x 59.9 fps = 14.81 x 52.7 = 785 ms/s). So report PER GAME FRAME (TL swaps per second).
fr = [(fsec[g[0]], (fsec[g[1]] + fsec[g[-1]]) / 2) for g in groups]
print(f"game frames/s (TL): p0 {sum(f[0] for f in fr) / len(fr):.1f}, p1..: {sum(f[1] for f in fr) / len(fr):.1f}")
print("== per second (ms/s)"); show(sorted(k for k in keys if k.startswith('#')))
PF[0] = True; print(f"== PER GAME FRAME (ms/frame)  {'key':50s}")
show(sorted(k for k in keys if k.startswith('#')))
for pre, n in (('self:', a.top), ('incl:', 8), ('leaf:', a.top), ('sub:', 8)):
    ks = sorted((k for k in keys if k.startswith(pre)), key=lambda k: -abs(stat(k)[1]))[:n]
    print(f"-- {pre} top {n} by |delta|"); show(ks)
