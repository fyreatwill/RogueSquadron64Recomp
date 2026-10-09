# Next work unit (s4426): attribute the allocator block for the title pointers

HYPOTHESIS-ID: m5-selector-alloc-return

Session 4425 selected H-pretitle-same-writer. On the last 640-wide frame
(origin `0x00790500`), before the 1024 title switch, `0x8008F228` stored
`0x80171CE0` and `0x8008F264` stored `0x80173B20`. Both words had started at
0. Straight-line code between `jal 0x80001ACC` and either `sw v0` does not
write `v0`. The callee clears `s2`, sets `s2 = a1 + 16` at `0x80001C10`,
and copies `s2` to `v0` at `0x80001C74` before the epilogue restores `s2`.

Competing hypotheses:

- H-freelist-header: on that frame, the two calls whose return address is
  the store function execute `0x80001C10` with `a1+16` equal to
  `0x80171CE0` and `0x80173B20`. The header at `a1` is the producing block.
- H-other-s2: the store control is live, but `v0` at `0x80001C74` is not
  `a1+16` from `0x80001C10` for those calls.
- H-join-failure: the establishing store rows or the `0x80001C10` watch do
  not fire in the same run.

Discriminating measurement: one retail oracle capture, no pc-range over a
hot function. Keep `--store-field-dump-all` on both table words with
`--store-field-dump-any-phase` as the positive control (the
`0x00790500` rows must reappear). Add `--watch-pc 0x80001C10` and
`--pc-phase-log-width 0x00790500:640` so that frame's allocator GPR rows
print. Record `a1`, `s2` after the addiu, and `ra`. Do not rewrite heap
state.

Exact commands:

1. No rebuild unless the oracle binary is older than `tools/oracle/rs64_oracle.c`.
2. Run from the repo root with `--oracle-emulator 1`, Rice, the Start-press
   schedule, `--secs 50` (the establishing frame is ~16s), whole-RDRAM
   watch 0, the two physical table watches, and the watches above.
3. Kill with SIGKILL. Require the whole-RDRAM line, the two establishing
   store rows, and at least one `0x80001C10` row on origin `0x00790500`
   before interpreting a mismatch.
