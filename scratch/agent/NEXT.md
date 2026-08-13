# NEXT work unit (s855)

HYPOTHESIS-ID: m3-slot-dispatcher-crash

Perform one bounded source-only audit of every input read and state transition
in `slotDispatcherIter` and `slotDispatcherInner`, then trace the caller-side
slot/index arguments and the NPC update-function pointer. Do not build, run,
or change parser advancement, RDP handlers, or mitigation.

Competing hypotheses and discriminator:

- H-invalid-slot: the slot-chain/index or NPC context is invalid before the
  dispatcher dereference.
- H-invalid-update: the NPC update-function pointer is invalid or returns a
  corrupted context that faults in the dispatcher frame.
- H-caller-state: the dispatcher inputs are valid and corruption enters from a
  caller-side state transition or a callee return.
- H-stale-breadcrumb: the source path does not match the observed host PC and
  the apparent dispatcher attribution remains symbol/stack artefact.

Discriminator: enumerate each dereference and call edge, identify the source
of the slot/index/update pointer, and determine whether the faulting host
instruction can be one of those operations. A proven invalid input selects
H-invalid-slot or H-invalid-update; valid inputs with a corrupting caller or
callee select H-caller-state; a source/PC mismatch selects H-stale-breadcrumb.
No source-only result authorizes a mitigation.

Exact commands:

1. `rg -n "slotDispatcherIter|viRetraceHandlerThread|\[CRASH\]|last-guest-pc|vifs-snapshot" src lib docs tools`
2. Read bounded windows around every dereference/callsite and representative
   crash markers in `scratch/agent/soak_results/`; produce a complete input
   table in the session ledger.
