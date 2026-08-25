# NEXT work unit (s2352) — all-observed-origin placement of `0x173C20` writer

HYPOTHESIS-ID: m5-dataptr100-writer-provenance

## Work unit

Run one fresh retail exact-destination census with explicit phase buckets for
both observed title origins (`0x00790400`, `0x00790800`) and both observed
hangar origins (`0x006AB400`, `0x006AB800`). Retain `0x00171DE0`, whole-RDRAM,
target-window, and every named PC as positive controls. Derive every positive
`0x00173C20` writer PC from every `writer-pc-phase` row, then join its
`(origin,width,pc)` rows to the existing s2351 four-arm field snapshot/DMA
ordering table. Do not write either field, alter task data, change a consumer
or default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-TargetWriterTitleOrigin: with all four phase buckets positive, one or more
  writer PCs are phase-attributed to `0x00173C20` in an observed 1024/title
  origin; the writer placement is title-only at this capture scope.
- H-TargetWriterHangarOrigin: an all-PC writer row appears in one of the two
  512/hangar origins, contradicting the s2351 null and reopening the hangar
  task-field relation.
- H-TargetWriterOutsideObservedTargets: all four phase buckets have zero
  `0x00173C20` writer rows while the global exact-field watch is positive; the
  field is written outside these target origins and remains unrelated to the
  hangar task field at capture scope.
- H-CoverageInvalid: whole-RDRAM, target-window, either exact-field watch, any
  phase history, named-PC controls, or the reused four-arm port controls fail.

The discriminator is one table keyed by
`(phase_origin,width,field_phys,retail_writer_pc,retail_writer_rows,arm,c88,task_n,data_ptr,data_ptr_plus_100,field_pre,field_post,field_write_event,field_write_dram,field_write_len,task_begin,task_end,abi_event,ordering)`. Select the first hypothesis only with a positive `0x173C20` row in an explicit 1024 bucket; select the second only with a positive row in an explicit 512 bucket; select the third only when all four phase buckets and the global exact-field positive control pass while the phase writer set is empty. Otherwise select H-CoverageInvalid.

## Exact commands

Run the independent retail witness before adding or changing any parser or
port probe:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512 --post-value-watch 2 --post-value-watch 3 --watch-pc 0x800078EC,0x800908D4,0x8009081C,0x80090810,0x80090CA4,0x80094648,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2352_m5_writer_placement_oracle.log 2>&1

    zsh -n scratch/agent/run_s2352_m5_writer_placement.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2352_m5_writer_placement.sh s2352_m5_writer_placement

The new parser must require all four explicit `pc-hist-phase` origins and
derive the target writer set from every positive `writer-pc-phase` row, not
from the previously known PCs. Every arm must retain the s2351 task,
guest-receive, PCM, field-snapshot, image-DMA, filter, render, and key-on
controls; a null without those controls is H-CoverageInvalid.
