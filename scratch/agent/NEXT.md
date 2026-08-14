# NEXT work unit (s963)

Instrument one external-core initialization path around debugger breakpoint
installation and device mapping. Do not retry retail PIF/callback hypotheses
until the PIF-region read-watch arm survives or the failing frame is named.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-pif-map-install: installing a breakpoint over region `0x1fc0` leaves an
  invalid handler or saved-handler state during device/RDRAM initialization.
- H-pif-device-init: the PIF device is initialized with a handler/base state
  that is invalid independently of breakpoint installation.
- H-pif-debug-callback: the debugger callback or breakpoint table is entered
  during initialization and crashes before the first emulated instruction.

Discriminating measurement: add one rate-limited diagnostic at the PIF mapping,
breakpoint activation, and first debugger-read entry points, rebuild the core,
then run ordinary-RDRAM and PIF-region read-watch arms in the same bounded
batch. The whole-RDRAM write control must visibly fire in both. A crash before
the PIF activation marker selects device/mapping initialization; activation
followed by a crash before debugger-read selects breakpoint/callback setup; a
PIF debugger-read marker selects the saved-handler or address path. Remove or
keep the diagnostic based on whether it identifies a concrete failing stage.

Exact commands:

`rg -n -C 8 "map_region|activate_memory_break_read|add_breakpoint_struct|init_pif|init_memory|read_with_bp_checks" /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/debugger`

`tools/oracle/build_core.sh && tools/oracle/build.sh`

Run both arms with:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x00001000:0x00001004`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x1fc007c0:0x1fc007c4`
