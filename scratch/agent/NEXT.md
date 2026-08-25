# NEXT work unit (s2349) — M5 `data_ptr+0x100` writer provenance

HYPOTHESIS-ID: m5-dataptr100-writer-provenance

## Work unit

Run one fresh ground-truth-first retail census for the already observed
`0x80090CA4` writer and the two known task pointers/destinations, then one
same-build four-arm port table using the existing task-field snapshot, DMA,
and ordering probe. Keep `ROGUESQ_M5_B40_VALUE=0`, C88 opt-in, the qualified
LLE route, the eleven-Start schedule, title `1024 @ 0x00790400`, hangar
`512 @ 0x006AB400`, and SIGKILL cleanup. Do not write back the field, change
task data, change a consumer or default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-RetailDataPtr100PortAbsent: retail `0x80090CA4` writes the exact
  `data_ptr+0x100` destinations in the target phases, while both port C88=1
  treatment arms have no matching field-write event or pre/post change before
  their ABI snapshot.
- H-PortDataPtr100WriterPresent: the port field observer records a matching
  write event strictly between task begin and ABI capture, and the field
  changes in at least one qualified treatment arm.
- H-RetailKnownDestNotAudioOutput: retail's phase-matched
  `0x80090CA4` writes do not remain joined to the same task pointers and
  `data_ptr+0x100` destinations under the task-block controls; the known
  writes are another task-buffer operation.
- H-CoverageInvalid: any whole-RDRAM, task-block, exact-destination,
  title/hangar, named-PC, or four-arm port control is absent.

The discriminator is one table keyed by
`(arm,c88,phase,width,origin,retail_writer_pc,retail_task_ptr,retail_dest,
retail_value,task_n,data_ptr,data_ptr_plus_100,field_phys,field_pre,
field_post,field_write_event,field_write_dram,field_write_len,task_begin,
task_end,abi_event,dma_event,dma_dest,dma_len,ordering)`. Select
H-RetailDataPtr100PortAbsent only when retail has positive task-block and
exact-destination controls showing the writer/destination relation and both
C88=1 arms have no matching port event/change. Select
H-PortDataPtr100WriterPresent only when a matching port event is positive and
strictly precedes ABI capture with a changed field. Select
H-RetailKnownDestNotAudioOutput only when retail's writer and task-pointer
rows fail the exact relation under positive controls. Otherwise select none
and keep the contract open.

## Exact commands

Run the independent retail witness before adding or changing any port
instrument:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --watch-write 0x141AD0:0x141AF0 --hit-cap 64 --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 2 --post-value-watch 3 --post-value-pc 0x80090CA4 --post-value-pc-detail --watch-pc 0x80090CA4,0x80094648,0x800078EC,0x80090CA4,0x8008EC88,0x8009123C,0x8009142C,0x80091454,0x80091468,0x80091484,0x80091544,0x800915F8,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2349_m5_dataptr100_writer_oracle.log 2>&1
    zsh -n scratch/agent/run_s2349_m5_dataptr100_writer.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2349_m5_dataptr100_writer.sh s2349_m5_dataptr100_writer

The new driver must launch all four arms from `build/`, require every
positive control in every arm, and write one phase/task/write-order table
under `scratch/agent/s2349_m5_dataptr100_writer/`. Use the existing
`audtask-field-snapshot-control` as the field-read positive control and the
image-only generic DMA-observer control for image arms; a silent-arm zero DMA
count is expected and is not a coverage failure. A null without the retail
task-block/exact-destination controls is H-CoverageInvalid, not evidence.
