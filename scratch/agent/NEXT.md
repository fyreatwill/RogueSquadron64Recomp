# NEXT work unit (s970)

Capture the exact successful oracle link command, then disassemble the fresh
`memory.o` call site and inspect its relocation plus the linked dylib's symbol
binding. Do not edit the recomp runtime or retry retail PIF/callback
hypotheses until the object-to-dylib boundary is explained.

HYPOTHESIS-ID: oracle-pif-link-artifact

Competing hypotheses:

- H-pif-lto-link-transform: matching fresh object/link inputs reach the final
  dylib, but link/LTO/codegen drops or repurposes the fourth argument.
- H-pif-wrong-object-selected: the link selects a different/older object or
  symbol body than the freshly rebuilt `memory.o`, despite the dylib being new.
- H-pif-relocation-target: the object has a different relocation or call target
  than expected, exposing a broader ABI or symbol-binding defect.

Discriminating measurement: save the verbose link command and compare the
fresh object call/relocation with the linked call target. Matching object and
link inputs but missing `w3` selects link/LTO transformation; a different
object or symbol input selects wrong-object selection; a changed relocation or
call target selects a broader link/ABI defect.

Exact commands:

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix && make -B DEBUGGER=1 STRINGS=/opt/homebrew/opt/binutils/bin/strings LDFLAGS="-framework CoreFoundation -dynamiclib -L/opt/homebrew/Cellar/binutils/2.47/lib" V=1 all 2>&1 | tee /tmp/rs64-oracle-link.log`

`otool -tvV _obj/device/memory/memory.o | rg -n -C 12 "check_breakpoints_on_mem_access"`

`otool -rv _obj/device/memory/memory.o | rg -n -C 8 "check_breakpoints_on_mem_access|memory.o"`

`nm -an libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks"`

`otool -tvV libmupen64plus.dylib | sed -n '19840,19930p'`
