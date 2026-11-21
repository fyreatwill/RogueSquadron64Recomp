# NEXT (s7736)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'` (a NEW report outranks everything; the full output is
100+ KB, filter it), then any owner report, then any new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, ~10+ min, background, CPU cap 2). Note: zsh `time` prints "... total", not "real".

Closed, do not repeat: s7726-s7734 census passes; s7735 replay reproduces the compiled readings (reader census now inside s7719).

Candidate bounded item if nothing above applies: the 18 live-only reader occurrences (s7735 getenv text diff, live vs replay)
are hand edits no fixup reproduces (CLAMPP s6522, FORFACE_LOG, LOG_ALL x2, EDGE_FADE_TEST2, LOG_G1D_TASK, LOG_M5_FIELD348_WRITER,
LOG_M5_WRITER_PARITY, LOG_SUBMIT_GATE_STORES, POOLWATCH, DRAW_DISTANCE x4). Hypotheses: H-dead-probe (all diagnostic, safe to drop
from live at the next regen: nothing reads them in OWNER-OPT-INS / tools/agent recipes) vs H-needed (a recipe or soak still sets
one, so the regen silently loses an instrument it relies on). Discriminator: grep every name across tools/, scratch/agent/soak_queue,
docs/OWNER-OPT-INS.md; the DRAW_DISTANCE x4 rows need reading (owner knob, must not be live-only behaviour). Kept tree:
scratch/s7735/gate/replay. Fix = add the needed apply script to RS64_REPLAY, or record the probe as dead.
