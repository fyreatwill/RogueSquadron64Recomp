# NEXT work unit (s2359) — retail task-field value and order

HYPOTHESIS-ID: m5-retail-task-field-value-order

## Work unit

Run one fresh retail oracle capture with the existing `--pc-task-dump
0x80033FCC` instrument, `--post-value-watch 2/3/4/5`, and
`--post-value-pc 0x80090CA4 --post-value-pc-detail`. Join the post-store
values to the s2357 task rows, exact writer histogram, and retained s2352
port ABI table. This is ground truth and analysis only: do not write back a
field, edit task data, change a consumer/default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-RetailWriterPublishesTaskField: a positive `0x80090CA4` post-value row at
  a task-matched phase/field is nonzero and matches the retained port field
  payload/order. This identifies a publish-order contract but authorizes no
  port change.
- H-RetailWriterPayloadMismatch: the writer is positive and stores a nonzero
  value, but the value/order does not match the task-matched port field
  payload. The field address relation is real; its payload contract remains
  open.
- H-RetailWriterPostValueAbsent: the exact writer histogram is positive but
  no post-value row joins the task-matched field, selecting a writer/store
  boundary rather than a port field mismatch.
- H-CoverageInvalid: whole-RDRAM, target-window, exact fields, all four phase
  histories, histogram watches, named PCs, task dump, post-value detail, or
  retained four-arm port controls fail; no relation can be inferred.

The discriminator is one table keyed by
`(phase_origin,width,task_n,field_phys,writer_pc,writer_vi,writer_value,
port_arm,field_pre,field_post,ordering)`. Require whole-RDRAM, target-window,
all four exact field watches, all four phase histories, writer histograms for
watches 2–5, named-PC controls, task-dump phase/type-2/overflow controls,
post-value-detail rows or an explicit zero summary, and all four retained
port controls. Count nonzero value matches, nonzero mismatches, and
zero/sentinel-only rows separately.

## Exact commands

    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --watch-write 0x171F70:0x171F74 --watch-write 0x173DB0:0x173DB4 --hit-cap 64 --pc-task-dump 0x80033FCC --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 --post-value-watch 5 --post-value-pc 0x80090CA4 --post-value-pc-detail --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 --pc-hist-watch 5 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512 --watch-pc 0x800078EC,0x80033FCC,0x800908D4,0x8009081C,0x80090810,0x8009220C,0x80090CA4,0x80094648,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2358_m5_task_value_order.log 2>&1

    python3 scratch/agent/parse_s2358_m5_task_value_order.py scratch/agent/s2358_m5_task_value_order.log scratch/agent/s2352_m5_writer_placement scratch/agent/s2358_m5_task_value_order

The parser must emit the complete keyed table, reject any missing control or
post-value-detail overflow, and report value matches, value mismatches, and
zero/sentinel-only rows separately.
