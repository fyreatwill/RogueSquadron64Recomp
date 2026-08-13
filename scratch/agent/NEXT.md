# NEXT work unit (s857)

HYPOTHESIS-ID: m3-slot-dispatcher-crash

Increase the existing behavior-neutral, phase-scoped dispatcher trace bounds
from 512 entry / 256 detail rows to 4096 entry / 2048 detail rows in the
generated-code fixup path, build once, and run one 1024-width phase-gated
capture. Keep selector, masked index, table-entry pointer, slot fields,
update-function address, and pre/post update-call state unchanged. Do not
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

Discriminator: the same-run positive-control count must be nonzero. If the
expanded window captures a bad selector/link or null/implausible slot before a
matching fault, select H-invalid-slot; a bad update address or post-call
context selects H-invalid-update; valid inputs through a matching fault select
H-caller-state; no dispatcher entry before the host fault selects
H-stale-breadcrumb. If the run ends cleanly again, classify only the observed
window as valid and leave the crash population unevaluable. No trace result
authorizes a mitigation without identifying the writer and legitimacy.

Exact commands:

1. `rg -n "slotDispatcherIter|viRetraceHandlerThread|\[CRASH\]|last-guest-pc|vifs-snapshot" src lib docs tools`
2. Update the existing s857 trace bounds in `../N64Recomp/fixup_game_funcs.py`
   and the current generated `funcs_8.c` output; keep the fixup as the source
   of truth.
3. `cmake --build build --config Debug --target RogueSquadron64Recomp`
4. `env ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_SLOT_DISPATCH_PHASE_MIN=3 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/soak_results/s858_slot_dispatch 300 0.5`
5. Require nonzero `[slot-dispatch] kind=entry` rows, then compare the final
   trace rows with `[CRASH]`/`pc-symbol` markers before classifying anything.
