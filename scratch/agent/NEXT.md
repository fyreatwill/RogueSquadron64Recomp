# NEXT work unit (s2357) — retail task-ABI field relation

HYPOTHESIS-ID: m5-retail-task-abi-field-relation

## Work unit

Add one oracle-only `--pc-task-dump A` instrument. At the retail
`osSpTaskStartGo` entry `A=0x80033FCC`, phase-gated by the existing four
title/hangar origin buckets, dump type-2 `OSTask` rows: task ordinal, task
pointer, `data_ptr`, `data_size`, `output_buff`, `output_buff_size`,
`yield_data_ptr`, `yield_data_size`, and computed `data_ptr+0x100`. Join those
rows to the exact field-write histogram and the retained s2352 port ABI table.
This is ground truth and instrumentation only: no port field writeback, task
data edit, consumer/default change, or guard is allowed.

## Competing hypotheses and discriminating measurement

- H-RetailTaskAbiNamesPortField: a target-phase type-2 retail task row exposes
  a `data_ptr+0x100` or output-field relation that joins a nonzero field write
  and its writer/order to the s2352 port task rows. This identifies one
  contract candidate but authorizes no behavior change.
- H-RetailTaskAbiUsesSeparateBuffer: type-2 task fields do not map to the
  exact watched fields or the port ABI values/order, so the candidate field
  writers are separate state and the missing task relation is elsewhere.
- H-CoverageInvalid: any independent control, task-dump positive control, or
  overflow check fails, so no retail relation can be inferred.

The discriminator is one table keyed by
`(phase_origin,width,task_n,task_phys,type,data_ptr,data_size,output_buff,
output_size,yield_data_ptr,data_ptr_plus_100,field_phys,writer_pc,post_value,
ordering,port_arm,port_task_n)`. Require whole-RDRAM, target-window, all four
exact field watches, all four phase histories, writer histograms for watches
2–5, `0x80033FCC` execution, zero task-dump overflow, and the retained
four-arm port controls. A nonzero task/field/order relation selects the first
hypothesis; a controlled task table with no such relation selects the second;
any failed control selects the third.

## Exact commands after adding the instrument

    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --watch-write 0x171F70:0x171F74 --watch-write 0x173DB0:0x173DB4 --hit-cap 64 --pc-task-dump 0x80033FCC --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x00790800:1024 --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x006AB800:512 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 --pc-hist-watch 5 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512 --watch-pc 0x800078EC,0x80033FCC,0x800908D4,0x8009081C,0x80090810,0x8009220C,0x80090CA4,0x80094648,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2357_m5_task_abi_oracle.log 2>&1

    python3 scratch/agent/parse_s2357_m5_task_abi.py scratch/agent/s2357_m5_task_abi_oracle.log scratch/agent/s2352_m5_writer_placement scratch/agent/s2357_m5_task_abi

The parser must emit the complete keyed table, reject any missing control or
overflow, and report both the nonzero task/field/order relation count and the
zero/sentinel-only count separately.
