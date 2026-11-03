# NEXT: fold the s6833 lives witness soak, then the next ladder rung
HYPOTHESIS-ID: g1e-fps60-tick-unfix-witness

Context: s6833 moved 800FB4F8 (lives decrement in the respawn routine tickMissionTransitionAndTeardown) to UNFIX in
tools/fixup_fps60_ticks.py, static-only. Queued scratch/agent/soak_queue/s6833_lives_fps60_lvl14.sh (lvl14 FPS60 400 s,
ROGUESQ_LIVES_CAP=9 logs every lives change, ROGUESQ_TICK_TRACE).
Step 1: read SOAK-RESULTS tail + scratch/agent/soak_results/s6833_lives_fps60_lvl14_*.log.
Hypotheses / outcomes:
- H-respawn-path-hit: fb4f8>0 rows, each followed by a lives change of exactly -1 -> UNFIX runtime-confirmed (2nd line).
- H-other-death-path: lives changes >0 but fb4f8=0 -> deaths go through requestMissionTransitionMode only; the
  0x380000 respawn path is a different death kind (find which flag bit sets it: grep stores to 0x80137F3C with
  0x0008/0x0010/0x0020 << 16) - note it, do not chase further.
- H-no-death: lives_changes=0 (no [livescap] lines at all, or only the initial value) -> the run never died; the
  instrument is unproven (no positive control). Do not conclude anything; skip.
Step 2: all backlog items wait on the owner (FPS60 feel, G1d sheets). Take the next ladder rung that is engineering, not
the G5 rename sweep (iron rule 14 counts renames as churn): e.g. G3 render fidelity in-flight frame diffs.
