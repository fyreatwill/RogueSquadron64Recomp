# NEXT work unit (s855)

HYPOTHESIS-ID: m3-slot-dispatcher-crash

Perform one bounded source-only idiom audit of every `slotDispatcherIter+872`
definition, call path, crash marker, and guest-PC handoff. Do not build, run,
or change parser advancement, RDP handlers, or mitigation.

Competing hypotheses and discriminator:

- H-real-stall: the dispatcher intentionally aborts after a guest-side
  scheduler stall and task 650 is unreachable without fixing that idiom.
- H-crash-report-only: the process is still making progress and the host crash
  marker is a false attribution or stale signal.
- H-runtime-corruption: an invalid slot or queue state reaches the dispatcher
  and causes the SIGBUS before the residual task.
- H-unrelated-thread: the marker belongs to a different thread and cannot
  explain the late-task reachability loss.

Discriminator: enumerate every source site and call edge, then classify each
observed marker by thread, guest PC, signal/abort origin, and whether the
dispatcher has a progress counter or explicit stall threshold. A complete
one-to-one match between task-650 failures and an intentional stall gate
selects H-real-stall; a mismatch selects H-crash-report-only or
H-unrelated-thread; a reproducible invalid-state input selects
H-runtime-corruption. No source-only result authorizes a mitigation.

Exact commands:

1. `rg -n "slotDispatcherIter|viRetraceHandlerThread|\[CRASH\]|last-guest-pc|vifs-snapshot" src lib docs tools`
2. Read bounded windows around every definition/callsite and the latest crash
   marker in `scratch/agent/soak_results/`; produce a complete site table in
   the session ledger.
