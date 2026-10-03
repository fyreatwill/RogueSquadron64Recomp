# M5 session 3757 — target-only native task-data value retry

The Debug build succeeded after changing the task-data page-fault witness so
the positive-control fault is not instruction-decoded. Decoding and pending
post-store sampling now run only for exact task-data faults observed while a
target route phase is active.

One paired 75-second capture used the validated real-audio/silent-control,
LLE-solo, spin-yield, ungated, autopilot route with phase gating. Both arms
passed the page positive control and reached title VI 1024. The real arm also
reached hangar VI 512; the silent arm crashed in the existing VI retrace path
before hangar. The real arm later crashed in `musyxBuildVoiceCommandList`.
Neither arm produced a target-range fault row or a post-store row.

This is not evidence that native stores are absent or zero-valued. It selects
run instability/no target fault for this capture: the target-only decoder was
never exercised. The next probe must preserve the positive control and improve
target-fault capture stability before interpreting values.

Evidence: `scratch/agent/s3757_m5_task_value_retry/{real,silent}.log` and the
paired summaries in the same directory.
