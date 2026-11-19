# NEXT (s7674)
HYPOTHESIS-ID: g6c-standin-handoff-polish

s7673 closed the s7614_hm census OPEN row (census PASS 8/8). First: `python3 tools/crash_reports.py --since 2026-11-13`
(a NEW report outranks everything), then any owner report.
Unit: G6c handoff polish (CURRENT-TRUTH item 20, s7672). Question: after ROGUESQ_S7672_HOLD, does a held stand-in that is
culled by our own view test while the real object is also culled ever leave a visible gap ON SCREEN? Hypotheses: H-offscreen
(every held-stand-in cull frame coincides with the real object failing the game's view test = off-screen, not a defect) vs
H-gap (some frames: real object not yet accepted, stand-in culled, object inside the view frustum -> visible blink).
Discriminator: in scratch/s7672/run.zsh logs, per spawn, join held-stand-in cull frames with the real object's view-test exit
reason (s7625 tally) and its screen position; any in-frustum frame selects H-gap. Same-run control: the s7672 HOLD=0 arm
(must show blinks). If H-offscreen, record and close; then the next owner item.
One game at a time, SIGKILL only, never touch build/saves, <=2 CPU-heavy jobs, no repeat-hold soaks.
