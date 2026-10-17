# Unblocked: M4 shared boundary

Route 1 — refuted the block as reasoned.

The blocked claim was that no locally available method could drive the rebuilt
port from title/640 to hangar/512. Source inspection found the in-process
`ROGUESQ_AUTOPILOT` path, and the existing validated recipe supplied its
LLE/ungated/solo route. The prior blocked run used window-injected keys and a
different schedule.

Evidence from `scratch/agent/unblock_m4_autopilot/run.log`:

- build completed successfully;
- autopilot armed and fired the validated Start/A schedule;
- phase control reached `vi_width=1024`, origin `0x00790400`;
- the port reached `vi_width=512`, origin `0x006AB400` at 23.8 seconds;
- the 512-gated M4 instrument was live, with 464 `[m4-y8000]` records.

The observation that makes the block false is the live
`vi_width=512 (was 1024) origin=0x006AB400` line from the same run. No M4
accumulator result was inferred; NEXT now calls for the complete task-keyed
comparison.
