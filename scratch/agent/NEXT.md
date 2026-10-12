# Next work unit

HYPOTHESIS-ID: m3-mem-h-nonself

Run one complete census of the 19 generated backward non-self zero-offset
`MEM_H` pointer transitions. This is a static idiom audit first; do not add a
guard until the writer and legitimacy of every candidate are classified.

Competing hypotheses:

- H-MEMH-bounded: every site is a count-bounded, sentinel-terminated, or
  otherwise valid table/list transition, so no runtime change is authorized.
- H-MEMH-invalid: at least one site can consume an invalid halfword-derived
  pointer on the qualified route and has a named guest writer; that complete
  site class becomes the next guard candidate.
- H-MEMH-unreached: the 19 sites are not reached in the target phase, so the
  audit remains static and must not motivate a mitigation.

Discriminating measurement: enumerate all 19 sites and classify each by
function, guest PC, source register, zero-offset target, loop/sentinel or
count bound, and immediate consumers. For every site that executes in the
qualified title/hangar route, batch one probe build/run with the pointer,
writer PC/value, phase, and consumer entry, plus the existing allocator/free-
list positive controls, title `0x00790400`, hangar `0x006AB400`, and retail
whole-RDRAM control. A valid bounded transition at every executed site selects
H-MEMH-bounded; one invalid value with an independently named legitimate or
illegitimate writer selects H-MEMH-invalid or its writer-specific explanation;
zero target-phase entries selects H-MEMH-unreached. No guard is allowed from a
single-source or unqualified null.

Before building, run:

    rg -n -C 8 'MEM_H\([^,]+,\s*0\)|MEM_H\(0X0,|MEM_H\(0x0,' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    rg -n -C 5 'rs_malloc|buildHeapFreeList|coalesceFreeHeapBlocks' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs

Then write the complete site table and hypotheses into the session artifact,
add all counters in one regeneration-safe fixup/apply script, build once, and
run both any required control arms concurrently. Use SIGKILL cleanup and keep
the current A10 guards unchanged.
