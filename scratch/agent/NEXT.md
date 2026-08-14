# NEXT work unit (s1164)

HYPOTHESIS-ID: slot-dispatcher-runtime-origin

The s1163 capture passed the slot positive control but did not reach the
recurring fault: it stayed in the pre-1024 `640→2→640` loop. Perform one
bounded retry of the same runtime-origin audit using the existing phase-gated
driver. Do not add a skip or guard; any wild value requires an `ORIGIN:` writer
attribution and a legitimacy assessment.

Competing hypotheses and discriminator:

- H1: a runtime-side writer corrupts the caller frame/value before the failing dispatcher entry.
- H2: the generated dispatcher prologue observes a legitimate but invalid caller `$sp` due to an ABI transition.
- H3: the crash value is produced inside the dispatcher prologue itself.

The discriminating measurement is a writer-attribution row immediately before
the crash: H1 requires a prior writer and changed value; H2 requires an ABI
transition with no ordinary writer; H3 requires the prologue's own first write
to create the bad value. A null is invalid unless phase, slot-dispatch, and
crash/stack controls all fire.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env GAME_EXTRA_ENV='ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_LOG_SLOT_LINK=1 ROGUESQ_LOG_CRASH=1' PROBE_MODE=start_only HOLD_S=0 CAPTURE_TICK_S=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh slot_origin_s1164 240 12

Expected outcomes: if VI 1024 and the recurring SIGBUS occur, classify the
writer row against H1/H2/H3; if the run again remains pre-1024, record it as
unevaluable and pivot to the highest-information pre-1024 reachability probe.
Do not infer parser or renderer causality from this frame-origin audit.
