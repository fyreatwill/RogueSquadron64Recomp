# NEXT (s7707)
HYPOTHESIS-ID: g1d-219-postg6c-rehold

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.

1. Fold the queued soaks s7706_219_rehold_L15 / _L4 / _L1 (SOAK-RESULTS + scratch/s7706_219_L*): 300 s, ROGUESQ_ASPECT=21:9 dd2
   STANDINS=1 FPS60 fullscreen. Each prints a g1e_owner_quiet_arms tag line + `s7706 L<n> aspect219_lines= standins_on_line= spawns=`.
   Hypotheses: H-clean (post-G6c 21:9 = 16:9 result, 3/3 alive, vi_stalls30s=0) / H-219-regress (stand-ins or the G6 changes break at
   21:9: crash, stall, or standins_on_line=0) / H-void (aspect override did not apply: check the log for the 21:9 FB_WIDTH/aspect line;
   if aspect219_lines=0 grep the log for `[aspect]`/`FB_WIDTH` by hand before scoring).
   If the soaks have not run (idle gate), run L15 in-session: `zsh scratch/agent/soak_queue/s7706_219_rehold_L15.sh`.
   A crash = G4 side-effect datum: capture the .ips / backtrace and name the writer.
2. If all clean: every ladder rung is closed or with the owner. Run the standing health check `python3 tools/s7651_gate_sweep.py`
   (--jobs 2) and fold it (expect 130 GREEN, 0 RED); a RED is the next work unit.
