# M5 s3676 — sparse stage event join

The qualified concurrent recipe `zsh scratch/agent/run_s3674_m5_stage_task_join.sh`
was run after adding a thread-local source-span input-DMA event to the stage
witness. The build completed. Oracle whole-RDRAM, descriptor/task, and VI
controls fired; the port emitted 1,024 source-span input rows and 1,854 stage
rows.

Sparse title stage ordinal 1 had `source_event=0`. Title ordinals 460 and 463,
and hangar ordinal 464, retained `source_event=1029`; the source row for 1029
belonged to route ordinal 92 and task `0x80171CE0`, not those sparse callback
rows. Later hangar stages retained the last hangar input event 6372 at route
ordinal 667/task `0x80171E70`.

This is single-source port evidence selecting `H-ExceptionTiming` over a
stable destination map within this instrument. It does not prove guest timing
is wrong: a thread-local handoff cannot represent cross-thread ownership. The
next probe must use a bounded task-keyed shared record and report hit/miss/age.
