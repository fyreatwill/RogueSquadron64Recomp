# NEXT work unit (s2346) — M5 task-output/PCM handoff provenance

HYPOTHESIS-ID: m5-c88-task-output-gap

## Work unit

Run one fresh ground-truth-first, same-build four-arm census of the opt-in C88
treatment:

| audio arm | C88 | treatment |
|---|---:|---|
| stub | 0 | control |
| stub | 1 | C88 nonzero |
| image | 0 | control |
| image | 1 | C88 nonzero |

Keep `ROGUESQ_M5_B40_VALUE=0` and make no writer, task-data, consumer, guard,
or default change. Retain the eleven-Start schedule, title
`1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, SIGKILL cleanup, and every
s2345 positive control. `ROGUESQ_LOG_AUDIOTICK_TRACE=1` remains mandatory.

## Competing hypotheses and discriminating measurement

- H-OutputMetadataWriterAbsent: C88=1 reaches the audio-task ABI and CPU
  voice work, but `output_buff`/`output_buff_size` remain zero in the same
  route ordinal and no output metadata writer fires.
- H-DmaRangeDoesNotPublish: C88=1 supplies nonzero output metadata, but the
  task's generated DMA ranges have no same-ordinal output overlap or point at a
  different destination, so no PCM source is published.
- H-PcmPublicationNoConsumer: C88=1 has same-ordinal output metadata, a valid
  overlapping DMA/source event, and a completed task, but the PCM consumer is
  absent, mismatched, or ordered before publication.
- H-OrdinalJoinMisclassified: the output and PCM events exist, but the current
  route ordinal is not the join key; an event-sequence/phase join exposes a
  same-task publication that the ordinal table lost.

The discriminator is one table keyed by
`(audio_arm,c88,phase,width,origin,writer_seq,branch_event,route_ordinal,
route_row,abi_event,output_buff,output_buff_size,task_complete,dma_event,
dma_dest,dma_len,output_overlap,source_event,consumer_event,ordering)`, with
one row for every restored C88=1 route ordinal and matched C88=0 controls. Do
not interpret a null until the fresh retail whole-RDRAM, target-window,
title/hangar, status/queue, and named-PC controls pass and all four port arms
have title/hangar, task/DMA, guest-receive, PCM, filter, render, key-on, and
callback-helper controls. Select H-OutputMetadataWriterAbsent only if the
metadata writer and fields stay zero; select H-DmaRangeDoesNotPublish only if
metadata is nonzero but same-ordinal DMA/output overlap and source remain
absent; select H-PcmPublicationNoConsumer only with a same-ordinal source and
consumer mismatch; select H-OrdinalJoinMisclassified only with an independent
event-sequence join that restores publication. Otherwise select none and keep
the task-output boundary open.

## Exact commands

Run the independent retail witness before the port build/run, using the s2345
recipe and its positive controls:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x165000:0x16B000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x141AD0:0x141AF0 --watch-write 0x1498A:0x1498C --watch-write 0x154620:0x154624 --watch-write 0x11A8A4:0x11A8B4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 2 --post-value-pc 0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48 --post-value-pc-detail --watch-pc 0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48,0x8009123C,0x8009142C,0x80091454,0x80091468,0x80091484,0x80091544,0x800915F8,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --pc-phase-log-width 0x006AB400:512 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2346_m5_task_output_oracle.log 2>&1
    zsh -n scratch/agent/run_s2346_m5_task_output_provenance.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2346_m5_task_output_provenance.sh s2346_m5_task_output_provenance

The new driver must launch all four arms itself from `build/`, write its
phase/ordinal table under
`scratch/agent/s2346_m5_task_output_provenance/`, and kill every game process
with SIGKILL after the required hangar capture. If any required control is
missing, stop as H-CoverageInvalid rather than interpreting a null.
