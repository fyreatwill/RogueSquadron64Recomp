# NEXT work unit (s966)

Instrument the first statement of `check_breakpoints_on_mem_access()` in the
external oracle core. Do not retry retail PIF/callback-table hypotheses until
the PIF-region read-watch arm survives or this callback boundary is named.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-pif-call-abi: the wrapper reaches the call expression, but callback
  argument setup or call/return ABI handling crashes before callback body code.
- H-pif-callback-prologue: callback control transfers to the function but its
  generated prologue/first-entry operations crash before the marker.
- H-pif-callback-body: the first callback statement fires, then existing
  callback logic crashes before the wrapper's post-callback marker.

Discriminating measurement: add a rate-limited PIF-only marker as the first
statement of `check_breakpoints_on_mem_access()`, then run ordinary-RDRAM and
PIF-region read-watch arms concurrently. The whole-RDRAM write control must
fire in both. Wrapper pre-marker plus no callback-first marker selects the
call/prologue boundary; callback-first plus no wrapper-post marker selects
early callback body; all three markers select a later wrapper/return issue.

Exact commands:

`rg -n -C 12 "int check_breakpoints_on_mem_access" /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/debugger/dbg_breakpoints.c`

`tools/oracle/build_core.sh && tools/oracle/build.sh`

Run both arms with:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x00001000:0x00001004`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x1fc007c0:0x1fc007c4`
