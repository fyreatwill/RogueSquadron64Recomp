# NEXT work unit (s977)

Run one bounded static recipe-diff experiment for the external oracle. Capture
`make -pn` and `make -n` for the known-good s976 all-LTO recipe and compare
feature variables, expanded compile/link flags, object lists, and library
search paths against the s975 recipe/log. Rebuild only the smallest
one-variable variant identified by that diff, preserving
`/tmp/s977-lto.o`; inspect the callback entry and both wrapper call sites with
`nm` and `otool -tvV`. Do not edit the recomp runtime or retry retail
PIF/callback hypotheses.

HYPOTHESIS-ID: oracle-pif-breakpoints-recipe

Competing hypotheses:

- H-pif-breakpoints-recipe-feature: `DEBUGGER=1` or another feature/input
  difference changes which callback-bearing objects enter the all-LTO link.
- H-pif-breakpoints-recipe-link: overwritten macOS dylib flags or library
  search paths alter the linker's LTO materialization or selected inputs.
- H-pif-breakpoints-recipe-toolchain: the same expanded recipe still produces
  different callback code, selecting compiler/linker nondeterminism or a stale
  external artifact.

Discriminating measurement: the first expanded flag/object difference that
reproduces the callback mismatch. A feature/object-list difference selects
recipe-feature; a linker-input/flag difference selects recipe-link; identical
expanded recipes with divergent fresh artifacts selects recipe-toolchain.

Exact commands:

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix && make -pn DEBUGGER=1 > /tmp/s977-good-vars.txt && make -n all DEBUGGER=1 LDFLAGS="-framework CoreFoundation -dynamiclib -Wl,-object_path_lto,/tmp/s977-lto.o" LDLIBS="-lm -ldl -lz -L/opt/homebrew/opt/libpng/lib -lpng16 -L/opt/homebrew/lib -lSDL2main -lSDL2 -Wl,-framework,Cocoa -L/opt/homebrew/opt/freetype/lib -lfreetype -L/opt/homebrew/Cellar/binutils/2.47/lib -lopcodes -lbfd -framework OpenGL" > /tmp/s977-good-link.txt`

`rg -n "^(DEBUGGER|OPTFLAGS|LDFLAGS|LDLIBS|SOURCE|OBJECTS) ?[:+]?=" /tmp/s977-good-vars.txt; rg -n "clang\+\+.*-object_path_lto|DEBUGGER|lopcodes|lbfd" /tmp/s977-good-link.txt`

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix && make clean && make all DEBUGGER=1 LDFLAGS="-framework CoreFoundation -dynamiclib -Wl,-object_path_lto,/tmp/s977-lto.o" LDLIBS="-lm -ldl -lz -L/opt/homebrew/opt/libpng/lib -lpng16 -L/opt/homebrew/lib -lSDL2main -lSDL2 -Wl,-framework,Cocoa -L/opt/homebrew/opt/freetype/lib -lfreetype -L/opt/homebrew/Cellar/binutils/2.47/lib -lopcodes -lbfd -framework OpenGL"`

`file /tmp/s977-lto.o libmupen64plus.dylib && nm -a /tmp/s977-lto.o libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks" && otool -tvV libmupen64plus.dylib | rg -n -A 45 "_check_breakpoints_on_mem_access:|_read_with_bp_checks:"`
