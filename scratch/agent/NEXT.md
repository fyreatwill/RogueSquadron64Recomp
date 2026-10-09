# Next work unit (s4423): split retail title preinitialization from bypass

HYPOTHESIS-ID: m5-selector-title-init-route

Session 4423 passed the corrected paired controls. Retail reached selector
load `0x80091060` 1,421 times, wrote the table zero times in title, and wrote
it in hangar at the expected PCs and values. The next boundary is whether title
loads consume preexisting table state or bypass the table route.

Competing hypotheses:

- H-retail-title-preinitialized: retail reaches the title load with a table
  value established before the phase-gated route.
- H-retail-title-bypass: retail's title selector path bypasses the table-store
  route entirely while still reaching the load PC.
- H-join-failure: the selector-load field or phase join is not positively
  qualified.

Discriminating measurement: one retail oracle capture must pass whole-RDRAM,
title/hangar VI, selector-load, and hangar table-write controls, then retain
the selector-load field dump and title caller/preceding rows. Same table value
and index at title load selects H-retail-title-preinitialized; a distinct
selector field or caller path selects H-retail-title-bypass; failed controls
select H-join-failure.

Exact commands:

1. Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
2. Run the retail oracle from the repo root with `--oracle-emulator 1`,
   `--watch-write 0x0:0x800000`, physical table watches
   `0x00149758:0x0014975C` and `0x0014975C:0x00149760`,
   `--watch-pc 0x80091060`, `--watch-pc-range 0x8008E000:0x80091340`,
   `--pc-field-dump 0x80091060`, and phase-gated title/hangar buckets. Keep
   `--pc-hist-watch`/`--post-value-watch` for both table watches.
3. Run the qualified port arm concurrently from `build/` with the existing
   real-audio/LLE/ungated/solo/spin-yield route and selector witnesses.
4. Kill with SIGKILL. Require selector/table, field, VI, task, image, and
   positive-control markers before interpreting any null.
