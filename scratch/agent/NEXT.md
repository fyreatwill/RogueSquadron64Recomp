# NEXT work unit (s860)

HYPOTHESIS-ID: m3-guest-pc-8000834c-audit

Perform a source-only audit of the complete `0x8000834c` attribution chain:
enumerate every write of `g_rs64_last_guest_pc`, every crash-handler read, and
every host/guest-PC handoff, then compare the handoff semantics with the last
s860 helper event. Do not build or run until the inventory can distinguish a
stale breadcrumb from a fault in `getNextSlotNpcTypeId`.

Competing hypotheses:

- H-stale-breadcrumb: the guest PC is a sticky or asynchronously written
  breadcrumb unrelated to the faulting host instruction.
- H-helper-handoff: the crash handler's guest-PC handoff identifies a real
  helper instruction or return path.
- H-other-thread: the host crash occurs on a thread/path that cannot share the
  helper's guest-PC state under the documented ownership rules.
- H-unresolved: source ownership is complete but the handoff remains
  ambiguous; leave the crash family open rather than adding a guard.

Discriminator: the exhaustive source inventory must show whether the value
reported as `0x8000834c` can be the faulting guest instruction, which thread
writes it, and whether the crash handler samples it synchronously. A valid
helper trace ending before the host crash plus an asynchronous/sticky writer
selects H-stale-breadcrumb; a synchronous helper-owned handoff selects
H-helper-handoff; disjoint thread ownership selects H-other-thread. No outcome
authorizes a mitigation without naming the writer and establishing value
legitimacy.

Exact commands:

1. Inventory writers/readers first:
   `rg -n -C 8 "g_rs64_last_guest_pc|last-guest-pc|mcontext|CRASH" src lib ../N64Recomp/fixup_game_funcs.py`.
2. Read bounded source windows around every hit and map thread/ordering; no
   build or run unless the inventory leaves a discriminating ambiguity.
3. If a runtime probe is still required, add it only through the appropriate
   fixup/source path, then regenerate and build once with the existing
   phase-gated controls.
