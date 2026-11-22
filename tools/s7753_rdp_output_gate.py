#!/usr/bin/env python3
"""s7753 end-to-end ucode OUTPUT regression gate.

The s7741/s7742 ucode gates compare generated C text. This one compares what the ucode EMITS: each retained s7751 gfx-task
snapshot (ROGUESQ_S7751_SNAP .bin: header + DMEM + RDRAM + the live RDP stream tail) is replayed offline through the live
build's factor5_ucode_lean.cpp.o (tools/s7752_port_task/harness, rebuilt when older than that object) at that snap's live
policy (SNAPS: dd1 CAP=65536 TG_FIX=0, dd>1 CAP=1048576 TG_FIX=1), and the output must equal the snap's live tail byte for byte.
s7752 measured 3/3 tasks exact, so any difference means the emitted RDP stream changed: either intended (re-capture with
tools/s7753_capture_snaps.zsh and say so in the ledger) or a regression.

--controls (iron rule 1; a gate that cannot see these is HOLLOW):
  tg0   (snaps with TriGen hits) ROGUESQ_G5B_TG_FIX=0 must DIFFER from the live tail at the cxd4 length pinned in s7752
  cap   ROGUESQ_UCODE_CAP=<capc> must give a strict prefix of the tail with cap_fires=1
  flip  the comparator must call a one-byte-mutated copy of the replay output a mismatch
Inputs absent (fresh clone: scratch/ is gitignored) -> prints "NEEDS-INPUT ..." and exits 4.
usage: s7753_rdp_output_gate.py [--controls]   exit 0 GREEN, 1 RED, 3 control FAIL, 4 NEEDS-INPUT"""
import os, re, shutil, struct, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import resolve, materialize  # s7802: retained snaps are stored *.bin.zst

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = os.path.join(ROOT, "tools/s7752_port_task/harness")
OBJ = os.path.join(ROOT, "build/CMakeFiles/RogueSquadron64Recomp.dir/src/rsp/factor5_ucode_lean.cpp.o")
# snap -> live policy: cap/tg = the ROGUESQ_UCODE_CAP / ROGUESQ_G5B_TG_FIX the live run used (dd1: 65536/0, dd>1: 1048576/1);
# tg0 = cxd4 / retail-ucode (TG_FIX=0) stream length (PORTING-STATE s7752), only where that task has TriGen hits, else None;
# capc = a cap that must truncate the task (cap control). s7754 widened coverage beyond dd8 flight (tools/s7754_capture_route.zsh,
# ROGUESQ_S7751_EVERY): attract, SELECT GAME, the L4 intro cutscene and flight at dd1 4:3 retail and 16:9 dd2 FPS60. The hangar
# (AVAILABLE CRAFT) is EXCLUDED by measurement, not by choice: the game CPU rewrites the craft display list's vertex pointers
# (0x8072xxxx -> 0x80739xxx) while the gfx task reads it, so no begin-of-task snapshot can replay it (s7754 H-state, 10/10 tasks).
SNAPS = {
    "scratch/s7751/snap_f0/k0_s4054.bin": dict(cap=1048576, tg=1, tg0=1716608, capc=65536),   # L1 21:9 dd8 flight FARMAX=0
    "scratch/s7751/snap_d/k0_s4056.bin": dict(cap=1048576, tg=1, tg0=1718528, capc=65536),    # L1 21:9 dd8 flight
    "scratch/s7754/retained/dd1_s250.bin": dict(cap=65536, tg=0, tg0=None, capc=2048),        # attract, dd1 4:3
    "scratch/s7754/retained/dd1_s1000.bin": dict(cap=65536, tg=0, tg0=None, capc=2048),       # SELECT GAME, dd1
    "scratch/s7754/retained/dd1_s1500.bin": dict(cap=65536, tg=0, tg0=None, capc=2048),       # L4 intro cutscene, dd1
    "scratch/s7754/retained/dd1_s3000.bin": dict(cap=65536, tg=0, tg0=None, capc=2048),       # L4 flight, dd1 retail
    "scratch/s7754/retained/dd2w_s2250.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),    # L4 intro cutscene, 16:9 dd2 FPS60
    "scratch/s7754/retained/dd2w_s4000.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),    # L4 flight, 16:9 dd2 FPS60
    # s7757: owner 21:9 recipe (ASPECT=21:9 dd4 FPS60 STANDINS=1), 22/24 route tasks exact (the 2 misses = hangar H-state);
    # tg0 here = our TG_FIX=0 replay length (the retail-ucode TriGen path; not cxd4-run for these two).
    "scratch/s7754/retained/w219_s250.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),     # attract, 21:9 dd4
    "scratch/s7754/retained/w219_s1000.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),    # SELECT GAME, 21:9 dd4
    "scratch/s7754/retained/w219_s2250.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),    # L4 intro cutscene, 21:9 dd4
    "scratch/s7754/retained/w219_s2750.bin": dict(cap=1048576, tg=1, tg0=1401816, capc=2048) ,  # L4 flight, 21:9 dd4 (64 TG hits)
    "scratch/s7754/retained/w219_s4000.bin": dict(cap=1048576, tg=1, tg0=1547472, capc=65536),  # L4 flight, 21:9 dd4 (14 TG hits)
    # s7758: L10 flight at the owner 21:9 dd4 FPS60 STANDINS=1 recipe, in seconds adding 3085 / 5705 stand-ins (~50-95 per frame);
    # the stand-in region 0x81700000+ is CPU-only (node matrices go through the DL pool), so these tasks stay begin-replayable.
    "scratch/s7754/retained/w219L10_s10200.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),  # L10 flight, stand-ins, largest tail
    "scratch/s7754/retained/w219L10_s10800.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),  # L10 flight, stand-ins add peak
    # s7759: hangar RE-ENTRY after a mission abort (s6995 route, owner save, 21:9 dd4 FPS60 STANDINS=1): SELECT YOUR CRAFT scrolls
    # under the s6907/s6995 aim camera replay byte-exact (20/20); the forced route never visits this screen.
    "scratch/s7754/retained/w219re_s15500.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),  # re-entry craft scroll (Y-wing), largest
    "scratch/s7754/retained/w219re_s17000.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),  # re-entry craft settled (A-wing)
    # s7760: in-mission overlays on the same owner route (PAUSE menu and ABORT LEVEL confirm drawn over the re-rendered flight frame,
    # MISSION FAILED medal): 24/24 snaps VI 10920-12300 replay byte-exact from begin AND end (b==e), so overlays are begin-replayable.
    "scratch/s7754/retained/w219ov_s11040.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),  # PAUSE menu, cursor on ABORT LEVEL
    "scratch/s7754/retained/w219ov_s11400.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),  # ABORT LEVEL / ARE YOU SURE? confirm
    "scratch/s7754/retained/w219ov_s12060.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),  # MISSION FAILED medal screen
    "scratch/s7754/retained/w219sel_s1620.bin": dict(cap=1048576, tg=1, tg0=None, capc=2048),  # SELECT LEVEL holo, the one begin-exact task (s7761)
}


def tail(path):
    b = open(path, "rb").read()
    if struct.unpack_from("<I", b, 0)[0] != 0x31353753:
        raise SystemExit(f"RED bad snap header {path}")
    off = 20 + 4096 + struct.unpack_from("<I", b, 16)[0]
    n = struct.unpack_from("<I", b, off)[0]
    return b[off + 4: off + 4 + n]


def replay(snap, tg, cap):
    with tempfile.NamedTemporaryFile(suffix=".rdp", delete=False) as t:
        out = t.name
    env = dict(os.environ, ROGUESQ_UCODE_CAP=str(cap), ROGUESQ_G5B_TG_FIX=str(tg))
    env.pop("S7752_G1E_FAST", None)
    p = subprocess.run([H, snap, out], env=env, capture_output=True, text=True, timeout=300)
    data = open(out, "rb").read() if p.returncode == 0 else b""
    os.unlink(out)
    if p.returncode != 0:
        raise SystemExit(f"RED harness rc={p.returncode}: {p.stderr.strip()[-300:]}")
    m = re.search(r"cap_fires=(\d+)", p.stderr)
    return data, int(m.group(1)) if m else -1


def first_diff(a, b):
    n = min(len(a), len(b))
    return next((i for i in range(n) if a[i] != b[i]), n)


def main():
    ctl = "--controls" in sys.argv[1:]
    snaps = [s for s in SNAPS if resolve(os.path.join(ROOT, s))]
    if 0 < len(snaps) < len(SNAPS):  # s7802: a partly retained set is lost coverage, not a fresh clone
        print(f"RED partial retained input: {len(SNAPS) - len(snaps)}/{len(SNAPS)} snaps absent: "
              f"{[s for s in SNAPS if s not in snaps][:3]}")
        return 1
    if len(snaps) != len(SNAPS):
        print(f"NEEDS-INPUT {len(SNAPS) - len(snaps)}/{len(SNAPS)} retained snaps absent (re-capture: tools/s7753_capture_snaps.zsh, tools/s7754_capture_route.zsh)")
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
    global TMP
    TMP = tempfile.mkdtemp(prefix="s7753_")
    try:
        return _score(snaps, ctl)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)


def _score(snaps, ctl):
    red = 0; cfail = 0
    for s in snaps:
        sp = materialize(os.path.join(ROOT, s), TMP); live = tail(sp)
        P = SNAPS[s]
        got, fires = replay(sp, P["tg"], P["cap"])
        eq = got == live
        print(f"{os.path.basename(s)} live={len(live)} replay={len(got)} cap_fires={fires} "
              f"{'EQUAL' if eq else 'DIFF@%d' % first_diff(got, live)}")
        red += not eq
        if not ctl:
            continue
        ok0 = True
        if P["tg0"] is not None:
            g0, _ = replay(sp, 0, P["cap"])
            ok0 = g0 != live and len(g0) == P["tg0"]
            print(f"  ctl tg0: len={len(g0)} want={P['tg0']} differs={g0 != live} -> {'PASS' if ok0 else 'FAIL'}")
        gc, fc = replay(sp, P["tg"], P["capc"])
        okc = 0 < len(gc) < len(live) and live.startswith(gc) and fc == 1
        print(f"  ctl cap={P['capc']}: len={len(gc)} prefix={live.startswith(gc)} cap_fires={fc} -> {'PASS' if okc else 'FAIL'}")
        mut = bytearray(got); mut[len(mut) // 2] ^= 0x01
        okf = bytes(mut) != live
        print(f"  ctl flip: mutated replay read as {'DIFF' if okf else 'EQUAL'} -> {'PASS' if okf else 'FAIL'}")
        cfail += not (ok0 and okc and okf)
    if ctl:
        print(f"CONTROL {'PASS' if cfail == 0 else 'FAIL'} snaps={len(snaps)}")
        if cfail:
            return 3
    if red:
        print(f"VERDICT RED: {red}/{len(snaps)} tasks' emitted RDP stream differs from the live capture")
        return 1
    print(f"VERDICT GREEN: {len(snaps)}/{len(snaps)} tasks replay == live RDP stream byte-for-byte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
