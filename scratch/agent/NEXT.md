# NEXT work unit (s2239) — rs_memset caller/argument/order audit

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Add one phase-gated host attestation at the generated `rs_memset` entry
(`0x800078E0`), recording `$a0` destination, `$a1` fill byte, `$a2` length,
`$ra`/callsite, target phase/origin, and a monotonic call ordinal. Keep the
s2238 scalar-store, image-stage, ABI, DMA, and PCM controls in the same build
and run. Join each overlapping call to the existing image-stage row by
phase/origin and source span; do not alter the clear, task fields, image
dispatch, writeback, consumer behavior, or defaults.

The hook must also emit one target-phase `rs_memset` positive-control call
outside both exact spans. If the incremental fixup is applied to generated
files, add the hook to `fixup_game_funcs.py` and use the script's guarded
incremental path; do not hand-edit generated output. The host hook should
remain diagnostic-only and bounded by phase and call count.

## Competing hypotheses and discriminating measurement

- **H-ExpectedField348Init:** overlapping `rs_memset` calls use a zero fill and
  cover the source spans before the first matching image-stage row, with no
  later overlapping clear. The zero source is an initialization boundary;
  inspect the preceding producer/caller contract next.
- **H-WrongClearAfterProducer:** an overlapping clear occurs after a matching
  task/image-stage event or repeats during the target task stream. This selects
  a port-side clear ordering/caller contract defect; do not mitigate it yet.
- **H-MissedBulkWriter:** the call attestation has no overlapping call, while
  the s2238 scalar writer rows remain positive. This selects a different
  producer path or a bulk-write boundary missing from the current join.
- **H-CallsiteOriginSplit:** the two active field348 sources have different
  destination, fill, length, or callsite/order patterns. Keep the next
  producer analysis origin-keyed rather than combining the two spans.
- **H-MemsetInstrumentGap:** the target route and s2238 writer/stage controls
  fire but neither an outside-span call control nor ordered `rs_memset` rows
  appear. The attestation is unevaluable and must be fixed before interpreting
  exact-span nulls.

The discriminator is one table keyed by
`(phase,width,origin,field348_span,dst,fill,len,callsite,call_ordinal)`, joined
to `audtask-image-stage` `field348/field348_nz`, stage ordinal/row, and the
s2238 store ordinal. A clear before the first stage row, a clear after a stage
row, a no-call/positive-store split, and an origin-specific call pattern each
select different hypotheses. A null is valid only with the outside-span
`rs_memset` control plus the existing ABI, DMA, image-stage, and PCM controls.

## Build and run

```sh
env RS64_S2239_FIELD348_MEMSET=1 python3 fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2239_field348_memset 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2239_field348_memset_driver.log 2>&1
```

Run the fixup command from `/Users/williambuckley/Documents/Tools/N64Recomp`
and the build/run commands from the project root. Use SIGKILL handling from
the recipe; do not run a cross-run A/B or enable any runtime mitigation.
