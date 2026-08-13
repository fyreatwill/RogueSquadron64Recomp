# NEXT work unit (s856)

HYPOTHESIS-ID: m3-slot-dispatcher-crash

Add one behavior-neutral, phase-scoped dispatcher trace in the generated-code
fixup path, build once, and run the existing phase-gated recipe once. Record a
positive-control entry for every dispatcher invocation, then record selector,
masked index, table-entry pointer, slot fields, update-function address, and
pre/post update-call state for the first bounded late-task window. Do not
change parser advancement, RDP handlers, or mitigation.

Competing hypotheses and discriminator:

- H-invalid-slot: the slot-chain/index or NPC context is invalid before the
  dispatcher dereference.
- H-invalid-update: the NPC update-function pointer is invalid or returns a
  corrupted context that faults in the dispatcher frame.
- H-caller-state: the dispatcher inputs are valid and corruption enters from a
  caller-side state transition or a callee return.
- H-stale-breadcrumb: the source path does not match the observed host PC and
  the apparent dispatcher attribution remains symbol/stack artefact.

Discriminator: the same-run positive-control count must be nonzero. A bad
selector/link or null/implausible slot before the fault selects H-invalid-slot;
a bad update address or post-call context selects H-invalid-update; valid
inputs through the crash select H-caller-state; no dispatcher entry before a
matching host fault selects H-stale-breadcrumb. No trace result authorizes a
mitigation without identifying the writer and legitimacy.

Exact commands:

1. `rg -n "slotDispatcherIter|viRetraceHandlerThread|\[CRASH\]|last-guest-pc|vifs-snapshot" src lib docs tools`
2. Read bounded windows around every dereference/callsite and representative
   crash markers in `scratch/agent/soak_results/`; implement the trace through
   the regeneration/fixup path.
3. Build once, run the phase-gated recipe once, and require the dispatcher-entry
   positive control before classifying any null result.
