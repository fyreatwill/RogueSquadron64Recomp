# NEXT work unit (s962)

Make one minimal source-level fix or diagnostic in the external oracle core's
debugger/memory handler so a PIF-region read watch can survive initialization.
Do not edit the recomp runtime or retry retail PIF/callback hypotheses until
this passes.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-pif-saved-handler: the debugger wrapper calls an invalid or incomplete
  saved handler for the PIF device mapping.
- H-pif-early-breakpoint: the first PIF read hits during core/boot setup and
  the synchronous debugger callback/step sequence is unsafe at that point.
- H-pif-address-normalization: the physical PIF address reaches the wrapper in
  a form that the PIF handler or breakpoint lookup does not support.

Discriminating measurement: rebuild the external core with exactly one source
change or diagnostic, then run ordinary-RDRAM and PIF-region read-watch arms in
the same bounded batch, each with `--watch-write 0x0:0x800000 --hit-cap 200
--vi-poll --verbose`. Ordinary read survival with PIF survival selects a
fixed PIF handler path; ordinary survival with PIF still crashing selects the
remaining PIF-specific branch; a logged PIF hit before failure selects the
early-breakpoint callback path. The whole-RDRAM write control must visibly
fire in every arm.

Exact starting checks/commands:

`rg -n -C 8 "read_with_bp_checks|activate_memory_break_read|read_pif_mem|MM_PIF_MEM" /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device`

`tools/oracle/build_core.sh && tools/oracle/build.sh`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x00001000:0x00001004`

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 5 --watch-write 0x0:0x800000 --hit-cap 200 --vi-poll --verbose --watch-read 0x1fc007c0:0x1fc007c4`
