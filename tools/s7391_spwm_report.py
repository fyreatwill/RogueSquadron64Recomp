#!/usr/bin/env python3
"""s7391 guest stack low-water report (class BA). usage: s7391_spwm_report.py <log> [funcs_dir]
Reads [s7391-sp] lines (build_spwm, ROGUESQ_S7391_SPWM=1), keeps the deepest record per thread, names the thread by
matching its first $sp to the static osCreateThread table (s7391, from the retail ELF disassembly), names the deepest
frame's function from the generated file:line, and compares depth with the stack size where it is statically known.
Exit 0 = every thread with a known size keeps >= 128 B headroom; 3 = a thread is within 128 B of (or past) its bottom;
2 = no records (instrument did not fire: not a result)."""
import re, sys, os, bisect
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen  # s7723

# name, stack top (osCreateThread sp arg), size in bytes (None = bottom not known statically), how known
STATIC = [
    ("preNmiResetThread",        0x8010DDA0, None, "sp = OSThread addr"),
    ("idle_thread_handle",       0x8010FED8, None, "static"),
    ("thread3_video_handle",     0x801163B0, None, "static (game main loop)"),
    ("siServiceThread",          0x80110520, None, "static"),
    ("viRetraceHandlerThread",   0x8011C928, None, "static"),
    ("dpInterruptHandlerThread", 0x8011CD28, 0x400, "static: [vi top 0x8011C928, OSThread(vi) 0x8011CD28)"),
    ("spTaskSchedulerThread",    0x8011D498, None, "static"),
]
# registerServiceWorker(msgs, stack size, pri, entry) callers (0x80006C28: rs_malloc, top = round8 end, bottom = top - size,
# two 0xCDCDCDCD canary words AT the bottom: the game's own checkServiceWorkerStackGuard overflow test)
SERVICE = {"mainBootstrapWorker": 8192, "mainEventQueueWorker": 8192, "piDmaWorker": 512, "hudDisplayUpdateWorker": 2048,
           "saveServiceWorker": 2048, "tickBackdropLoaderWorker": 2048, "tickSongAssetLoadWorker": 2048}
HEAP1K = {"periodicCallbackWorker": "rs_malloc(8192) base+0x400 (0x800073F0)",
          "runAiAudioStreamPlaybackLoop": "rs_malloc(1024) base+0x400 (0x80091BF8)"}
REC = re.compile(r"\[s7391-sp\] tid=(\d+) first=0x([0-9A-F]+) min=0x([0-9A-F]+) depth=(\d+) (\S+):(\d+) "
                 r"nz_below=(-?\d+)/64 nz_above=(-?\d+)/16")
FN = re.compile(r"^(?:RECOMP_FUNC )?void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{")
_idx = {}

def func_at(fdir, f, line):
    if f not in _idx:
        rows = []
        p = os.path.join(fdir, f)
        if not os.path.exists(p):
            p2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'RecompiledPatches', f)
            p = p2 if os.path.exists(p2) else None
        if p:
            for i, s in enumerate(open(p, errors='replace'), 1):
                m = FN.match(s)
                if m: rows.append((i, m.group(1)))
        _idx[f] = rows
    rows = _idx[f]
    k = bisect.bisect_right([r[0] for r in rows], line) - 1
    return rows[k][1] if k >= 0 else "?"

def frame_at(fdir, f, line):
    p = os.path.join(fdir, f)
    if not os.path.exists(p): return 0
    with open(p, errors='replace') as fh:
        for i, t in enumerate(fh, 1):
            if i == line:
                m = re.search(r"ADD32\(ctx->r29, -0X([0-9A-F]+)\)", t)
                return int(m.group(1), 16) if m else 0
    return 0

def main():
    log = sys.argv[1]
    fdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', '..', 'N64Recomp', 'RecompiledFuncs')
    deep, firstfn, firstrec, nrec = {}, {}, {}, 0
    for s in zopen(log, errors='replace'):
        m = REC.search(s)
        if not m: continue
        nrec += 1
        tid = int(m.group(1)); r = (int(m.group(4)), int(m.group(2), 16), int(m.group(3), 16), m.group(5), int(m.group(6)),
                                    int(m.group(7)), int(m.group(8)))
        if tid not in firstfn: firstfn[tid] = func_at(fdir, r[3], r[4]); firstrec[tid] = r
        if tid not in deep or r[0] > deep[tid][0]: deep[tid] = r
    if not nrec:
        print("VERDICT no-records (instrument did not fire)"); return 2
    worst = 0
    for tid in sorted(deep):
        d, first, mn, f, l, nb, na = deep[tid]
        name, top, size, how = "?", None, None, ""
        for n, t, sz, h in STATIC:
            if 0 <= t - first < 0x200: name, top, size, how = n, t, sz, h
        est = first + frame_at(fdir, firstrec[tid][3], firstrec[tid][4]) + 0x10  # ultramodern t->sp = sp - 0x10
        if name == "?" and firstfn[tid] in HEAP1K:
            name, top, size, how = firstfn[tid], est, 0x400, HEAP1K[firstfn[tid]] + " top=first+frame+0x10"
        if name == "?" and firstfn[tid] in SERVICE:
            name, top, size, how = firstfn[tid], est, SERVICE[firstfn[tid]], "service worker, top=first+frame+0x10"
        if name == "?" and firstfn[tid] == "main": name, how = "boot/main", "recomp entry sp"
        used = (top - mn) if top else d
        room = (size - used) if size else None
        if room is not None and room < 128: worst = 3
        print(f"THREAD tid={tid} name={name} firstfn={firstfn[tid]} first=0x{first:08X} top={'0x%08X' % top if top else '?'} "
              f"min=0x{mn:08X} used={used} size={size if size else '?'} headroom={room if room is not None else '?'} "
              f"deepest={func_at(fdir, f, l)} {f}:{l} nz_below={nb}/64 nz_above={na}/16 {how}")
    print(f"RECORDS {nrec} THREADS {len(deep)}")
    # line B: last [s7391-scan] per service-worker thread (memory dirtied vs the entry snapshot)
    SC = re.compile(r"\[s7391-scan\] tid=(\d+) bottom=0x([0-9A-F]+) top=0x([0-9A-F]+) lowdirty=0x([0-9A-F]+) "
                    r"spmin=0x([0-9A-F]+) gap=(-?\d+) canary=(\d) ctlseen=(\d)")
    last, nscan, ctl_all, neg, canbad = {}, 0, True, [], []
    for t in zopen(log, errors='replace'):
        m = SC.search(t)
        if not m: continue
        nscan += 1; tid = int(m.group(1)); last[tid] = m
        if m.group(8) != '1': ctl_all = False
        if int(m.group(4), 16) and int(m.group(6)) < 0: neg.append(tid)
        if m.group(7) != '1': canbad.append(tid)
    for tid in sorted(last):
        m = last[tid]; bot, top, low = (int(m.group(i), 16) for i in (2, 3, 4))
        print(f"SCAN tid={tid} size={top-bot} lowdirty=0x{low:08X} spmin=0x{m.group(5)} gap={m.group(6)} "
              f"dirty_used={top-low if low else 0} canary={m.group(7)} ctlseen={m.group(8)}")
    if nscan:
        print(f"LINEB scans={nscan} threads={len(last)} control={'PASS' if ctl_all else 'FAIL/off'} "
              f"below_spmin_tids={sorted(set(neg))} canary_broken_tids={sorted(set(canbad))}")
        if neg or canbad: worst = 3
    print("VERDICT", "headroom-low" if worst else "headroom-ok")
    return worst

if __name__ == '__main__':
    sys.exit(main())
