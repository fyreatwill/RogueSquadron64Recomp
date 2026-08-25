# NEXT work unit (s2351) — all-PC attribution of the hangar `0x173C20` field

HYPOTHESIS-ID: m5-dataptr100-writer-provenance

## Work unit

Run one fresh retail all-PC exact-destination census for `0x00173C20` in the
512/hangar phase, retaining `0x00171DE0` and the known candidate PCs as
positive controls. Then run one same-build four-arm port table by extending
the s2350 driver/parser to derive every positive hangar writer PC from the
oracle's `writer-pc-phase` rows. Canonicalize `0x006AB400` and `0x006AB800` to
the same hangar phase. Do not write either field, alter task data, change a
consumer or default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-RetailHangarFieldWriterPresent: with all retail controls positive, one or
  more writer PCs are phase-attributed to exact `0x00173C20` writes in the
  512/hangar bucket; the matching writer scope is then joined to the existing
  four-arm field snapshot/DMA/order table.
- H-RetailHangarFieldUnwritten: with all controls positive and the
  `0x00171DE0` exact-writer control firing, no writer PC is phase-attributed to
  `0x00173C20` in hangar; the field is not written during this retail capture
  phase and its task-buffer role remains open.
- H-PortHangarFieldWriterPresent: a qualified C88=1 port arm has a changed
  computed field plus an `audtask-field-write` event strictly between task
  begin and ABI capture, regardless of the retail result.
- H-CoverageInvalid: whole-RDRAM, task-block, both exact-field watches, both
  title/hangar phase histories, named-PC controls, or any of the four port
  controls fail.

The discriminator is one table keyed by
`(phase,width,origin,field_phys,retail_writer_pc,retail_writer_rows,arm,c88,task_n,data_ptr,data_ptr_plus_100,field_pre,field_post,field_write_event,field_write_dram,field_write_len,task_begin,task_end,abi_event,ordering)`. Select H-RetailHangarFieldWriterPresent only when a positive all-PC retail row exists for exact `0x173C20` in the canonical hangar phase and the controls pass. Select H-RetailHangarFieldUnwritten only when the controls pass, the `0x171DE0` control has positive hangar writer rows, and the all-PC `0x173C20` phase row is absent. Select H-PortHangarFieldWriterPresent only when a C88=1 port arm has a changed field and a strictly ordered field-write event. Otherwise select none.

## Exact commands

Run the independent retail witness before adding or changing any port probe:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 2 --post-value-watch 3 --watch-pc 0x800078EC,0x800908D4,0x8009081C,0x80090810,0x80090CA4,0x80094648,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2351_m5_hangar_field_writer_oracle.log 2>&1
    zsh -n scratch/agent/run_s2351_m5_hangar_field_writer.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2351_m5_hangar_field_writer.sh s2351_m5_hangar_field_writer

The new parser must derive the retail writer-PC set from every
`writer-pc-phase` row for watch 2, not from the three already known PCs. It
must require the retail whole-RDRAM, task-block, exact-field, phase, and
named-PC controls and require `controls=1` for all four reused port arms. A
silent-arm zero-DMA count remains expected. A null without those controls is
H-CoverageInvalid, not evidence.
