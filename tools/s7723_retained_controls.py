#!/usr/bin/env python3
"""s7723: planted RED controls for the S7723_RETAINED gates of tools/s7651_gate_sweep.py (one-capture scorers run over their
retained scratch/ capture). Per gate, in ONE run: (1) the real ARGS row must match its PASS regex with rc 0 (positive arm);
(2) one input is rewritten with a single mutation (a control row dropped / disarmed, or an open-class row planted) into a
temp .zst and the same row must then read RED (rc != 0 or the regex unmatched). Exit 0 iff every gate passes both arms.
usage: s7723_retained_controls.py [gate ...]   (default: all; inputs absent -> SKIP, exit 3 if any skipped)"""
import os, re, subprocess, sys, tempfile, importlib.util as iu
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sp = iu.spec_from_file_location("sweep", os.path.join(ROOT, "tools", "s7651_gate_sweep.py"))
SW = iu.module_from_spec(sp); sp.loader.exec_module(SW)

def drop(prefix):
    return lambda lines: [l for l in lines if not l.startswith(prefix)], f"drop {prefix} rows"

def sub_first(pat, rep, where=None):
    def f(lines):
        out, done = [], False
        for l in lines:
            if not done and (where is None or l.startswith(where)) and re.search(pat, l):
                l = re.sub(pat, rep, l, count=1); done = True
            out.append(l)
        assert done, f"mutation {pat!r} found no row"
        return out
    return f, f"first {where or ''} row {pat} -> {rep}"

# gate -> (index or indices of the inputs in its argv to mutate, mutation)
MUT = {
    "s7392_mq_report.py": (0, drop("[s7392-ctl]")),
    "s7393_cq_report.py": (0, drop("[s7393-ctl]")),
    "s7394_bd_report.py": (0, drop("[s7394-sum]")),
    "s7396_tq_report.py": (0, drop("[s7396-tq-ctl]")),
    "s7397_timer_report.py": (0, drop("[s7397-tm-ctl]")),
    "s7399_evp_report.py": (0, drop("[s7399-ctl]")),
    "s7516_pak_shape.py": (2, drop("[s7516-pak]")),          # the --ctl arm loses its motor rows
    "s7517_vi_feat.py": ((2, 3, 4, 5), drop("[vi-feat-ctl]")),   # one arm showing the ctl suffices, so disarm every arm
    "s7518_cache_shape.py": ((2, 3, 4, 5), drop("[cache-ctl]")),
    "s7528_evict_score.py": (2, sub_first(r"stale_window_entries=0\b", "stale_window_entries=5")),  # open row in NEW arm
    # directory input: copy its san_* files and append one live UBSan row to the un-planted arm p
    "s7579_bounds_report.py": (0, "DIR"),
    # s7801: the MTL_OWN=0 control arm loses every _NSZombie_ row -> CONTROL FAIL, exit 3
    "s7726_zombie_census.py": (3, (lambda L: [l for l in L if "class _NSZombie_" not in l], "drop control _NSZombie_ rows")),
    # s7724: profiler dirs; every sample file gets the planted control frames renamed, so CONTROL must FAIL (exit 3)
    **{t: (0, "SAMPLES") for t in SW.S7724_RETAINED if t not in ("s7467_san_report.py", "s7624_flicker_score.py")},
    "s7467_san_report.py": (0, "SANDIR"),   # copy the arm files, plant one unreviewed UBSan group in arm l7 -> new_groups=1, exit 1
    "s7624_flicker_score.py": (0, (lambda L: [l for l in L if not re.search(r"\[standins-fb\] n=\d+ win=1 ", l)],
                                   "drop window-1 [standins-fb] rows")),
}

def dir_mutant(src, td):
    import glob, shutil
    d = os.path.join(td, "san"); os.makedirs(d)
    for f in glob.glob(os.path.join(ROOT, src, "san_*")):
        shutil.copy(f, d)
    tgt = sorted(glob.glob(os.path.join(d, "san_p.*")))[0]
    with open(tgt, "a") as fh:
        fh.write("/tmp/s7723_plant.c:12:5: runtime error: index 9 out of bounds for type 'int[4]'\n")
    return d

def samples_mutant(src, td):
    import glob, shutil
    d = os.path.join(td, "smp"); os.makedirs(d); n = 0
    for f in glob.glob(os.path.join(ROOT, src, "*")):
        if not os.path.isfile(f): continue
        if f.endswith(".txt.zst"):
            t = subprocess.run(["zstd", "-dcq", f], capture_output=True, check=True).stdout.decode("utf-8", "replace")
            t, k = re.subn(r"rs64_(store_diag_tick|diag_spin_us|diag_quiet_tick)", r"mut_ctl_\1", t); n += k
            subprocess.run(["zstd", "-1qf", "-o", os.path.join(d, os.path.basename(f))], input=t.encode(), check=True)
        else:
            shutil.copy(f, d)
    assert n, "no control frames to rename"
    return d, n

def sandir_mutant(src, td):
    import glob, shutil
    d = os.path.join(td, "sanr"); os.makedirs(d)
    for f in glob.glob(os.path.join(ROOT, src, "san_*")) + glob.glob(os.path.join(ROOT, src, "log_*")):
        shutil.copy(f, d)
    tgt = sorted(glob.glob(os.path.join(d, "san_l7.*")))[0]
    with open(tgt, "a") as fh:
        fh.write("src/main/s7724_plant.cpp:12:5: runtime error: shift exponent 40 is too large for 32-bit type 'int'\n"
                 "    #0 0x100001234 in rs64_s7724_plant_fn s7724_plant.cpp:12\n")
    return d

def run(t, argv, rx):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", t)] + argv, capture_output=True, text=True, cwd=ROOT)
    o = r.stdout + r.stderr
    return r.returncode == 0 and (rx is None or re.search(rx, o) is not None), r.returncode, o.strip().split("\n")[-1][:110]

def main(sel):
    bad = skip = 0
    for t, (argv, rx) in {**SW.S7723_RETAINED, **SW.S7724_RETAINED}.items():
        if sel and t not in sel: continue
        if not all(os.path.exists(os.path.join(ROOT, a)) for a in argv if "/" in a):
            print(f"SKIP {t}: retained input absent"); skip += 1; continue
        ok, rc, tail = run(t, argv, rx)
        if MUT[t][1] == "SAMPLES":
            with tempfile.TemporaryDirectory() as td:
                margv = list(argv); margv[MUT[t][0]], n = samples_mutant(argv[MUT[t][0]], td)
                mok, mrc, mtail = run(t, margv, rx)
            res = ok and not mok; bad += not res
            print(f"{'PASS' if res else 'FAIL'} {t}: real rc={rc} pass={int(ok)} | mutant ({n} control frames renamed) "
                  f"rc={mrc} pass={int(mok)} :: {mtail}")
            continue
        if MUT[t][1] == "SANDIR":
            with tempfile.TemporaryDirectory() as td:
                margv = list(argv); margv[MUT[t][0]] = sandir_mutant(argv[MUT[t][0]], td)
                mok, mrc, mtail = run(t, margv, rx)
            res = ok and not mok; bad += not res
            print(f"{'PASS' if res else 'FAIL'} {t}: real rc={rc} pass={int(ok)} | mutant (1 unreviewed UBSan group planted in arm l7) "
                  f"rc={mrc} pass={int(mok)} :: {mtail}")
            continue
        if MUT[t][1] == "DIR":
            with tempfile.TemporaryDirectory() as td:
                margv = list(argv); margv[MUT[t][0]] = dir_mutant(argv[MUT[t][0]], td)
                mok, mrc, mtail = run(t, margv, rx)
            res = ok and not mok; bad += not res
            print(f"{'PASS' if res else 'FAIL'} {t}: real rc={rc} pass={int(ok)} | mutant (1 live UBSan row planted in arm p) "
                  f"rc={mrc} pass={int(mok)} :: {mtail}")
            continue
        idx, (fn, what) = MUT[t]
        idx = (idx,) if isinstance(idx, int) else idx
        margv, removed = list(argv), 0
        with tempfile.TemporaryDirectory() as td:
            try:
                for i in idx:
                    src = argv[i]
                    lines = subprocess.run(["zstd", "-dcq", os.path.join(ROOT, src)], capture_output=True,
                                           check=True).stdout.decode("utf-8", "replace").split("\n")
                    mut = fn(lines)
                    removed += len(lines) - len(mut)
                    mp = os.path.join(td, f"mut{i}_" + os.path.basename(src))
                    subprocess.run(["zstd", "-1qf", "-o", mp], input="\n".join(mut).encode(), check=True)
                    margv[i] = mp
            except AssertionError as e:
                print(f"FAIL {t}: {e}"); bad += 1; continue
            mok, mrc, mtail = run(t, margv, rx)
        res = ok and not mok
        bad += not res
        print(f"{'PASS' if res else 'FAIL'} {t}: real rc={rc} pass={int(ok)} | mutant ({what}, {removed} rows removed) "
              f"rc={mrc} pass={int(mok)} :: {mtail}")
    print(f"CONTROLS {'PASS' if not bad else 'FAIL'} bad={bad} skipped={skip}")
    return 1 if bad else (3 if skip else 0)

if __name__ == "__main__":
    sys.exit(main(set(sys.argv[1:])))
