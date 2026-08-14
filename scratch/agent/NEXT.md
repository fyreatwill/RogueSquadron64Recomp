# NEXT work unit (s1167)

HYPOTHESIS-ID: pre1024-failure-source

Audit the existing pre-1024 host/RT64 operation markers around guest PC
`0x8000B650` in one phase-gated run. Do not add a skip, guard, restore, or new
counter. Use the existing crash, slot-dispatch, writeback, DPC, and RT64
operation/resource categories; attribute the first marker after the last
writeback control and before the crash.

Competing hypotheses and discriminator:

- H1: a DPC/RT64 operation marker identifies a specific operation immediately
  before the pre-1024 failure.
- H2: the host Metal/compiler failure is independent of the guest writeback
  stream and has no preceding RT64 operation marker.
- H3: the run stays stable or fails in another host operation, so the current
  `0x8000B650` family is nondeterministic and not classifiable from this arm.

The discriminating measurement is the ordered marker window from the final
phase-scoped `[ost-wb]` row through `[CRASH][last-guest-pc]`, with slot,
writeback, and crash positive controls live. A specific preceding operation
selects H1; a valid crash with no operation marker selects H2; a valid stable
arm or different failure selects H3. A null is invalid unless all controls
fire.

Exact commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env GAME_EXTRA_ENV='ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_CRASH=1 ROGUESQ_LOG_OST_WB=1 ROGUESQ_LOG_DPC=1 ROGUESQ_LOG_RT64_ALLOC=1' PROBE_MODE=start_only HOLD_S=0 CAPTURE_TICK_S=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh pre1024_source_s1167 240 12

Expected outcomes: classify the first ordered host operation marker before a
reproduced fault, or record a valid control-passing stable/different-failure
arm as H3. No mitigation is authorized by this work unit.
