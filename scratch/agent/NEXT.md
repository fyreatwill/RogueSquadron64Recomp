# Next work unit

HYPOTHESIS-ID: m3-memb-nonself

Run one complete static census of backward-loop non-self zero-offset `MEM_B`
loads in the external generated tree. Reconcile the raw count and classify
every candidate as a byte scalar/table read or a genuine pointer transition.
Do not add a guard until a named writer and value legitimacy are established.

Competing hypotheses:

- H-MEMB-bounded: every candidate is a byte flag, index, table field, or other
  scalar read; no runtime change is authorized.
- H-MEMB-invalid: at least one candidate is part of a pointer reconstruction
  with a named guest writer that can publish an invalid value; that site gets
  a justified runtime probe candidate.
- H-MEMB-unreached: no candidate executes on the qualified title/hangar route;
  the result remains static and cannot motivate mitigation.

Discriminating measurement: two independent source scans must agree on the
candidate-site count. For every site, record file, function, guest PC, source
register/expression, destination register, back-edge, loop bound/sentinel, and
the immediate consumer. A pointer reconstruction with a named writer selects
H-MEMB-invalid; scalar consumers at every site select H-MEMB-bounded; a zero
target-phase runtime result selects H-MEMB-unreached. No build is needed
unless the static census identifies a real pointer candidate; if it does,
batch all candidate probes and controls in one regeneration-safe build/run.

Before any build, run:

    rg -n -C 8 'MEM_B\([^,]+,\s*0\)|MEM_B\(0X0,|MEM_B\(0x0,' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    rg -n -C 5 'rs_malloc|buildHeapFreeList|coalesceFreeHeapBlocks' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs

If a runtime arm is selected, require the existing allocator/free-list
positive controls, title `0x00790400`, hangar `0x006AB400`, phase-gated
budgets, and the retail whole-RDRAM control. Keep all M5 and A10 guards
unchanged. Use SIGKILL for cleanup.
