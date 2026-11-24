#!/usr/bin/env python3
"""s7862: the G3 retail-flight det sweep (save byte 0x31 = 0..15 + bonus 16/17/18) as one checked table.

usage: python3 tools/s7862_det_sweep_table.py [--control]

Every row records the ledger verdict for one mission. Rows with a retained score.txt (the s7849_det_pair.sh output, scored
since s7854 with a p2 unpinned arm + a word-50 flip control) are RE-SCORED here by tools/s7856_det_verdict.py and must give
the recorded verdict (and fork class on FORK rows); a disagreement prints MISMATCH and exits 1. Rows from before the driver
carried the control section (s7831-s7853) are hand-scored in the cited session and printed as `hand`.
--control plants a wrong expected verdict on the first re-scored row and must report MISMATCH 1 (exit 0 if it does).
Prints `TABLE OK rescored=N hand=M mismatch=0` on success.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# (0x31 / label, mission, session, verdict, fork class or '', score.txt path or None, note)
ROWS = [
    ("0", "mission 1", "s7880", "H-exact", "", "scratch/s7880/v1/score.txt", "305 s pinned pair, retail-matched AP schedule (APM=1): all 5556 retail ticks H-exact, full record 5555; render 2895/2895 flight frames exact on s7879's first 2901 ticks (s7879 short schedule / s7831 hand row superseded)"),
    ("1", "mission 2", "s7881", "H-exact", "", "scratch/s7881/v1/score.txt", "305 s pinned pair, APM=1: all 5776 retail ticks H-exact, full record 5776; render 5771/5771 flight frames exact (s7840 hand row superseded)"),
    ("2", "mission 3", "s7840", "H-exact", "", None, "pinned port = retail"),
    ("3", "mission 4 Corellia", "s7877", "FORK", "audio-clock", "scratch/s7877/v3/score.txt", "s7840 170 s run was pre-death; 305 s: death song 01 ends t2313/t2312, render exact 2308 pre-fork"),
    ("4", "mission 5 Gerrard V", "s7878", "H-exact", "", "scratch/s7878/v4/score.txt", "305 s pinned pair: 5926 ticks H-exact, render 5779/5779 flight frames exact (s7841-3 170 s hand row superseded)"),
    ("5", "mission 6", "s7845", "H-exact", "", None, "seed pin + dt replay, 2262 rows bit-identical"),
    ("6", "mission 7", "s7882", "H-exact", "", "scratch/s7882/v6/score.txt", "305 s pinned pair, APM=1: all 1876 retail ticks H-exact, full record 1876; render 1873/1873 flight frames exact (s7847 hand row superseded)"),
    ("7", "mission 8", "s7851", "H-exact", "", None, "rumble/3D-sound residual = timing class (s7850/s7851)"),
    ("8", "mission 9", "s7883", "FORK", "audio-clock", "scratch/s7883/v8/score.txt", "305 s pinned pair, APM=1: song 03 end t3527/t3526 again (= s7852 under the old schedule), render exact 3523/3523 pre-fork flight frames"),
    ("9", "mission 10", "s7884", "H-exact", "", "scratch/s7884/v9/score.txt", "305 s pinned pair, APM=1: all 5076 retail ticks H-exact, full record 5074; render 5067/5067 flight frames exact (s7853 hand row superseded)"),
    ("10", "mission 11 Bespin", "s7854", "H-exact", "", "scratch/s7854b/score.txt", ""),
    ("11", "mission 12", "s7855", "H-exact", "", "scratch/s7855/score.txt", ""),
    ("12", "mission 13", "s7885", "H-exact", "", "scratch/s7885/v12/score.txt", "305 s pinned pair, APM=1: all 5765 retail ticks H-exact, full record 5763; render 5754/5754 flight frames exact (s7856 row superseded)"),
    ("13", "mission 14", "s7886", "H-exact", "", "scratch/s7886/v13/score.txt", "305 s pinned pair, APM=1: all 3903 retail ticks H-exact, full record 3902, residual timing-class (word 149 t1979, = s7857); render 3900/3900 flight frames exact (s7857 row superseded)"),
    ("14", "mission 15", "s7887", "FORK", "audio-clock", "scratch/s7887/v14/score.txt", "305 s pinned pair, APM=1: song 01 end t1396/t1395 again (= s7857/s7858), render exact 1392/1392 pre-fork flight frames (s7858 row superseded)"),
    ("15", "mission 16", "s7888", "H-exact", "", "scratch/s7888/v15/score.txt", "305 s pinned pair, APM=1: all 1892 retail ticks H-exact, full record 1891, residual timing-class (word 149 t943); render 1887/1887 flight frames exact at the flight offset (--port-start 7439; the ~150 s intro shifts pairing -98 -> -99) (s7859 row superseded)"),
    ("16 locked", "= mission 16 dup", "s7859", "H-exact", "", "scratch/s7859/v16/score.txt", "locked-bonus fallback to 15"),
    ("b16", "bonus race", "s7889", "H-exact", "", "scratch/s7889/v16b/score.txt", "race-safe press schedule, APM-scaled AP + bonus save: all 458 retail ticks H-exact, residual none; render exact on all 455/455 frames of the race (--port-start 1916; the 723 pre-tick-0 lead-in is unpinned) (s7860 row superseded)"),
    ("b17", "bonus Death Star trench", "s7861", "FORK", "audio-clock", "scratch/s7861/v17/score.txt", "song 3 end t1124/t1123"),
    ("b18", "bonus Battle of Hoth", "s7890", "H-exact", "", "scratch/s7890/v18/score.txt", "s7862 PP + APM-scaled AP (s7889 rule): all 6444 retail ticks H-exact, residual none; render 6439/6439 flight frames exact (global offset 317, no --port-start needed) (s7862 row superseded)"),
]


def rescore(path):
    sys.path.insert(0, HERE)
    from rs64_zopen import resolve
    p = resolve(os.path.join(ROOT, path))
    out = subprocess.run([sys.executable, os.path.join(HERE, "s7856_det_verdict.py"), p],
                         capture_output=True, text=True).stdout.strip()
    toks = out.split()
    verdict = toks[1] if len(toks) > 1 else "MISSING"
    fork = ""
    if "fork=" in out:
        fork = out.split("fork=", 1)[1].split("(")[0].strip()
    return verdict, fork, out


def main():
    control = "--control" in sys.argv
    resc = hand = bad = 0
    planted = False
    for key, name, sess, verdict, fork, path, note in ROWS:
        exp_v, exp_f = verdict, fork
        if path is None:
            hand += 1
            print(f"{key:>9}  {name:<24} {sess}  {verdict:<8} {fork or '-':<12} hand  {note}")
            continue
        if control and not planted:
            exp_v = "FORK" if verdict == "H-exact" else "H-exact"
            planted = True
        got_v, got_f, raw = rescore(path)
        ok = got_v == exp_v and (exp_v != "FORK" or got_f == exp_f)
        resc += 1
        if not ok:
            bad += 1
        tag = "rescored" if ok else f"MISMATCH (got {got_v} {got_f})"
        print(f"{key:>9}  {name:<24} {sess}  {exp_v:<8} {exp_f or '-':<12} {tag}  {note}")
    if control:
        print(f"CONTROL {'PASS' if bad == 1 else 'FAIL'} MISMATCH {bad}")
        return 0 if bad == 1 else 1
    print(f"TABLE {'OK' if bad == 0 else 'BAD'} rescored={resc} hand={hand} mismatch={bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
