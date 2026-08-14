# NEXT work unit (s961)

Isolate the oracle debugger read-watch crash with one bounded source-level
probe/fix attempt: compare the existing read-watch callback path against a
read watch on an ordinary RDRAM word, and inspect the core's memory-handler
activation for the PIF region. Do not retry the retail PIF hypothesis until a
read watch survives initialization. If editing under the oracle's external
core is required, record the exact external path and rebuild result; do not
edit the recomp runtime.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

Competing hypotheses:

- H-oracle-read-breakpoint-core: any debugger read watch triggers the core's
  pre-VI crash, independent of address.
- H-oracle-pif-mapping: only a read watch in the PIF region activates an
  invalid/uninitialized memory handler.
- H-oracle-callback-reentry: the PIF read watch reaches the callback during
  initialization and the frontend callback/resume sequence crashes.

Discriminating measurement: a same-build/read-watch arm on a normal mapped
RDRAM range, paired with the already-proven whole-RDRAM write control. A crash
on both read-watch addresses selects the generic debugger read path; survival
on RDRAM but crash on PIF selects PIF mapping/handler; a logged read hit before
the crash selects callback re-entry or a later PIF-specific failure.

Exact starting checks:

`rg -n "activate_memory_break_read|read_with_bp_checks|check_breakpoints_on_mem_access|dbg_update|pDebugStep" /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src tools/oracle`

`mkdir -p scratch/agent/oracle_results/s961_read_watch`

Use the existing oracle binary and ROM, with a short bounded run and both
`--watch-read 0x00001000:0x00001004` and the whole-RDRAM write control. Preserve
`--vi-poll --verbose --press 6:start`; the whole-RDRAM watch must visibly fire.
