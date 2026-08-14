# NEXT work unit (s1165)

HYPOTHESIS-ID: pre1024-writeback-reachability

The s1164 retry passed slot dispatch but did not reach the recurring fault: it
stayed pre-1024 and terminated in RT64 `copyToRAM` at guest PC `0x8000B650`
after wild-width writeback skips. Perform one bounded pre-1024 reachability
audit using the existing phase-gated driver and `[ost-wb]` instrumentation. Do
not add a skip or guard; any wild value requires an `ORIGIN:` writer attribution
and a legitimacy assessment.

Competing hypotheses and discriminator:

- H1: wild writeback state is present before the pre-1024 RT64 crash.
- H2: writeback skips are unrelated and the crash is an independent RT64 resource failure.
- H3: the same pre-1024 path is nondeterministic reachability gating.

The discriminating measurement is a phase-scoped `[ost-wb]` control/skip/
overlap sequence immediately before the crash, with slot-dispatch and crash
controls live. H1 predicts wild skips/overlaps temporally preceding the crash;
H2 predicts no relevant writeback relation; H3 predicts materially different
pre-1024 reachability across the same controlled recipe. A null is invalid
unless slot-dispatch, `[ost-wb]` positive control, and crash/phase controls all
fire.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env GAME_EXTRA_ENV='ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_CRASH=1 ROGUESQ_LOG_OST_WB=1' PROBE_MODE=start_only HOLD_S=0 CAPTURE_TICK_S=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh wb_origin_s1165 240 12

Expected outcomes: if the `[ost-wb]` positive control and crash occur before
VI 1024, classify the temporal relation against H1/H2/H3; if the run reaches
VI 1024, retain the pre-1024 trace and do not infer parser causality. If the
positive control is absent, the run is invalid and the instrument must be
fixed before interpretation.
