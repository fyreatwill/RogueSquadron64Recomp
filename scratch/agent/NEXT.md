# NEXT work unit (s2360) — retail writer source relation

HYPOTHESIS-ID: m5-retail-writer-source-relation

## Work unit

Run one fresh retail oracle capture with the qualified positive controls,
existing task/post-value probes, and phase-gated execution GPR rows for
`0x80090CA4`. Join each writer VI/field/value to the task `data_ptr` and
`data_ptr+0x100` relation, the writer histogram, and retained s2352 port
profiles. This is ground truth and analysis only: do not write back a field,
edit task data, change a consumer/default, or add a guard.

## Competing hypotheses and discriminating measurement

- H-RetailWriterSourceIsTaskData: at least one positive writer row has a
  phase-gated source argument or pointer equal to the task `data_ptr`, its
  `data_ptr+0x100` field, or a directly joined task buffer, with the same
  writer value. This identifies a task-data source relation.
- H-RetailWriterSourceIsSeparateState: every positive writer row misses the
  task pointer/field candidates, while its source pointer/argument resolves
  to a stable non-task retail state buffer across repeated writer VIs. This
  identifies a separate retail producer; it does not authorize port changes.
- H-RetailWriterValueIsDerived: every positive writer row misses the direct
  pointer candidates and no stable separate buffer exists, but the
  phase-gated GPR/source tuple changes in lockstep with the writer value. This
  selects a derived-value boundary requiring a deeper source probe.
- H-CoverageInvalid: whole-RDRAM, target-window, exact fields, all four phase
  histories, all four writer histograms, named PCs, task controls, post-value
  detail, or phase-gated writer GPR rows fail. No source relation can be
  inferred.

The discriminator is one complete table keyed by
`(phase_origin,width,writer_vi,writer_pc,source_s1,source_a0,source_a2,
writer_addr,writer_value,task_n_scope,task_field,data_ptr,data_ptr_plus_100,
port_arm,field_pre,field_post,ordering,source_class)`. A direct task pointer
match selects H-RetailWriterSourceIsTaskData; a stable non-task pointer across
positive rows selects H-RetailWriterSourceIsSeparateState; changing
non-pointer state that tracks the writer value selects H-RetailWriterValueIsDerived.
The parser must emit all phase-gated writer rows, report the three source
classes separately, and reject missing controls or phase-log overflow.

## Exact commands

    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x149470:0x1494B0 --watch-write 0x173C20:0x173C24 --watch-write 0x171DE0:0x171DE4 --watch-write 0x171F70:0x171F74 --watch-write 0x173DB0:0x173DB4 --hit-cap 64 --pc-task-dump 0x80033FCC --post-value-watch 2 --post-value-watch 3 --post-value-watch 4 --post-value-watch 5 --post-value-pc 0x80090CA4 --post-value-pc-detail --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 --pc-hist-watch 5 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x00790800:1024 --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x006AB800:512 --watch-pc 0x800078EC,0x80033FCC,0x800908D4,0x8009081C,0x80090810,0x8009220C,0x80090CA4,0x80094648,0x8008EC88,0x80091468,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2360_m5_writer_source.log 2>&1

    python3 scratch/agent/parse_s2360_m5_writer_source.py scratch/agent/s2360_m5_writer_source.log scratch/agent/s2352_m5_writer_placement scratch/agent/s2360_m5_writer_source

The parser must emit the complete keyed table and select exactly one of the
three source hypotheses when all controls pass.
