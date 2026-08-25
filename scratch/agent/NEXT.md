# NEXT work unit (s2348) — M5 output-field semantic and ordering boundary

HYPOTHESIS-ID: m5-c88-output-metadata-writer-provenance

## Work unit

Run one fresh ground-truth-first retail field dump at the phase-qualified
output-span writer `0x80094648`, then one same-build four-arm port table. Keep
`ROGUESQ_M5_B40_VALUE=0`, C88 opt-in, the eleven-Start schedule, title
`1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, SIGKILL cleanup, and every
s2347 positive control. Do not promote a writer, write back `data_ptr+0x100`,
change task data, change a consumer, change a default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-RetailDataPtr100Output: the retail `0x80094648` writer's live pointer and
  value identify `data_ptr+0x100` output metadata, while the port has no
  corresponding write before its ABI snapshot.
- H-RetailWriterSentinelUnrelated: the retail writer is a sentinel or another
  field; its phase match does not identify the missing output-publication
  contract.
- H-PortMetadataLostOrdering: the port writes the corresponding output field
  before the `audtask-abi` snapshot, but a later task-copy/publication step
  restores zero.
- H-CoverageInvalid: any required whole-RDRAM, target-phase, title/hangar,
  named-PC, or four-arm port control is missing.

The discriminator is one table keyed by
`(arm,c88,phase,width,origin,writer_pc,writer_s0,writer_value,writer_target,
task_n,task_ptr,data_ptr,data_size,output_buff,output_buff_size,abi_event,
field_write_event,task_begin,task_end,dma_event,dma_dest,dma_len,
output_overlap,ordering)`. Select H-RetailDataPtr100Output only when the
retail field dump proves the target relation and both port treatment arms
have no corresponding field-write event before ABI capture. Select
H-RetailWriterSentinelUnrelated only when the retail pointer/value relation
does not match `data_ptr+0x100` under the same phase controls. Select
H-PortMetadataLostOrdering only when a port field-write event is positive and
strictly precedes an ABI row that reads zero. Otherwise select none and keep
the boundary open.

## Exact commands

Run the independent retail witness before adding or building any port
instrument:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x141AD0:0x141AF0 --watch-write 0xA0F50:0xA0F54 --watch-write 0x154620:0x154624 --watch-write 0x11A8A4:0x11A8B4 --hit-cap 64 --pc-hist-watch 1 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 1 --post-value-pc 0x80094648 --post-value-pc-detail --pc-field-dump 0x80094648 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --watch-pc 0x80094648,0x800078EC,0x80090CA4,0x8008EC88,0x8009123C,0x8009142C,0x80091454,0x80091468,0x80091484,0x80091544,0x800915F8,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2348_m5_output_field_semantics_oracle.log 2>&1
    zsh -n scratch/agent/run_s2348_m5_output_field_semantics.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2348_m5_output_field_semantics.sh s2348_m5_output_field_semantics

The new driver must launch all four arms itself from `build/`, add one
phase/task/write-order table under
`scratch/agent/s2348_m5_output_field_semantics/`, require every positive
control in every arm, and SIGKILL every game after hangar retention. A null
without controls is H-CoverageInvalid, not evidence.
