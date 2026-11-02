"""s6776 G1e: per-run fps/cost table from the per-second [g1e-split] rows (ROGUESQ_G1E_AQ=2) of one flight phase.
tasks = gfx tasks per second (= game fps), ucode/submit/rest = per-task ms, ns/cmd = ucode_ms / calls (calls is per task),
busy = tasks * (ucode+submit) ms per second (fraction of the Gfx thread), dense = rows with calls/task above the median.
Usage: g1e_dd_table.py <run_dir>... [--phase 6,7] [--skip 10]"""
import sys, os, re, statistics as st
args = sys.argv[1:]; phase = "6,7"; skip = 10
for flag in ("--phase", "--skip"):
    if flag in args:
        i = args.index(flag); v = args[i + 1]; del args[i:i + 2]
        if flag == "--phase": phase = v
        else: skip = int(v)
R = re.compile(r"^\[g1e-split\] phase=(\d+) (.*)$")
print(f"{'run':34s} rows  fps   fps_p10 ucode_ms submit_ms rest_ms calls/task ns/cmd busy  | dense: fps ucode_ms calls")
for d in args:
    rows = []
    for ln in open(os.path.join(d, "run.log"), errors="replace"):
        m = R.match(ln)
        if m and m[1] in phase.split(","):
            kv = {}
            for x in m[2].split():
                k, v = x.split("=")
                try: kv[k] = float(v)
                except ValueError: pass
            if kv.get("tasks", 0) > 0: rows.append(kv)
    rows = rows[skip:]
    if not rows: print(f"{os.path.basename(d):34s} no phase-{phase} rows"); continue
    for r in rows: r["cpt"] = r["calls"]  # already per task (s6715)
    fps = [r["tasks"] for r in rows]
    m = lambda k, rs: st.mean(r[k] for r in rs)
    nscmd = 1e6 * m("ucode_ms", rows) / m("cpt", rows)
    busy = st.mean(r["tasks"] * (r["ucode_ms"] + r["submit_ms"]) / 1000 for r in rows)
    med = st.median(r["cpt"] for r in rows); dense = [r for r in rows if r["cpt"] > med]
    p10 = sorted(fps)[len(fps) // 10]
    print(f"{os.path.basename(d):34s} {len(rows):4d} {st.mean(fps):5.1f} {p10:5.0f}   {m('ucode_ms', rows):7.2f}  {m('submit_ms', rows):7.3f}"
          f"  {m('rest_ms', rows):7.2f} {m('cpt', rows):9.0f} {nscmd:6.1f} {busy:5.2f} | {m('tasks', dense):5.1f} {m('ucode_ms', dense):6.2f}"
          f" {m('cpt', dense):6.0f}")
