"""s6706 G1e: fold [g1e-aq] lines (ROGUESQ_G1B=1 + ROGUESQ_RDP_ASYNC[_TOGGLE]) into per-arm per-task means (t >= tmin).
rsp = send_dl entry -> drain entry (RSP + producer work), drain = wait for the worker at task end, wk = worker busy per task,
wk_tail = worker busy after drain entry. H-endload: drain ~ wk_tail ~ large, wk - wk_tail small. H-worker: wk ~ total.
H-producer: rsp(as=1) > rsp(as=0) - sync_rt64(as=0). Usage: g1e_aq.py <run_dir>... [--tmin S]"""
import sys, os, re, statistics as st
args = sys.argv[1:]; tmin = 140
if "--tmin" in args: i = args.index("--tmin"); tmin = int(args[i + 1]); del args[i:i + 2]
R = re.compile(r"^\[g1e-aq\] t=(\d+) as=(\d) n=(\d+) (.*)$")
for d in args:
    arms = {0: [], 1: []}
    for ln in open(os.path.join(d, "run.log"), errors="replace"):
        m = R.match(ln)
        if m and int(m[1]) >= tmin:
            kv = dict(x.split("=") for x in m[4].split()); kv = {k: float(v) for k, v in kv.items()}; kv["n"] = int(m[3])
            arms[int(m[2])].append(kv)
    print(os.path.basename(d))
    for a, rows in arms.items():
        if not rows: continue
        N = sum(r["n"] for r in rows)
        w = lambda k: sum(r[k] * r["n"] for r in rows) / N
        print(f"  as={a} secs={len(rows):3d} tasks={N:5d} " + " ".join(f"{k}={w(k):.2f}" for k in rows[0] if k != "n"))
