# NEXT work unit (s2354) — retail hangar task-field payload/order census

HYPOTHESIS-ID: m5-hangar-task-field-payload-order

## Work unit

Run one fresh retail oracle census with post-store detail for every positive
hangar writer PC from s2353, then join the detail rows to the qualified s2352
four-arm task-field table. This is a ground-truth/parser experiment only: do
not write a port field, alter task data, change a consumer or default, or add
a guard.

## Competing hypotheses and discriminating measurement

- H-RetailPayloadMatchesPortField: in the 512 buckets, each of the three
  port-observed fields has a positive `(writer_pc, field_phys, value)` detail
  row, and its value set intersects the corresponding s2352 port
  `field_pre/field_post` values with a bounded phase/order row. This selects a
  concrete task-field contract candidate for a later same-build A/B; it does
  not authorize the A/B by itself.
- H-RetailWriterIsUnrelated: the retail writer/detail rows are positive at the
  watched address, but the payload sets do not intersect the corresponding
  port field values or the writer lands outside the task-field phase/order
  relation. This proves address overlap is insufficient evidence for a
  writeback contract at capture scope.
- H-RetailWriterOrderUnresolved: exact address and payload rows are positive,
  but the bounded detail is incomplete, capped, or cannot be joined to the
  task completion/order row. This keeps the writer candidate open without
  changing behavior.
- H-CoverageInvalid: the whole-RDRAM, target-window, exact-field, any of the
  four phase histories, 23 named PCs, or the s2352 four-arm control join fails.

The discriminator is one table keyed by
`(phase_origin,width,writer_pc,field_phys,post_vi,value,post_row,global_hits,port_arm,task_n,data_ptr,field_pre,field_post,task_begin,task_end,abi_event,ordering)`. Require the fresh whole-RDRAM positive control, target-window control, exact watches `0x173C20/0x171DE0/0x171F70/0x173DB0`, all four phase histories, named-PC `23/23`, and all four retained port controls before interpreting any null.

## Exact commands

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --watch-write 0x171F70:0x171F74 --watch-write 0x173DB0:0x173DB4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 --pc-hist-watch 5 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512 --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 --post-value-watch 5 --post-value-pc 0x800908D4,0x8009081C,0x8009220C,0x80090810,0x80090CA4 --post-value-pc-detail --watch-pc 0x800078EC,0x800908D4,0x8009081C,0x80090810,0x80090CA4,0x80094648,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2354_m5_hangar_payload_order_oracle.log 2>&1

    zsh -n scratch/agent/run_s2354_m5_hangar_payload_order.sh
    zsh scratch/agent/run_s2354_m5_hangar_payload_order.sh s2354_m5_hangar_payload_order

The parser must read the s2352 table only as the port-side join, retain all
four arms and their controls, and report the exact post-value detail rows for
writer PCs and addresses. A positive writer count without a detail row is not
a payload control.
