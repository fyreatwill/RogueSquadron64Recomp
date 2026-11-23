# NEXT (s7851)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7850 closed the 0x31=7 rumble fork as an oracle CPU-timing race (SI pass preempting physics mid-frame; w115/w116 now
TIMING-class in tools/s7849_rec_align.py). The only remaining 0x31=7 record diff: rows 1505-1510 (p4 vs r1), w149 = player obj
0x80137DBC+0x248 retail 1.2 (3f99999a) vs port 0.3 (3e99999a), w135 = obj+0x1F8 low half 0x0003 vs 0x0011/0x0013 (rows 1505-1507).
Unit (ONE oracle run, offline): name the writer of obj+0x248 / +0x1F8 near mission tick ~1880 (row 1505).
 1. Oracle: `env CPO=1 RSECS=305 EEP=scratch/s7849/lvl.eep PP=19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start
    RDPBIN=/dev/null RS64_ORACLE_FPR=0,4,6,14,20 XO="--watch-write 0x137FF8:0x137FFC --watch-write 0x138004:0x138008 --watch-pc 0x800FA730
    --watch-pc 0x800027C0" zsh tools/s7828_retail_cpo.sh scratch/s7851/r5` (positive control: the watch must fire > 0; obj base is
    fixed at 0x80137DBC? confirm *0x80137DBC first from r1's xtrace; adjust the physical range if not).
 2. Classify the writer: if it is a rumble-adjacent or SI-pass-timed value (e.g. written right after startRumbleEffect / around a
    mid-frame P) -> TIMING-class like w115/w116 (add to TIMING, note why); if it is game logic (hit/weapon/AI) -> H-new-fork, find
    the port-side input that differs.
Hypotheses: H-timing-sibling (writer is in the rumble/feedback block of updatePlayerCraftPhysics) vs H-logic (another path, e.g.
weapon heat/charge or damage flash; then compare with a port write probe in a pinned run).
After that: continue the sweep with `zsh tools/s7849_det_pair.sh 8 scratch/s785x` (0x31=8, ~28 min, background it).
