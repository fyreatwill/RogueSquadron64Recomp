# NEXT work unit (s968)

Trace the external oracle source-to-artifact ABI mismatch through preprocessing,
LLVM IR, and the exact compile/link flags. Do not edit the recomp runtime or
retry retail PIF/callback hypotheses until this boundary is explained.

HYPOTHESIS-ID: oracle-pif-call-abi-artifact

Competing hypotheses:

- H-preprocess-prototype: the preprocessed translation unit sees a different
  callback prototype or macro than the source/header audit suggests.
- H-llvm-ir-call: preprocessing is correct but LLVM IR contains the wrong
  argument order/count before code generation.
- H-link-artifact: source/IR/object are correct and the linked dylib contains
  an obsolete or mismatched object/link product.

Discriminating measurement: compare the four-argument call in preprocessed C,
LLVM IR, object disassembly, and linked-dylib disassembly. A wrong prototype in
preprocessed C selects preprocessing; correct C but a three-argument/wrong-slot
IR call selects the compiler/IR path; correct IR/object but wrong dylib selects
link-artifact. Preserve the paired ordinary positive-control run if a rebuild
is needed.

Exact commands:

`rg -n "memory\\.c|dbg_breakpoints\\.c|clang|CFLAGS|DBG" /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/Makefile`

`clang -E <exact-build-flags> src/device/memory/memory.c | rg -n -C 4 "check_breakpoints_on_mem_access"`

`clang -S -emit-llvm <exact-build-flags> src/device/memory/memory.c -o /tmp/rs64-memory.ll`

`rg -n -C 6 "check_breakpoints_on_mem_access" /tmp/rs64-memory.ll`

`nm -an /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks"`
