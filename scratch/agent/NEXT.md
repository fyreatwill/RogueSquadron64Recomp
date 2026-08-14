# NEXT work unit (s976)

Run one bounded oracle rebuild with the all-LTO recipe, preserving the
linker-generated LTO object with `-Wl,-object_path_lto,/tmp/s976-lto.o`.
Inspect that object and the resulting dylib with `file`, `nm`, and
`otool -tvV`; compare the callback entry and both wrapper call sites against
the s975 non-LTO control. Do not edit the recomp runtime or retry retail
PIF/callback hypotheses.

HYPOTHESIS-ID: oracle-pif-breakpoints-lto

Competing hypotheses:

- H-pif-breakpoints-lto-lowering: the generated LTO object already drops
  `x3`/changes the callback argument shape, selecting LTO lowering/backend
  code generation.
- H-pif-breakpoints-final-link: the generated LTO object is correct but the
  final dylib changes the shape, selecting final-link handling.
- H-pif-breakpoints-recipe: preserving the generated object is unsupported or
  unreproducible, selecting recipe/toolchain state.

Discriminating measurement: whether `/tmp/s976-lto.o` has the same callback
entry/call shape as the bad all-LTO dylib. Bad generated object selects LTO
lowering; correct generated object plus bad dylib selects final-link handling;
failure to preserve/reproduce it selects recipe/toolchain state.

Exact commands:

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix && make clean && make LDFLAGS="-Wl,-object_path_lto,/tmp/s976-lto.o"`

`file /tmp/s976-lto.o && nm -m /tmp/s976-lto.o && otool -tvV /tmp/s976-lto.o | rg -n -A 45 "check_breakpoints_on_mem_access|read_with_bp_checks"`

`otool -tvV /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix/libmupen64plus.dylib | rg -n -A 45 "_check_breakpoints_on_mem_access:|_read_with_bp_checks:"`
