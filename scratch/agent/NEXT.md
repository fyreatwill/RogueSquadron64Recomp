# NEXT (s7756)
HYPOTHESIS-ID: hangar-hstate-visibility-gate
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7755 CLOSED the hangar mid-task DL rewrite as not visible (CURRENT-TRUTH item 27): live == end-image render <=1 LSB on 20/20
H-state pairs (dd1 + 16:9 dd2 FPS60), begin-vs-live <=3 LSB on <=313 px. The s7753 RDP-output gate excludes hangar tasks, so a
future ucode/RDP change could make the hangar visibly torn without any gate noticing.
Unit (offline, no game run): wire tools/s7755_hstate_visibility.py into tools/s7651_gate_sweep.py as a retained-input gate:
- inputs scratch/s7754/retained/hangar_hstate/k900_s1250.bin (--cap 65536 --tg 0) and
  scratch/s7754/retained/hangar_hstate_dd2/k900_s1500.bin (--cap 1048576 --tg 1);
- add a mode (e.g. --gate) that checks live-vs-end ge2LSB == 0 (the property that matters; begin-vs-live may legitimately be
  2-3 LSB) plus both controls, prints `NEEDS-INPUT` if a pair is missing and `VERDICT GREEN 2/2` otherwise;
- register it like s7753 (NEEDS-INPUT regex row + EXTRA_GATES + expected-output regex); prove it goes RED with a control
  (e.g. --cap 2048 truncates the stream -> live-vs-end must differ) and GREEN at the real policy; then run the full sweep (--jobs 2).
Hypotheses: H-green (gate GREEN 2/2 on the current tree, as s7755 measured) / H-drift (already RED: tree changed since s7755).
Max 2 CPU-heavy jobs.
