# NEXT work unit (s972)

Build one non-LTO oracle dylib using the successful target flags with
`OPTFLAGS='-O3 -fno-lto'`, then inspect its `read_with_bp_checks` callback call
and compare it with the current LTO dylib. Do not edit the recomp runtime or
retry retail PIF/callback hypotheses.

HYPOTHESIS-ID: oracle-pif-link-artifact

Competing hypotheses:

- H-pif-nonlto-linked-correct: a non-LTO linked dylib preserves `w2=4,w3=3`,
  isolating the defect to LTO.
- H-pif-nonlto-linked-wrong: the non-LTO linked dylib also shifts or drops an
  argument, selecting a link-stage input or symbol-state defect independent
  of LTO.
- H-pif-nonlto-build-blocked: the target cannot be linked non-LTO with the
  successful flags, so the exact link failure is the result and no runtime
  hypothesis is tested.

Discriminating measurement: compare the fresh non-LTO dylib call with the
current LTO dylib. Correct non-LTO `w2=4,w3=3` isolates LTO; the same shifted
call selects a non-LTO link/input defect; a failed link selects the build
boundary and leaves the runtime unevaluable.

Exact commands:

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix && make -B DEBUGGER=1 OPTFLAGS='-O3 -fno-lto' all`

`stat -f "%Sm %N" -t "%Y-%m-%d %H:%M:%S" _obj/device/memory/memory.o _obj/debugger/dbg_breakpoints.o libmupen64plus.dylib`

`nm -an libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks"`

`otool -tvV libmupen64plus.dylib | rg -n -A 45 "_read_with_bp_checks:" | rg -n -C 8 "check_breakpoints_on_mem_access|mov[[:space:]]+w[23]"`
