# NEXT work unit (s981)

Perform one bounded binary-level callback-entry probe on the corrected
external oracle dylib. Do not edit the recomp runtime, add callback markers,
or run a retail soak.

HYPOTHESIS-ID: oracle-pif-callback-runtime

Competing hypotheses:

- H-pif-core-entry: the direct call reaches the valid callback, but its first
  compiled instructions or diagnostic operation faults.
- H-pif-binary-target: the linked image's call target or prologue differs from
  the static source model or lands in an invalid image state.
- H-pif-harness: an isolated direct invocation survives, so the fault depends
  on emulator/core state around the callback rather than handler ownership.

Discriminating measurement: inspect the exact corrected dylib call target and
first instructions, then invoke that callback in an isolated harness with the
same four arguments. A valid target/prologue plus isolated survival selects
H-pif-harness; a fault in the first body instructions selects H-pif-core-entry;
a target/prologue discrepancy selects H-pif-binary-target.

Exact commands:

`nm -n /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib | rg 'read_with_bp_checks|check_breakpoints_on_mem_access|activate_memory_break_read|read_pif_mem'`

`otool -tvV /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib | sed -n '/_read_with_bp_checks:/,/^$/p'`

The existing source audit is the baseline: handler types, saved PIF
ownership, and callback state ownership are coherent. No retail phase result
may be inferred from this probe.
