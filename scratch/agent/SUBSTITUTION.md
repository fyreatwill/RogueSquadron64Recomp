Planned unit: join the port's first post-free stream-node consumer read to the
exact `rs_free` boundary.

1. What stopped it: the port never produced a valid VI-512 capture in this
iteration. The 1024-gated attempt died at VI 640; two 512-gated attempts
crashed in `fillSampleStreamRange+13572` / guest `0x8000834c`; the final run
with DPC wrap-flush/shadow prerequisites remained at VI 640 until its 180 s
watchdog.
2. Evidence this iteration: the final run log reports `last width: 640` and
the wrapper returned `probe_rc=4`; the s4306 adjacent-range positive control
fired, while `grep -c` found 0 `[s4306-row]`/`[s4307-row]` records and no VI-512
phase. The crash arms recorded the named crash PC before the phase gate.
3. Refutation experiment: replay the exact successful s4307 seeded-save route
and key driver from `scratch/agent/s4307_read_join_512/run.log`, with the same
free/read hooks enabled. If it reaches VI 512 and emits the positive control
plus target rows, the current blocker is refuted and the planned join can run.
