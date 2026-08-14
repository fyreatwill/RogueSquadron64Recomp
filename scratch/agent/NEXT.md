# NEXT work unit (s965)

Instrument one external-core PIF `read_with_bp_checks()` call boundary. Do not
retry retail PIF/callback hypotheses until the PIF-region read-watch arm
survives or this wrapper boundary is named.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-pif-wrapper-before: the PIF wrapper crashes before invoking
  `check_breakpoints_on_mem_access()`.
- H-pif-callback-entry: the wrapper invokes the callback, but argument/state
  setup or entry crashes before its first instruction marker.
- H-pif-wrapper-after: the callback returns, but the saved-handler restore or
  wrapper return path crashes.

Discriminating measurement: add rate-limited markers immediately before and
after the PIF wrapper's call to `check_breakpoints_on_mem_access()`, then run
ordinary-RDRAM and PIF-region read-watch arms in one bounded batch. The
whole-RDRAM write control must fire in both. No pre-call marker selects an
earlier wrapper/device fault; pre-call plus no post-call marker selects the
callback path; both markers select the restore/return path.

Exact commands:

`rg -n -C 12 "read_with_bp_checks|check_breakpoints_on_mem_access" /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core`

`tools/oracle/build_core.sh && tools/oracle/build.sh`

Run both arms with:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x00001000:0x00001004`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x1fc007c0:0x1fc007c4`
