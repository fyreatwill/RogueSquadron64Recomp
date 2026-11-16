# NEXT (s7471)
HYPOTHESIS-ID: host-asan-coverage

Class EA (ASan per-level sweep) is OPEN. Done: L0, L1 (dd8 21:9), L2 (s7470 recipe a, 0 NEW, plants PASS); earlier L4, L7, L12,
L15 (dd8, s7469 hold300), L16. Queued: soak_queue/s7470_asan_lv_b (L3 dd8, L5, L6 dd8), _c (L8, L9 dd8, L10), _d (L11 dd8, L13,
L14 dd8), _e (L17, L18 dd8), HOLD=220.

Fold first: each verdict line in SOAK-RESULTS + scratch/s7470_asan_lv_<x>/san_report.txt and the "arm=lN initMission=" lines.
Exit 0 = PASS + 0 NEW; 1 = NEW group -> read scratch/s7470_asan_lv_<x>/san_lN.* stack, name the writer, fix it (ORIGIN line),
or add it to tools/s7467_san_reviewed.tsv only with a reason; 3 = control FAIL (instrument blind: rerun, no verdict).
If a recipe is still queued and the host is idle (HID idle > 180 s, screen unlocked), run it in-session:
  zsh scratch/agent/soak_queue/s7470_asan_lv_b.sh > scratch/agent/soak_results/s7470_asan_lv_b_manual.log 2>&1  (move it out of the queue first)
Unreached arm (initMission=0): re-queue it alone at HOLD=300:
  zsh tools/s7470_gen_asan_lv.zsh s7471_asan_lv_reN 300 N:dd
Hypotheses per arm: H-lv-clean / H-lv-hit / H-lv-unreached. Close EA when all 19 levels have a flown ASan arm and every recipe's
plant arm passed; then write the class EA close line in CURRENT-TRUTH and pick the next ladder item (3b/3c) for NEXT.md.
