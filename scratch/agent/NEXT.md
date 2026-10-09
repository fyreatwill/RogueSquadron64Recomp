# Next work unit (s4370): independently confirm phase-specific task payloads

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4369 capture qualified the selector/task boundary: whole-RDRAM control
reached 10,000 callbacks, all three phase buckets were live, and 4,485 of
4,488 C904/C950 witnesses joined valid type-2 task rows. The canonical input
remained `0x04001000` with words `0x09000419/0x20010FC0`, while title payload
families were rooted at `0x80178C80` and hangar payloads at `0x801797B0`.

Competing hypotheses:

- H-selector-multiplex: valid task rows publish phase-specific payload families
  despite the canonical selector input being constant.
- H-watch-boundary: the apparent family split is caused by incomplete physical
  payload observation or phase/task mis-joining.
- H-pre-filter-origin: selected C904/C950 fields are directly reflected in
  the published payload words.

Discriminating measurement: one qualified retail run retaining the
whole-RDRAM control and all three VI buckets, while independently watching the
phase-latched physical payload blocks at `0x80171CE0`, `0x80173B20`, and
`0x80171E70` and retaining `--c904-witness --c904-task-join` plus typed
`0x80033FCC` task rows. Stable snapshots matching the joined task payloads
and phase-specific roots corroborate H-selector-multiplex; absent or
misaligned snapshots select H-watch-boundary; direct selected-word equality
would revive H-pre-filter-origin. Reject missing positive control, any phase
bucket, or fewer than 1,000 valid joins.

Exact run shape: Rice retail route for 75 seconds with the established Start
schedule, `--watch-write 0x0:0x800000`, phase-latched payload watches,
`--watch-pc 0x80033FCC`, `--pc-task-dump 0x80033FCC --pc-task-type 2
--pc-task-join`, `--c904-witness --c904-task-join`, explicit phase buckets
`0x00790400:1024`, `0x00790800:1024`, `0x006AB400:512`, and `--vi-trace`.
Kill with SIGKILL after the watchdog; do not build unless the payload watch
requires a source change.
