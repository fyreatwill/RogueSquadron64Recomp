# NEXT work unit (s2492) — retail/port OSTask join at osSpTaskYielded

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Capture the retail task fields at `osSpTaskYielded` (`0x80034450`) and compare
them with the corrected port descriptor rows. Use the oracle whole-RDRAM
positive control first, then one retail run with the target phase bucket and
the task dump. Do not change task dispatch, audio behavior, or any guard.

Before building, write the comparison table in this file. Run the oracle with:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 70 --watch-write 0x0:0x800000 --watch-pc 0x80034450 --pc-phase-log-width 0x006AB400:512 --pc-task-dump 0x80034450`

## Competing hypotheses and discriminator

- H-retail-matches-corrected-port: retail `type`, `data_ptr`, `data_size`,
  `yield_data_ptr`, and output fields join the corrected port descriptor rows.
- H-retail-differs-from-port: the same phase-gated retail task rows differ,
  leaving generated-alternate equivalence unresolved at the task boundary.

The discriminator is the joined field table at `0x006AB400` / width 512, with
the oracle positive-control row present. A field-by-field retail/port match
selects the equivalence hypothesis; a mismatch refutes it. A zero task-dump
row count is invalid until the positive control and watched-PC control both
fire.
