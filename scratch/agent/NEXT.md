# NEXT work unit (s980)

Audit the external oracle's runtime PIF handler replacement and saved-pointer
path as one bounded static unit. Do not edit the recomp runtime and do not add
another callback marker until the ownership path is classified.

HYPOTHESIS-ID: oracle-pif-callback-runtime

Competing hypotheses:

- H-pif-handler-trampoline: PIF breakpoint activation installs a wrapper or
  saved handler with an incompatible function type; the direct callback call
  is valid but the runtime memory-handler transition corrupts state.
- H-pif-callback-state: the callback target and ABI are valid, but callback
  entry faults because the debugger state/opaque pointer is invalid or stale.
- H-pif-core-reentrancy: the callback entry is valid, but the first callback
  operations re-enter or touch core state in a context that is not safe; the
  current marker placement is after the failing operation.

Discriminating measurement: enumerate every assignment and invocation of the
PIF handler and saved pointer from `activate_memory_break_read` through
`read_with_bp_checks`, then compare the declared callback types, casts, and
opaque lifetimes. A mismatched handler/trampoline type selects
H-pif-handler-trampoline; coherent ownership with an invalid callback state
selects H-pif-callback-state; coherent types/state with an unsafe first-body
operation selects H-pif-core-reentrancy. Do not infer a retail phase result
from this oracle boundary.

Exact commands:

`rg -n -C 8 'activate_memory_break_read|read_with_bp_checks|check_breakpoints_on_mem_access|saved_handler|handler|opaque' /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/debugger/dbg_breakpoints.c /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device/memory/memory.c`

`sed -n '1,240p' /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/debugger/dbg_breakpoints.h; sed -n '1,260p' /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device/memory/memory.h`

`nm -n /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib | rg 'read_with_bp_checks|check_breakpoints_on_mem_access|activate_memory_break_read|read_pif_mem'`

Expected outcomes: classify the handler/saved-pointer type and lifetime, or
record the exact unresolved edge. No mitigation is authorized by this audit.
