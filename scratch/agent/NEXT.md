# NEXT work unit (s1166)

HYPOTHESIS-ID: pre1024-copytoram-source

The s1164/s1165 pair establishes a valid reachability split: both runs had
writeback activity and wild-width skips, but only s1164 reached the pre-1024
RT64 `copyToRAM` fault. Audit the existing RT64 resource/failure markers in one
phase-gated run. Do not add a skip, guard, or restore; any mitigation-shaped
change requires an `ORIGIN:` writer attribution and legitimacy assessment.

Competing hypotheses and discriminator:

- H1: the `copyToRAM` fault is preceded by a distinct RT64 resource/operation
  failure marker that is absent from the stable arm.
- H2: the fault is caused by writeback state, but the current `[ost-wb]` rows
  do not identify the relevant resource transition.
- H3: the fault remains nondeterministic with no reproducible preceding marker.

The discriminating measurement is the first resource/failure marker and its
ordering relative to phase-scoped `[ost-wb]` skips/controls, with slot-dispatch
and crash controls live. A null is invalid unless slot dispatch, writeback
positive control, and crash/phase controls all fire.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env GAME_EXTRA_ENV='ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_CRASH=1 ROGUESQ_LOG_OST_WB=1 ROGUESQ_LOG_RT64_ALLOC=1' PROBE_MODE=start_only HOLD_S=0 CAPTURE_TICK_S=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh copytoram_s1166 240 12

Expected outcomes: a reproducible resource marker before `copyToRAM` selects
H1; writeback-only correlation selects H2 provisionally; and another valid
stable/crash split with no marker selects H3 and closes this marker audit.
