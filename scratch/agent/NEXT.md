# Next work unit (s4371): compare selected words against published payloads

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4370 capture independently qualified the physical payload boundary:
whole-RDRAM control reached 10,000 callbacks, all three phase buckets were
live, and the 32-byte phase snapshots matched the distinct title/hangar task
families. It did not establish whether C904/C950 selected words are copied
into the published payload or transformed later.

Competing hypotheses:

- H-pre-filter-origin: selected C904/C950 words are directly reflected in the
  published payload words.
- H-later-consumer-transform: selected words are zero/unrelated while the
  consumer publishes a distinct phase-specific payload family.
- H-watch-boundary: the apparent mismatch is caused by incomplete physical
  observation or phase/task mis-joining.

Discriminating measurement: one qualified retail run retaining the
whole-RDRAM control and all three VI buckets, with `--c904-witness
--c904-task-join` and typed `0x80033FCC` rows. Compare every retained
`selected_word`/selected address with the first eight payload words for the
same joined row. Exact recurrence in the payload selects H-pre-filter-origin;
stable non-equality with valid phase-family snapshots selects
H-later-consumer-transform; missing snapshots or joins selects
H-watch-boundary. Reject missing positive control, any phase bucket, or fewer
than 1,000 valid joins.

Exact run shape: Rice retail route for 75 seconds with the established Start
schedule, `--watch-write 0x0:0x800000`, 32-byte phase-latched payload watches,
`--watch-pc 0x80033FCC`, `--pc-task-dump 0x80033FCC --pc-task-type 2
--pc-task-join`, `--c904-witness --c904-task-join`, explicit phase buckets
`0x00790400:1024`, `0x00790800:1024`, `0x006AB400:512`, and `--vi-trace`.
Kill with SIGKILL after the watchdog; do not build unless the payload watch
requires a source change.
