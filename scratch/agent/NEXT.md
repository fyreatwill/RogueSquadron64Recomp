# NEXT work unit (s974)

Build two isolated single-object mixed oracle dylibs from the successful s973
copies: arm A has fresh non-LTO `memory.o` with LTO `dbg_breakpoints.o`; arm B
has LTO `memory.o` with fresh non-LTO `dbg_breakpoints.o`. Compare both
callback call sites against s973's all-LTO and two-object-mixed disassemblies.
Do not edit the recomp runtime or retry retail PIF/callback hypotheses.

HYPOTHESIS-ID: oracle-pif-lto-boundary

Competing hypotheses:

- H-pif-memory-lto: arm A is correct and arm B is wrong, identifying
  `memory.c`'s LTO treatment as sufficient for the bad call.
- H-pif-breakpoints-lto: arm B is correct and arm A is wrong, identifying
  `dbg_breakpoints.c`'s LTO treatment as sufficient for the bad call.
- H-pif-joint-lto: both single-object arms remain wrong while the two-object
  mixed arm is correct, selecting an interaction that requires both objects
  to be LTO.
- H-pif-lto-input-recipe: the mixed arm cannot be reproduced with identical
  inputs/flags, selecting a build-recipe or toolchain-state defect instead.

Discriminating measurement: compare `w2,w3` at both callback calls in both
fresh dylibs. Only arm A correct selects `memory.c`; only arm B correct selects
`dbg_breakpoints.c`; both wrong with the two-object mixed arm correct selects
joint LTO; an unreproducible arm selects build-state rather than runtime.

Exact commands:

`env LDFLAGS='-L/opt/homebrew/Cellar/binutils/2.47/lib' make -B DEBUGGER=1 OPTFLAGS='-O3 -fno-lto' all`

`stat -f "%Sm %N" -t "%Y-%m-%d %H:%M:%S" _obj/device/memory/memory.o _obj/debugger/dbg_breakpoints.o libmupen64plus.dylib`

`nm -an libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks"`

`otool -tvV libmupen64plus.dylib | rg -n -A 45 "_read_with_bp_checks:" | rg -n -C 8 "check_breakpoints_on_mem_access|mov[[:space:]]+w[23]"`
