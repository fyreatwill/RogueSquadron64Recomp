# NEXT work unit (s969)

Force-rebuild the external oracle dylib from its current sources and exact
Makefile recipe, then disassemble the new wrapper call and callback entry. Do
not edit the recomp runtime or retry retail PIF/callback hypotheses until this
boundary is explained.

HYPOTHESIS-ID: oracle-pif-link-artifact

Competing hypotheses:

- H-pif-stale-dylib: the current dylib is stale or assembled from a different
  object/product set despite its timestamps.
- H-pif-lto-link-transform: the exact current object bitcode is linked, but
  the final LTO/codegen stage drops or repurposes the fourth argument.
- H-pif-rebuild-correct: a forced rebuild restores `w3`; the prior artifact
  was a stale or incomplete product and the callback crash boundary must then
  be retested separately.

Discriminating measurement: after the forced build, compare source/object/dylib
timestamps and hashes, then inspect `read_with_bp_checks`. `w3` restored selects
stale/incomplete product; `w3` still absent with fresh objects selects link/LTO
transformation; a changed call target or stack sequence selects a broader
link/ABI defect. If a rebuild is needed, preserve the paired ordinary
positive-control run for the later runtime boundary test; do not run it in
this static work unit.

Exact commands:

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix && make -B DEBUGGER=1 all`

`stat -f "%Sm %N" -t "%Y-%m-%d %H:%M:%S" ../../src/device/memory/memory.c ../../src/debugger/dbg_breakpoints.c _obj/device/memory/memory.o _obj/debugger/dbg_breakpoints.o libmupen64plus.dylib`

`shasum -a 256 _obj/device/memory/memory.o _obj/debugger/dbg_breakpoints.o libmupen64plus.dylib`

`nm -an libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks"`

`otool -tvV libmupen64plus.dylib | sed -n '19840,19930p'`
