# NEXT work unit (s2353) — retail hangar task-field destination attribution

HYPOTHESIS-ID: m5-hangar-task-field-relation

## Work unit

Run one fresh retail exact-destination census for the complete hangar
`data_ptr+0x100` set observed in the s2352 port table:
`0x00171DE0`, `0x00171F70`, and `0x00173DB0`. Retain `0x00173C20` and
`0x00171DE0` as exact controls, arm all four observed phase origins, and join
every positive 512-phase writer PC/address to the existing s2352 four-arm
field snapshot/DMA ordering table. Do not write a field, alter task data,
change a consumer or default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-HangarFieldWriterInPortSet: at least one exact hangar field has a positive
  `writer-pc-phase` row in an explicit 512 bucket, and that address appears in
  the s2352 hangar `field_phys` set. This identifies a retail writer/destination
  pair for the open task-field boundary.
- H-HangarFieldsOutsidePhase: the hangar exact watches are globally positive,
  but all three have zero phase-attributed writer-PC rows in both explicit 512
  buckets. This proves only that the watched fields are written outside those
  phase buckets at capture scope; it does not authorize a port writeback.
- H-HangarFieldSetMismatch: a positive 512-phase writer exists for a watched
  hangar field, but its address is absent from the s2352 hangar `field_phys`
  rows. This selects a port field-set mismatch rather than a missing retail
  writer.
- H-CoverageInvalid: whole-RDRAM, target-window, any exact watch, any explicit
  phase history, named-PC controls, or the reused four-arm port controls fail.

The discriminator is one table keyed by
`(phase_origin,width,field_phys,writer_pc,writer_rows,global_watch_hits,post_rows,arm,c88,task_n,data_ptr,field_pre,field_post,field_write_event,task_begin,abi_event,ordering)`. Select the first hypothesis only with a positive 512-phase writer row whose field is in the port hangar set; select the second only with positive global exact watches and an empty 512 writer set for all three fields; select the third only with a positive 512 writer row for a field absent from the port hangar set; otherwise select H-CoverageInvalid.

## Exact commands

Run the independent retail witness before adding or changing any parser or
port probe:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --watch-write 0x171F70:0x171F74 --watch-write 0x173DB0:0x173DB4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 --pc-hist-watch 5 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512 --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 --post-value-watch 5 --watch-pc 0x800078EC,0x800908D4,0x8009081C,0x80090810,0x80090CA4,0x80094648,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2353_m5_hangar_field_set_oracle.log 2>&1

    zsh -n scratch/agent/run_s2353_m5_hangar_field_set.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2353_m5_hangar_field_set.sh s2353_m5_hangar_field_set

The new parser must derive writer sets from every positive writer-PC row for
watch IDs 3–5, require all four explicit origins and the fresh whole-RDRAM
positive control, and reuse the s2352 table only as a port-side join. Every
arm must retain title/hangar, task, guest-receive, PCM, field-snapshot,
image-DMA, filter, render, key-on, and C88 controls.
