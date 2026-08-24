# NEXT work unit (s2240) — annotate all rs_memset callsites

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Add one incremental fixup that annotates every generated direct call to
`rs_memset(rdram, ctx)` with the guest callsite PC from its preceding
instruction comment, then passes that static callsite and the live `$a0/$a1/$a2`
arguments to the existing phase-gated host attestation. Require the fixup to
enumerate and patch the complete callsite set, rather than silently accepting
a partial match. Keep the s2238 scalar-store, image-stage, ABI, DMA, PCM, and
s2239 outside-span controls in the same build and run. Do not alter the clear,
task fields, image dispatch, writeback, consumer behavior, or defaults.

The host output must remain diagnostic-only and bounded by target phase and
call count. Preserve the existing entry `$ra`/`guest_pc` fields, but treat
them as a measured calling-convention control; the new static callsite is the
caller discriminator. Emit at least one target-phase callsite control outside
both exact spans and fail the interpretation if that control is absent.

## Competing hypotheses and discriminating measurement

- **H-InitCallsite:** each active source span is cleared by a stable setup/init
  callsite with fill `0` and length `0x298` before its first matching stage;
  the clear is legitimate initialization and the next producer edge is still
  missing.
- **H-WrongPhaseSpanCallsite:** an exact-span clear comes from a distinct
  phase/consumer caller, repeats after a matching stage, or applies the wrong
  source span for the active origin. This selects a port-side caller/order
  contract defect; do not mitigate it yet.
- **H-MissedProducer:** the annotated clear is a normal init callsite and no
  nonzero exact-span scalar writer precedes the matching stage. This selects a
  missing/disabled producer edge rather than a wrong clear.
- **H-CallsiteInstrumentGap:** all route, scalar-store, image-stage, ABI, DMA,
  and PCM controls fire, but the all-callsite annotation misses its outside-
  span control or cannot join the exact clear to a static callsite. Fix the
  instrumentation before interpreting the source boundary.

The discriminator is one table keyed by
`(phase,width,origin,field348_span,static_callsite,dst,fill,len,call_ordinal,first_matching_stage,first_nonzero_store)`, joined to the existing image-stage source/hash rows and s2238 scalar-store ordinal. A stable pre-stage init row, a repeated/post-stage row, a wrong-span/origin row, and a valid init with no nonzero producer select different hypotheses. A null is valid only with the outside-span callsite control plus the existing route, ABI, DMA, image-stage, scalar-writer, and PCM controls.

## Build and run

```sh
env RS64_S2240_FIELD348_CALLSITES=1 python3 fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2240_field348_callsites 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2240_field348_callsites_driver.log 2>&1
```

Run the fixup command from `/Users/williambuckley/Documents/Tools/N64Recomp`
and the build/run commands from the project root. Use SIGKILL handling from
the recipe; do not run a cross-run A/B or enable any runtime mitigation.
