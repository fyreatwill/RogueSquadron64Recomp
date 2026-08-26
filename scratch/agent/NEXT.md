# NEXT work unit (s2493) — retail/port OSTask join at osSpTaskLoad

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Capture retail task fields at `osSpTaskLoad` (`0x80033E3C`) and compare them
with corrected port descriptor rows. Use the whole-RDRAM positive control in
the same run, then the documented driven Rice/Start schedule. Do not change
task dispatch, audio behavior, or guards.

Command:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-pc 0x80033E3C --pc-phase-log-width 0x006AB400:512 --pc-task-dump 0x80033E3C --vi-trace --vi-poll --pif-trace`

## Competing hypotheses and discriminator

- H-retail-load-matches-corrected-port: retail `type`, `data_ptr`,
  `data_size`, `yield_data_ptr`, and output fields join the corrected port
  descriptor rows.
- H-retail-load-differs-from-port: the phase-gated retail task rows differ,
  refuting equivalence at the task boundary.
- H-retail-load-is-not-the-task-boundary: the exact load PC has no target-phase
  rows while its containing SP block executes; move to the caller only then.

The discriminator is the joined table at origin `0x006AB400`, width 512. The
whole-RDRAM control, VI/PIF controls, and an execution hit at `0x80033E3C` must
all be present. A field match selects equivalence; a mismatch refutes it. Zero
task rows are valid only for the third hypothesis when the containing block
executes in the target phase.

| Field | Corrected port s2491 | Retail oracle | Outcome |
|---|---|---|---|
| `type`, data/yield/output fields | corrected aligned OSTask rows | pending | match / mismatch |
| whole-RDRAM control | 10,000 callbacks required | required | invalid without it |
| VI/PIF controls | target origin and input path | required | invalid without them |
| watched PC | phase-gated port join | `0x80033E3C` target hit | third hypothesis if absent |
