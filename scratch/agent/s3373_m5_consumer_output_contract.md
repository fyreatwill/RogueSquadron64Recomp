# Session 3373 — M5 consumer/output contract

The first requested run was route-invalid: `tools/probe.sh` launched without
the canonical LLE/solo/spin-yield route controls, crashed in
`spTaskSchedulerThread`, and exited while still at VI width 320. Its null
result is discarded.

The fixed Debug build completed successfully. The fixed phase-gated run used
the canonical route and prescribed autopilot. It reached title VI
`1024 @ 0x00790400` at 11.5 s and hangar VI `512 @ 0x006AB400` at 19.8 s,
captured 141 frames, and had no `[CRASH]` or `[ABORT]` marker. Positive
controls were live: 2,978 audio-task ABI rows, 101 PCM source rows, 101 PCM
consumer rows, and the filter-audit control.

After the 512 transition, the named `m5-consumer-entry` marker remained at
zero. However, the regeneration-surviving audio joins recorded 5,402 task
joins, including 2,359 with `consumer_matches>0` and 1,899 with
`complete=1`; PCM source and consumer joins remained live (58 each in the
bounded post-transition scan). Completed joins paired source and consumer
spans, but the PCM rows reported `nz=0`; representative completed rows had
`consumer_matches=1`, `complete=1`, and source data while the corresponding
PCM consumer buffer had `nz=0`.

This run rejects the simple “no audio-task consumer/output path is
reachable” interpretation: existing task joins see consumer matches and
completed task/output relations. It provisionally selects an output-data gap
over a wholly unreached task consumer. The exact named `0x80019B74` entry
remains absent, so this is not proof that that particular guest consumer
executes; the distinction is single-source. No wait, slot, status, or output
behavior changed.

Evidence: `scratch/agent/s3373_m5_consumer_output_contract_fixed/run.log`.
