# M5 session 3756 — native task-data value attribution

The instrument decoded the faulting ARM64 instruction at the page-watch PC and
reported the source register/value for ordinary unsigned-immediate
`STRB`/`STRH`/`STR X` forms. The Debug build succeeded.

The first capture was invalid because it omitted the validated LLE/spin-yield
route and never reached the 1024/512 phases. The corrected route reached both
phases in both arms, but omitted the explicit watcher gate. The final capture
enabled `ROGUESQ_LOG_M5_TASK_WRITE_FAULT=1` in paired real/silent arms and
passed the page positive control.

The final run was not discriminating. Real reached both phases but later
entered the existing `musyxBuildVoiceCommandList` crash path; silent crashed in
`spTaskSchedulerThread` before a target phase. The watcher saw one exact-range
fault before phase gating and no target-phase attribution rows. Its positive
control decoded `0x782B6948` as an unrecognized instruction. Therefore no
native nonzero/zero producer conclusion is supported by this run.

The value-attribution hypothesis remains open. The next attempt should retain
the same positive control but make instruction decoding target-only and bound
the fault-watch arm to one stable target-phase window, so a pre-phase control
fault cannot perturb the qualified route.
