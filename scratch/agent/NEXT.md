# Next work unit

HYPOTHESIS-ID: m3-memwu-nonself

Run one complete static census of backward-loop non-self zero-offset `MEM_WU`
loads in the external generated tree. Reconcile the raw count with two
independent source scans and classify every candidate as a bounded scalar,
table/record field, or genuine pointer transition. Do not add a guard until a
named writer and value legitimacy are established.

Competing hypotheses:

- H-MEMWU-bounded: every candidate is a scalar, record field, table value, or
  bounded list value; no runtime change is authorized.
- H-MEMWU-invalid: at least one candidate participates in pointer
  reconstruction and has a named guest writer that can publish an invalid
  value; that site becomes a justified probe candidate.
- H-MEMWU-unreached: no candidate executes on the qualified title/hangar route;
  the result remains static and cannot motivate mitigation.

Discriminating measurement: two independent scans must agree on the direct
zero-offset candidate count. For every backward-loop non-self site, emit file,
function, guest PC, source/destination registers, back-edge, and immediate
consumer. Scalar/field classification at every site selects H-MEMWU-bounded; a
named writer plus pointer reconstruction selects H-MEMWU-invalid; only a
runtime arm with the existing positive controls and zero target-phase rows can
select H-MEMWU-unreached. No build is needed unless the census identifies a
real pointer candidate; if it does, batch all candidate probes and controls in
one regeneration-safe build/run.

Before any build, run:

    rg -n -C 8 'MEM_WU\([^,]+,\s*0\)|MEM_WU\(0X0,|MEM_WU\(0x0,' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    rg -n -C 5 'rs_malloc|buildHeapFreeList|coalesceFreeHeapBlocks' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs

Then add the analogous reproducible `tools/census_memwu.py` with two count
paths and run it. If a runtime arm is selected, require the existing
allocator/free-list positive controls, title `0x00790400`, hangar
`0x006AB400`, phase-gated budgets, and the retail whole-RDRAM control. Keep all
M5 and A10 guards unchanged. Use SIGKILL for cleanup.
