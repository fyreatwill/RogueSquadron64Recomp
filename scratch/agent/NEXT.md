# NEXT work unit (s2347) — M5 output-metadata writer provenance

HYPOTHESIS-ID: m5-c88-output-metadata-writer-provenance

## Work unit

Run one fresh ground-truth-first census of the same four arms:

| audio arm | C88 | treatment |
|---|---:|---|
| stub | 0 | control |
| stub | 1 | C88 nonzero |
| image | 0 | control |
| image | 1 | C88 nonzero |

Keep `ROGUESQ_M5_B40_VALUE=0`, C88 opt-in, the eleven-Start schedule, title
`1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, SIGKILL cleanup, and every
s2346 positive control. Do not promote a writer, write back `data_ptr+0x100`,
change task data, change a consumer, change a default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-RetailOutputWriterPortZero: retail writes a legitimate task/output field
  or destination relation in the target phase, but the port's corresponding
  task ABI fields remain zero.
- H-RetailStageOnlyLegitimate: retail also leaves the output field zero on
  this route; the known `data_ptr+0x100` writer and stage-only DMA are not the
  missing PCM publication contract.
- H-PortMetadataLostOrdering: the port writes nonzero output metadata at task
  construction, but a task-copy/publication ordering edge makes the image ABI
  observe zero before dispatch.
- H-DataPtr100Unrelated: the retail `data_ptr+0x100` writer is real but is not
  the output field for this audio task; no phase/task join connects it to the
  missing publication.

The discriminator is one table keyed by
`(arm,c88,phase,width,origin,task_n,route_ordinal,task_ptr,data_ptr,data_size,
output_buff,output_buff_size,field_writer_seq,writer_pc,writer_value,
data_ptr_plus_100_writer,dma_event,dma_dest,dma_len,output_overlap,
task_complete,source_event,consumer_event,ordering)`. The retail half must
include the whole-RDRAM positive watch, target/output-span writer sequence,
title/hangar, status/queue, and named-PC controls. The port half must include
all four title/hangar, task/DMA, guest-receive, PCM, filter, render, key-on,
and callback-helper controls. Select H-RetailOutputWriterPortZero only when
retail has a phase-matched legitimate writer/value and every corresponding
port ABI field is zero. Select H-RetailStageOnlyLegitimate only when retail's
independent phase-matched task/output rows are also zero. Select
H-PortMetadataLostOrdering only when a port writer sequence is nonzero before
the ABI snapshot but the snapshot is zero. Select H-DataPtr100Unrelated only
when the known writer is positive but cannot be joined to either task ABI or
DMA output. Otherwise select none and keep the output boundary open.

## Exact commands

Run the independent retail witness before the port build/run:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x165000:0x16B000 --watch-write 0x141AD0:0x141AF0 --watch-write 0xA0F50:0xA0F54 --watch-write 0x1498A:0x1498C --watch-write 0x154620:0x154624 --watch-write 0x11A8A4:0x11A8B4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 2 --post-value-pc 0x800078EC,0x80090CA4,0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48 --post-value-pc-detail --watch-pc 0x800078EC,0x80090CA4,0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48,0x8009123C,0x8009142C,0x80091454,0x80091468,0x80091484,0x80091544,0x800915F8,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --pc-phase-log-width 0x006AB400:512 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2347_m5_output_writer_oracle.log 2>&1
    zsh -n scratch/agent/run_s2347_m5_output_writer_provenance.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2347_m5_output_writer_provenance.sh s2347_m5_output_writer_provenance

The new driver must launch all four arms itself from `build/`, write one
phase/task/writer table under
`scratch/agent/s2347_m5_output_writer_provenance/`, and SIGKILL every game
after the required hangar capture. If any required control is missing, stop
as H-CoverageInvalid rather than interpreting a null.
