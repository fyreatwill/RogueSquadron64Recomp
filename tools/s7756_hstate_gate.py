#!/usr/bin/env python3
"""s7756 hangar H-state visibility gate (wraps tools/s7755_hstate_visibility.py for tools/s7651_gate_sweep.py).

The s7753 RDP-output gate excludes the hangar (AVAILABLE CRAFT) because the game CPU rewrites the craft display list while the
gfx task reads it (s7754 H-state), so no begin-of-task snapshot replays it byte-exact. s7755 measured that the rewrite is not
VISIBLE: the live RDP tail and our ucode replayed on the END-of-task RAM render within 1 LSB. This gate keeps that property:
for each retained hangar snap pair (<snap>.bin + <snap>_end.bin) at its live policy, live-vs-end must have 0 px at >=2 LSB,
and both s7755 controls (one-pixel flip, shade+16 on the differing tris) must PASS. live-vs-begin may legitimately reach 2-3 LSB
(it is the stale-vertex image) and is reported, not gated.
--controls (iron rule 1): ROGUESQ_UCODE_CAP=<capc> truncates the end replay, so live-vs-end MUST then show >=2 LSB px; a gate
that cannot see a truncated hangar stream is HOLLOW.
Inputs absent (fresh clone: scratch/ is gitignored) -> prints "NEEDS-INPUT ..." and exits 4.
usage: s7756_hstate_gate.py [--controls]   exit 0 GREEN, 1 RED, 3 control FAIL, 4 NEEDS-INPUT"""
import os, re, subprocess, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "tools/s7755_hstate_visibility.py")
H = os.path.join(ROOT, "tools/s7752_port_task/harness")
OBJ = os.path.join(ROOT, "build/CMakeFiles/RogueSquadron64Recomp.dir/src/rsp/factor5_ucode_lean.cpp.o")
# snap -> live policy (s7754 capture: dd1 4:3 retail CAP=65536 TG_FIX=0; 16:9 dd2 FPS60 CAP=1048576 TG_FIX=1); capc truncates.
PAIRS = {
    "scratch/s7754/retained/hangar_hstate/k900_s1250.bin": dict(cap=65536, tg=0, capc=2048),        # hangar, dd1 4:3
    "scratch/s7754/retained/hangar_hstate_dd2/k900_s1500.bin": dict(cap=1048576, tg=1, capc=2048),  # hangar, 16:9 dd2 FPS60
    "scratch/s7754/retained/hangar_hstate_219/k900_s1500.bin": dict(cap=1048576, tg=1, capc=2048),  # hangar, 21:9 dd4 FPS60 STANDINS (s7757)
    "scratch/s7754/retained/hangar_hstate_219re/k900_s12750.bin": dict(cap=1048576, tg=1, capc=2048),  # hangar RE-ENTRY after abort, 21:9 (s7759)
}
ROW = re.compile(r"^(live-begin|live-end|begin-end): px=(\d+) ge2LSB=(\d+)$", re.M)


def run(snap, cap, tg):
    d = tempfile.mkdtemp(prefix="s7756_")
    try:
        p = subprocess.run([sys.executable, TOOL, snap, "--cap", str(cap), "--tg", str(tg), "--out", d],
                           capture_output=True, text=True, timeout=900)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    rows = {k: (int(px), int(g2)) for k, px, g2 in ROW.findall(p.stdout)}
    if "live-end" not in rows:
        raise SystemExit(f"RED s7755 rc={p.returncode} printed no live-end row: {(p.stderr or p.stdout).strip()[-300:]}")
    return p.returncode, rows, p.stdout


def main():
    ctl = "--controls" in sys.argv[1:]
    miss = [s for s in PAIRS if not (os.path.exists(os.path.join(ROOT, s)) and os.path.exists(os.path.join(ROOT, s[:-4] + "_end.bin")))]
    if miss:
        print(f"NEEDS-INPUT {len(miss)}/{len(PAIRS)} retained hangar snap pairs absent (re-capture: tools/s7754_capture_route.zsh)")
        return 4
    if not os.path.exists(OBJ):
        print("NEEDS-INPUT live build object factor5_ucode_lean.cpp.o absent (build the game first)")
        return 4
    if not os.path.exists(H) or os.path.getmtime(H) < os.path.getmtime(OBJ):
        r = subprocess.run(["zsh", os.path.join(ROOT, "tools/s7752_port_task/build.sh")], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"RED harness build failed: {r.stderr.strip()[-300:]}")
            return 1
        print("harness rebuilt against the live factor5_ucode_lean.cpp.o")
    red = 0; cfail = 0
    for s, P in PAIRS.items():
        rc, rows, out = run(os.path.join(ROOT, s), P["cap"], P["tg"])
        ctl_ok = rc != 2 and "CTL flip PASS" in out and re.search(r"CTL shade\+16 .* PASS", out) is not None
        le = rows["live-end"]; lb = rows.get("live-begin", (-1, -1))
        ok = le[1] == 0 and ctl_ok
        print(f"{os.path.basename(s)} cap={P['cap']} tg={P['tg']} live-end px={le[0]} ge2LSB={le[1]} "
              f"live-begin(info) px={lb[0]} ge2LSB={lb[1]} s7755-ctls={'PASS' if ctl_ok else 'FAIL'} -> {'EQUAL' if ok else 'DIFF'}")
        red += not ok
        if ctl:
            rc2 = run(os.path.join(ROOT, s), P["capc"], P["tg"])[1]
            okc = rc2["live-end"][1] >= 1
            print(f"  ctl cap={P['capc']}: truncated live-end ge2LSB px={rc2['live-end'][1]} -> {'PASS' if okc else 'FAIL'}")
            cfail += not okc
    if ctl:
        print(f"CONTROL {'PASS' if cfail == 0 else 'FAIL'} pairs={len(PAIRS)}")
        if cfail:
            return 3
    if red:
        print(f"VERDICT RED: {red}/{len(PAIRS)} hangar H-state pairs render visibly different live vs end-of-task replay")
        return 1
    print(f"VERDICT GREEN: {len(PAIRS)}/{len(PAIRS)} hangar H-state pairs live == end replay within 1 LSB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
