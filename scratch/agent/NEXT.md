# NEXT work unit (s973)

Build two oracle dylibs in isolated copies using the same successful
environment-preserved binutils path: an all-non-LTO control and a mixed arm
with fresh non-LTO `memory.o`/`dbg_breakpoints.o` but an LTO link of the
remaining objects. Compare both callback call sites. Do not edit the recomp
runtime or retry retail PIF/callback hypotheses.

HYPOTHESIS-ID: oracle-pif-lto-boundary

Competing hypotheses:

- H-pif-mixed-correct: non-LTO callback objects remain correct when linked
  with the other LTO objects, localizing the defect to LTO-produced callback
  bitcode or its optimization.
- H-pif-mixed-wrong: the mixed link shifts/drops arguments, selecting an
  interaction between LTO objects and non-LTO callback objects.
- H-pif-lto-input-recipe: the mixed arm cannot be reproduced with identical
  inputs/flags, selecting a build-recipe or toolchain-state defect instead.

Discriminating measurement: compare `w2,w3` at both callback calls in the two
fresh dylibs. Correct mixed `w2=4,w3=3` localizes the defect to LTO-produced
callback objects; shifted mixed calls select an LTO/non-LTO interaction; an
unreproducible mixed recipe selects build-state rather than runtime.

Exact commands:

`env LDFLAGS='-L/opt/homebrew/Cellar/binutils/2.47/lib' make -B DEBUGGER=1 OPTFLAGS='-O3 -fno-lto' all`

`stat -f "%Sm %N" -t "%Y-%m-%d %H:%M:%S" _obj/device/memory/memory.o _obj/debugger/dbg_breakpoints.o libmupen64plus.dylib`

`nm -an libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks"`

`otool -tvV libmupen64plus.dylib | rg -n -A 45 "_read_with_bp_checks:" | rg -n -C 8 "check_breakpoints_on_mem_access|mov[[:space:]]+w[23]"`
