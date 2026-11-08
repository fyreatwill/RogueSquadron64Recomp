# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending (owner questions: CURRENT-TRUTH, and git show HEAD~3:scratch/agent/NEXT.md).

# NEXT: same-run DRAIN toggle at the owner dd4 recipe on a locked 60 Hz built-in
HYPOTHESIS-ID: g1e-present-drain
s6949 (cross-run, 4 arms): default dd4 16:9 FPS60 sits on the ~47 ms level half the time; ROGUESQ_PRESENT_DRAIN=40 holds 33.5/37.5 with 2 drops/240 s.
Hypotheses: H-drain-real (in one run, DRAIN-on blocks read ~30-34 ms and off blocks re-form the level after a stall dose) vs H-run-luck (on and off blocks read alike within a run; the s6949 gap was which level each run entered).
1. Add ROGUESQ_PRESENT_DRAIN_TOGGLE=<sec> in lib/rt64/src/contrib/plume/plume_metal.cpp rs64DrainMs (limit 0 on odd blocks), write a T row to the present ring at each flip; export.sh + commit (lib/ rule).
2. Rebuild (DEVELOPER_DIR set), then: env ARMS="60:4:t4:ROGUESQ_PRESENT_DRAIN=40_ROGUESQ_PRESENT_DRAIN_TOGGLE=20+ST" ... (arm env is whitespace-split: extend the spec parser for multiple vars, e.g. '_' -> ' ' after ROGUESQ_), zsh tools/g1e_owner_hz_arms.zsh. Check owner idle >120 s and only the built-in attached first.
3. Score per block (extend g1e_owner_hz_score.py with --blocks on T rows). Control: off blocks after a stall dose must show the level (acq ~15 ms); if none do, the run did not test anything.
If the XG49V (21:9, 144 Hz) is attached, its unit (git show HEAD~3:scratch/agent/NEXT.md, g1e-present-drain section) comes first. Owner reports override all of this.
Defaults: DRAIN, SKYZ, SCREEN_JOB, INFLIGHT stay opt-in, owner decides.
