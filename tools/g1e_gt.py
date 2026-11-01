"""s6710 G1e: join [g1b] (tasks/s, as=<arm>) with [g1b-gt] (per guest thread CPU ms / ms blocked in osRecvMesg, same wall
second) and [s4265-agg] kind=aud (audio task count, SP queue wait). Per arm: mean tasks/s, per-thread cpu/blk/rest (rest =
1000 - cpu - blk = runnable-not-running), then within each arm the slowest vs fastest quartile of seconds by tasks/s.
H-guest: the producing thread's cpu rises in slow seconds (and blk -> 0). H-wait: its blk or rest rises while cpu stays.
H-audio-rsp: aud qw rises in slow seconds. Usage: g1e_gt.py <run_dir>... [--tmin S]"""
import sys, os, re, statistics as st
args = sys.argv[1:]; tmin = 140
if "--tmin" in args: i = args.index("--tmin"); tmin = int(args[i + 1]); del args[i:i + 2]
RB = re.compile(r"^\[g1b\] t=(\d+) .*?tasks=(\d+) .*? as=(\d+)")
RG = re.compile(r"^\[g1b-gt\] t=(\d+) sum_cpu=(\d+)(.*)$")
RQ = re.compile(r"^\[g1e-aq\] t=(\d+) as=(\d) n=\d+ total=([\d.]+)")  # arm 0/2/3 (s6708 NODRAIN=2) + Gfx ms/task
RS = re.compile(r"^\[s4911\] row=(\d+) mq=(0x[0-9A-F]+) tid=(\d+) site=(\S+) blk=\d+ blk_ms=([\d.]+)")  # ROGUESQ_S4908=1
GT = int(os.environ.get("G1E_GT_TID", "3"))  # guest OSId whose blocked time is split by (mq, site); row ~ wall second
RA = re.compile(r"^\[s4265-agg\] t=(\d+) kind=aud n=(\d+) qw_avg=([\d.]+) qw_max=(\d+)")
for d in args:
    sec = {}; aud = {}; blk = {}
    for ln in open(os.path.join(d, "run.log"), errors="replace"):
        m = RB.match(ln)
        if m: sec.setdefault(int(m[1]), {}).update(tasks=int(m[2]), arm=int(m[3])); continue
        m = RG.match(ln)
        if m:
            th = {}
            for tok in m[3].split():
                i, cb = tok.split(":"); c, b = cb.split("/"); th[i] = (float(c), float(b))  # key "slot.osid" (s6710b) or "osid"
            sec.setdefault(int(m[1]), {}).update(sum=float(m[2]), th=th); continue
        m = RQ.match(ln)
        if m: sec.setdefault(int(m[1]), {}).update(qarm=int(m[2]), gfx=float(m[3])); continue
        m = RS.match(ln)
        if m:
            if int(m[3]) == GT: k = (m[2], m[4]); b = blk.setdefault(int(m[1]), {}); b[k] = b.get(k, 0) + float(m[5])
            continue
        m = RA.match(ln)
        if m: aud[int(m[1])] = (int(m[2]), float(m[3]), int(m[4]))
    for r in sec.values():
        if "qarm" in r: r["arm"] = r["qarm"]
    rows = [dict(r, t=t) for t, r in sorted(sec.items()) if t >= tmin and "tasks" in r and "th" in r]
    print(os.path.basename(d), "secs", len(rows), "aud secs", len(aud))
    tids = sorted({i for r in rows for i in r["th"]})
    def line(lbl, rs):
        if not rs: return
        s = f"  {lbl:10s} n={len(rs):3d} tasks/s={st.mean(r['tasks'] for r in rs):5.1f} sum_cpu={st.mean(r['sum'] for r in rs):5.0f}"
        g = [r["gfx"] for r in rs if "gfx" in r]
        if g: s += f" gfx_ms={st.mean(g):.2f}"
        for i in tids:
            c = st.mean(r["th"].get(i, (0, 0))[0] for r in rs); b = st.mean(r["th"].get(i, (0, 0))[1] for r in rs)
            if c >= 5 or b >= 5: s += f" | {i} cpu={c:.0f} blk={b:.0f} rest={1000 - c - b:.0f}"
        a = [aud[r["t"]] for r in rs if r["t"] in aud]
        if a: s += f" | aud n={st.mean(x[0] for x in a):.1f} qw={st.mean(x[1] for x in a):.2f} qwmax={max(x[2] for x in a)}"
        print(s)
        if blk:
            tot = {}
            for r in rs:
                for k, v in blk.get(r["t"], {}).items(): tot[k] = tot.get(k, 0) + v / len(rs)
            for k, v in sorted(tot.items(), key=lambda kv: -kv[1])[:4]:
                if v >= 5: print(f"      tid{GT} blk {v:6.0f} ms/s mq={k[0]} site={k[1]}")
    for arm in sorted({r["arm"] for r in rows}):
        rs = [r for r in rows if r["arm"] == arm]; line(f"as={arm}", rs)
        q = sorted(rs, key=lambda r: r["tasks"]); k = max(1, len(q) // 4)
        line("  slow25%", q[:k]); line("  fast25%", q[-k:])
