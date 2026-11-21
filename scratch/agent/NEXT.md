# NEXT (s7751)
HYPOTHESIS-ID: farmax-second-source
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
G6c coverage is CLOSED on L1/L10/L12 (s7750). Next rung: CURRENT-TRUTH Next-steps item 3 (s7310 21:9 left-edge sliver, ROGUESQ_DD_FARMAX
default 32767) rests on a single-source mechanism: "far above ~36-40k units makes the F5 clip pin sky-dome edge panels to fb x=0".
Unit (offline first, one game run max): grep PORTING-STATE s7308-s7312 for the logged vertex/matrix inputs and the RDP W decode tool.
Re-run the F5 vertex transform + clip for those inputs in a small python model, written from docs/F5-UCODE-REFERENCE.md and GLideN64's F5 HLE
(the reference math, not our RSP), at far 32767 and 40000.
Hypotheses / outcomes:
- H-ucode: the reference math also pins x=0 above the threshold (fixed-point W / clip-ratio overflow) -> the mechanism is the game's own,
  FARMAX stays the right fix, item 3 is two-source.
- H-rspemu: the reference math does NOT pin -> our LLE vector-op emulation (VRCP/VMACF clamp) diverges; bisect the op on those inputs.
- H-input: the logged inputs are not enough to reproduce (missing matrix) -> one capture run at L5 21:9 dd4 with FARMAX=0 that dumps
  the vertex+matrix for the pinned panel, then rerun the model.
