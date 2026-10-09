# Next work unit (s4427): name the first writer of the two user buffers

HYPOTHESIS-ID: m5-selector-block-fill

Session 4426 selected H-freelist-header. On width 640, origin `0x00790500`,
`rs_malloc` split one free block into the two title pointers. Headers
`0x80171CD0` / `0x80173B10`, requests `0x1E30`, flags 0, user pointers
`0x80171CE0` / `0x80173B20`. The publisher at `0x8008F228` / `0x8008F264`
stores those pointers and returns without writing the user bytes. Its later
`jal 0x800078E0` fills a different 664-byte buffer.

Competing hypotheses:

- H-named-fill: after those stores and before the first title execution of
  `0x80091064`, a guest PC writes the first word of `0x80171CE0` or
  `0x80173B20`.
- H-residual: both controls are live and neither user word is written in
  that window. The selector load then reads leftover heap bytes.
- H-join-failure: the establishing table stores or the `0x80091064` rows
  do not appear in the same run as the user-word watches.

Discriminating measurement: one retail oracle capture. No execution watch
on `rs_malloc`. Keep `--store-field-dump-all` and
`--store-field-dump-any-phase` on the two table words so the
`0x00790500` rows reappear. Watch writes of the first user word at physical
`0x171CE0` and `0x173B20` for the whole run. Phase-print `0x80091064` at
title origins `0x00790400:1024` and `0x00790800:1024` with `--exec-no-defer`
so the watch is armed before that frame; do not add a phase that arms only
at `0x00790500`, because that VI callback is after the stores. Record writer
PC, value, width, and origin for any user-word store. Do not rewrite heap
state.

Exact commands:

1. The oracle binary must be newer than `tools/oracle/rs64_oracle.c` (the
   `--exec-no-defer` flag). Rebuild with `bash tools/oracle/build.sh` only
   if it is older.
2. Run from the repo root with `--oracle-emulator 1`, Rice, the Start-press
   schedule, `--secs 25`, whole-RDRAM watch 0, the two table watches, the
   two user-word watches, and `--watch-pc 0x80091064` gated as above.
3. Kill with SIGKILL. Require the whole-RDRAM line, both establishing store
   rows, and at least one `0x80091064` row whose `v0` is `0x80171CE0` or
   `0x80173B20` before calling a zero-write result residual.
