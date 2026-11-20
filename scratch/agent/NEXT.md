# NEXT (s7688)
HYPOTHESIS-ID: g6c-owner-sheet-refresh

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7687 CLOSED the g6c-pos-fallback-neighbour thread (0x0C added, ROGUESQ_S7687_POSSUB; 0x24/0x2E/0x46 no itemless callers).
The owner sheet docs/owner_sheet_s7630_standins_on_off.jpg predates every handoff change since (s7672 hold, s7681 shield,
s7684 ray-shield key, s7685/s7686/s7687 pos rejects). Work unit: regenerate it on the current binary.
  zsh scratch/s7628_standins_proof.sh   # same-run STANDINS=frame toggle + dumps, arms L1 dd2 / L1 dd4 / L4 dd2 / L4 dd4 (read it first;
                                        # point its output dir at scratch/s7688 rather than overwriting s7628)
  python3 tools/s7628_standins_sheet.py --cluster 16 --control --pairs 3 <arm dirs>  -> docs/owner_sheet_s7688_standins_on_off.jpg
Expected: control PASS (>=288 of 576 synthetic px) in every arm, med_fpx of the same order as s7630 (bunker ~153, towers ~1298).
A big drop -> the handoff changes made stand-ins vanish earlier (regression; bisect with S7672_HOLD/S7685/S7686/S7687 =0 arms in
one run). Then update OWNER-OPT-INS row to point at the new sheet and wait on the owner's look (default stays off).
One game at a time, SIGKILL only, <=2 CPU-heavy jobs. Screen must be unlocked for the key-driven harness.
