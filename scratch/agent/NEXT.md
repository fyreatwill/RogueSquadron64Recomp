# NEXT work unit (s967)

Perform one static ABI/prologue audit of the external oracle PIF wrapper call
and `check_breakpoints_on_mem_access()` entry. Do not edit the recomp runtime
or retry retail PIF/callback hypotheses until this boundary is explained.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-pif-call-abi: the wrapper's C call setup or ABI/return sequence is invalid
  only for this PIF callback path.
- H-pif-callback-prologue: control reaches the callback but its generated
  prologue or first entry operation faults before the marker.
- H-pif-callback-body: the first marker is reached and the existing callback
  body is the failing region.

Discriminating measurement: inspect the compiled caller and callee assembly,
including the callback symbol address, argument registers, stack alignment,
call target, and instructions surrounding the first marker. A valid call/entry
sequence with a faulting first callback instruction selects the prologue; an
invalid call target/register/stack sequence selects ABI; a reachable first
marker selects callback body. Preserve the paired ordinary positive-control
run if a rebuild is needed.

Exact commands:

`rg -n -C 20 "check_breakpoints_on_mem_access|read_with_bp_checks" /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/debugger /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device/memory`

`nm -an /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks"`

`otool -tvV /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib | rg -n -C 12 "check_breakpoints_on_mem_access|read_with_bp_checks"`
