# NEXT: G1c phase 2 on the -O2 build - find the next binding limit above dd4
HYPOTHESIS-ID: g1c-phase2-o2-limit

s6700: -O2 is the default build (build/ rebuilt). lvl5 dd4 now ~30 game tasks/s. Phase 2 asks how far dd goes.
Hypotheses for the next limit: H-cost (gfx task / game thread time drops below 30 tasks/s at dd6 or dd8),
H-table (64-wide terrain table / cell cap saturates by dd6 - s6575/s6577 - so dd8 adds nothing visible),
H-fault (rare dd4/dd8 gfx SIGBUS, dd8 hangar garbage - parked, may reappear), H-fps60 (FPS60 at dd4 is now affordable).
One batch, sequential runs on build/ (ROGUESQ_G1B=1 ROGUESQ_STORE_DIAG=0, HOLD_S=300, LEVEL=5):
  dd4, dd6, dd8 (DD_UNSAFE=1 for >3), and dd4 + ROGUESQ_FPS60=1; recipe:
  env ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA="ROGUESQ_STORE_DIAG=0 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=6 " HOLD_S=300 LEVEL=5 TAG_SUFFIX=s6701_dd6 zsh scratch/agent/g1_level_coverage_common.zsh
Per arm: mission-phase tasks/s + gfx ms (awk over [g1b] lines, t>100), crash/stall, terrain fraction scorer and a
contact sheet of the same-index fb dumps. Outcomes: first arm < 30 tasks/s names H-cost (then profile that thread);
dd6==dd8 terrain fraction names H-table (lift the 64-wide stride next); a fault -> backtrace that one.
