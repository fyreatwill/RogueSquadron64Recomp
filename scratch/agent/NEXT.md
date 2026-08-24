# NEXT work unit (s2241) — compare field348 producer PCs

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Ask the retail oracle for the known field348 producer-PC range before adding a
port instrument, then add one fixup that annotates every generated scalar
store instruction in `0x80090F8C`–`0x80091000` with its static guest PC and
passes the live destination/value to a phase-gated host census. Include every
store site in the range, even stores outside the active source spans; the
fixup must report the complete enumeration and refuse a partial match. Keep
the s2240 callsite, scalar-writer, image-stage, DMA, ABI, and PCM controls in
the same build and run. Observation only: do not rewrite the source, image
task, writeback, consumer, or defaults.

## Ground truth before instrumentation

Run the retail ROM with the whole-RDRAM positive control first, exact source
watches, and an execution watch over the known retail producer range:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 180 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --watch-write 0x0:0x800000 \
  --watch-write 0x178C80:0x178E00 \
  --watch-write 0x1797B0:0x179930 \
  --watch-pc-range 0x80090F8C:0x80091004 \
  --vi-trace --hit-cap 64 \
  > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/oracle_s2241_field348_producers.log 2>&1
```

The whole-RDRAM watch must reach 10,000 callbacks and the VI trace must reach
title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` before any port null
is interpreted.

## Competing hypotheses and discriminating measurement

- **H-PortWriterAbsent:** retail executes the producer range at the target
  phases, but the port has no matching target-phase store execution. This
  selects a missing or disabled producer edge.
- **H-PortWriterZero:** the port executes the matched producer sites at the
  active source but writes only zero values. This selects a producer-payload
  defect, not a wrong clear or consumer defect.
- **H-PortWriterWrongDestination:** the port executes matched sites with
  nonzero values, but their computed destinations miss the active `field348`
  span or populate only the inactive origin. This selects an address/order
  contract mismatch.
- **H-PortWriterThenZero:** a matched nonzero store reaches the active span
  before the first matching image stage and a later zero clear erases it. This
  selects a post-producer clear ordering defect.
- **H-CandidateInstrumentGap:** the complete static store enumeration or its
  outside-span positive control is absent, so no writer conclusion is valid.

The discriminator is one table keyed by
`(phase,width,origin,writer_pc,store_pc,dst,value,value_nz,store_ordinal,
memset_ordinal,first_matching_stage)`, joined to the oracle writer-PC range
and the existing image-stage source hashes. A target-phase row for every
candidate is not required, but the known retail PCs, the port outside-span
control, route, ABI, DMA, image-stage, and PCM controls must all fire. A null
without those controls is instrumentation failure, not H-PortWriterAbsent.

## Build and run

```sh
env RS64_S2241_FIELD348_PRODUCERS=1 python3 fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_M5_FIELD348_WRITER=1 ROGUESQ_LOG_M5_FIELD348_MEMSET=1 ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2241_field348_producers 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2241_field348_producers_driver.log 2>&1
```

Run the fixup command from `/Users/williambuckley/Documents/Tools/N64Recomp`
and the build/run commands from the project root. If the known pre-target or
post-hangar crash recurs before the target table, rerun the unchanged build
and arm once; do not interpret the failed route attempt.
