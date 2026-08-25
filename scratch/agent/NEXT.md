# NEXT work unit (s2350) — identify the hangar `data_ptr+0x100` writer

HYPOTHESIS-ID: m5-dataptr100-writer-provenance

## Work unit

Run one fresh ground-truth-first retail exact-destination attribution for the
512/hangar field writers, using the already observed candidates
`0x800908D4`, `0x8009081C`, and `0x80090810`, plus both known task-field
watches. Reuse the qualified s2349 four-arm port field snapshot/DMA table for
the port side; do not add a port probe, write back the field, alter task data,
change a consumer or default, or add a guard in this unit.

## Competing hypotheses and discriminating measurement

- H-RetailHangarWriterMatchesField: with positive controls, the candidate PCs
  are phase-attributed writers to the exact `data_ptr+0x100` destinations in
  the 512/hangar bucket, and the title `0x80090CA4` rows remain a separate
  phase-specific writer.
- H-RetailHangarWriterDifferentDestination: the candidate PC rows are
  positive but do not write either exact task-field destination under the
  task-block and phase join; the exact field writer is another PC or another
  task-buffer role.
- H-PortHangarFieldWriterPresent: the retail candidate set maps to a matching
  port field-write/DMA event strictly between task begin and ABI capture in a
  qualified C88=1 arm of the existing s2349 table.
- H-CoverageInvalid: whole-RDRAM, target-window, exact-field, candidate-PC,
  title/hangar, named-PC, or the reused four-arm port controls fail.

The discriminator is one table keyed by
`(phase,width,origin,field_phys,candidate_pc,retail_phase_pc_hits,retail_post_rows,retail_nonzero,port_arm,c88,task_n,data_ptr,data_ptr_plus_100,field_pre,field_post,field_write_event,field_write_dram,field_write_len,task_begin,task_end,abi_event,ordering)`. Select H-RetailHangarWriterMatchesField only when both 512-phase field destinations have positive exact writer attribution and all controls pass. Select H-RetailHangarWriterDifferentDestination only when controls pass but the candidate rows fail the exact relation. Select H-PortHangarFieldWriterPresent only when a reused C88=1 port row has a changed field and a matching event strictly before ABI. Otherwise select none and keep the boundary open.

## Exact commands

Run the independent retail witness before adding or changing any port
instrument:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --hit-cap 64 --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 2 --post-value-watch 3 --post-value-pc 0x80090CA4 --watch-pc 0x80090CA4,0x800908D4,0x8009081C,0x80090810,0x80094648,0x800078EC,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2350_m5_hangar_writer_oracle.log 2>&1
    zsh -n scratch/agent/run_s2350_m5_hangar_writer.sh
    zsh scratch/agent/run_s2350_m5_hangar_writer.sh s2350_m5_hangar_writer

The new parser must canonicalize each observed origin and its `+0x400`
variant, require the oracle whole-RDRAM, target-window, exact-field,
candidate-PC, title/hangar, and named-PC controls, and verify the reused
s2349 port table has all four `controls=1` rows. The silent-arm zero-DMA
count remains expected. A null without those controls is H-CoverageInvalid,
not evidence.
