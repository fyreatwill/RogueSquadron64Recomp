# NEXT work unit (s2355) — uncapped retail hangar payload/order census

HYPOTHESIS-ID: m5-hangar-task-field-payload-order

## Work unit

Make one bounded oracle change: raise
`MAX_POST_VALUE_PC_DETAIL_ROWS` in `tools/oracle/rs64_oracle.c` from `512` to
`16384`, rebuild the oracle, and repeat the same fresh retail census. Join all
retained detail rows to the qualified s2352 four-arm task-field table. Do not
write a port field, alter task data, change a consumer or default, or add a
guard.

## Competing hypotheses and discriminating measurement

- H-RetailPayloadMatchesPortField: after the cap increase, all 11 positive
  hangar writer keys retain value rows and each has a compatible payload and
  bounded task/order relation in the joined table. This selects a contract
  candidate for a later same-build A/B; it does not authorize that A/B.
- H-RetailWriterIsUnrelated: all positive hangar keys retain detail, but the
  payload sets or phase/order relation do not match the s2352 field table.
- H-RetailWriterOrderUnresolved: the larger buffer still overflows, or detail
  rows remain absent/incomplete for a positive hangar writer key, so no bounded
  completion relation can be established.
- H-CoverageInvalid: the whole-RDRAM, target-window, exact-field, any of the
  four phase histories, 23 named PCs, or the s2352 four-arm control join fails.

The discriminator is one table keyed by
`(phase_origin,width,writer_pc,field_phys,post_vi,value,detail_capacity,port_arm,task_n,data_ptr,field_pre,field_post,task_begin,task_end,abi_event,ordering)`. Require the fresh whole-RDRAM positive control, target-window control, exact watches `0x173C20/0x171DE0/0x171F70/0x173DB0`, all four phase histories, named-PC `23/23`, zero detail overflow, and all four retained port controls before interpreting any payload null.

## Exact commands

    apply_patch: change MAX_POST_VALUE_PC_DETAIL_ROWS from 512 to 16384 in tools/oracle/rs64_oracle.c
    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --watch-write 0x171F70:0x171F74 --watch-write 0x173DB0:0x173DB4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512 --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 --post-value-watch 5 --post-value-pc 0x800908D4,0x8009081C,0x8009220C,0x80090810,0x80090CA4 --post-value-pc-detail --watch-pc 0x800078EC,0x800908D4,0x8009081C,0x80090810,0x80090CA4,0x80094648,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2355_m5_hangar_payload_order_oracle.log 2>&1

    env RS64_ORACLE=scratch/agent/s2355_m5_hangar_payload_order_oracle.log zsh scratch/agent/run_s2354_m5_hangar_payload_order.sh s2355_m5_hangar_payload_order

The parser must retain all four arms and their controls, report the exact
post-value detail rows for every positive hangar writer PC/address, and reject
the run if the enlarged capacity still overflows. A positive writer count
without a detail row is not a payload control.
