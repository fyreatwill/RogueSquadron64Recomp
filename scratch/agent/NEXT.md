# NEXT work unit (s975)

Run one bounded static comparison of fresh LTO and non-LTO
`dbg_breakpoints.o` from the same oracle source tree. Use `llvm-dis`/`llvm-nm`
on the LTO object and `otool -tvV`/`nm -m` on the non-LTO object; compare the
callback symbol signature, prologue, and references to
`check_breakpoints_on_mem_access`. Do not edit the recomp runtime or retry
retail PIF/callback hypotheses.

HYPOTHESIS-ID: oracle-pif-breakpoints-lto

Competing hypotheses:

- H-pif-breakpoints-codegen: the LTO and non-LTO callback object differ in
  the callback's emitted ABI or symbol/reference shape, identifying the
  object-level transformation rather than the linker.
- H-pif-breakpoints-link: the callback object is ABI-equivalent in isolation,
  selecting the LTO linker's cross-object transformation as the remaining
  boundary.
- H-pif-breakpoints-recipe: the object difference cannot be reproduced from
  identical source and flags, selecting build state/toolchain state instead.

Discriminating measurement: whether the LTO and non-LTO `dbg_breakpoints.o`
artifacts have the same callback signature/prologue and reference shape. A
reproducible object-level difference selects codegen; identical objects with
different final calls selects the linker; an unreproducible difference selects
build state rather than runtime.

Exact commands:

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix && llvm-nm -m _obj/debugger/dbg_breakpoints.o && llvm-dis _obj/debugger/dbg_breakpoints.o -o /tmp/s975-breakpoints.ll`

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB3/projects/unix && nm -m _obj/debugger/dbg_breakpoints.o && otool -tvV _obj/debugger/dbg_breakpoints.o | rg -n -A 45 "check_breakpoints_on_mem_access|read_with_bp_checks"`

`rg -n -C 8 "check_breakpoints_on_mem_access|define .*check_breakpoints" /tmp/s975-breakpoints.ll`
