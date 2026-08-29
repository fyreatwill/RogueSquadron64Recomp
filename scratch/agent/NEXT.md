# NEXT work unit — ground the upstream route divergence in retail

HYPOTHESIS-ID: m5-audio-route-upstream-boundary

## Single work unit

Use one static audit of the MIPS `__osViSwapContext` boundary to identify a
genuinely different named handoff for the next retail oracle run. The exact
`0x800356A8` candidate was absent in retail even though title/hangar controls
were valid, so do not repeat it or the closed `0x80034F38:0x800356AC` range.
Session 3126's port probe had valid controls (VI-context 8 rows and host
voice-audit 1 row), but the port reached only VI 640 and had zero rows from
the retail-live continuation. Audio and route behavior remain out of scope.

Static audit candidate: `0x80035788` is the `sw` that publishes the selected
origin to `VI_ORIGIN_REG` (`0xA4400004`); `0x80035798` is the subsequent width
store. This is a distinct origin-publication PC, not the rejected `0x800356A8`
or the closed pre-consumer range.

## Competing hypotheses

- H-NewStaticHandoff: `0x80035788` executes in retail during target phases,
  giving direct attribution for origin publication at the VI consumer edge.
- H-NoDistinctHandoff: the audited instructions are already covered or have
  no independent execution edge; choose the highest-information non-consumer
  boundary instead.
- H-RetailControlInvalid: the whole-RDRAM positive control or title/hangar
  phase markers fail, so the oracle result is unevaluable.

## Discriminating measurement

The oracle run must pass the whole-RDRAM control and reach title/hangar; a
target-phase row for `0x80035788` selects H-NewStaticHandoff, no row with
valid controls selects H-NoDistinctHandoff, and missing controls select
H-RetailControlInvalid.

## Exact commands

1. Run one oracle capture with `--watch-write 0x0:0x800000`,
   `--watch-pc 0x80035788`, Rice, VI tracing, and the verified Start schedule.
2. Record the positive-control count, title/hangar phases, and candidate-PC
   rows; do not add a port instrument until the writer/consumer PC is named.
