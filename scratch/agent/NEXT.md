# NEXT work unit (s964)

Instrument one external-core breakpoint callback path around lookup, debugger
state transition, and `update_debugger()`. Do not retry retail PIF/callback
hypotheses until the PIF-region read-watch arm survives or the failing stage is
named.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-pif-lookup: breakpoint lookup on the first PIF access dereferences invalid
  breakpoint-table state.
- H-pif-state-transition: pausing the debugger run state on a PIF hit enters an
  invalid state transition before the callback returns.
- H-pif-update-callback: `update_debugger()` or its frontend callback crashes
  after the breakpoint has been identified.

Discriminating measurement: add one rate-limited diagnostic before and after
breakpoint lookup, before and after the debugger state transition, and before
and after `update_debugger()`, then run ordinary-RDRAM and PIF-region
read-watch arms in one bounded batch. The whole-RDRAM write control must fire
in both. A crash before lookup return selects table lookup; a crash after
lookup but before state-transition return selects debugger-state handling; a
crash after state transition but before callback return selects
`update_debugger()`.

Exact commands:

`rg -n -C 8 "check_breakpoints_on_mem_access|update_debugger|lookup_breakpoint" /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/debugger`

`tools/oracle/build_core.sh && tools/oracle/build.sh`

Run both arms with:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x00001000:0x00001004`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x1fc007c0:0x1fc007c4`
