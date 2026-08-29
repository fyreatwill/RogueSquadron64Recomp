# NEXT work unit — external retail-entry boundary oracle handoff

HYPOTHESIS-ID: external-retail-entry-boundary-revisit

## Single work unit

Run one independent retail-oracle experiment to identify a new post-boot
handoff predecessor for the title/hangar transition. The generated-symbol
sweep is parked: all four remaining project `fake_func_*` entries have
bounded audits, and `0x800B75C4` was revalidated this iteration.

## Competing hypotheses

- H-ExternalCallsite: a retail CPU callsite outside the previously rejected
  four candidate PCs transfers into the VI/title route.
- H-WrapperChain: the transition is mediated by a stable internal wrapper;
  the useful discriminator is its predecessor histogram at the target phase.
- H-NoTarget: the watched execution boundary is not reached under the
  validated input schedule, so this oracle recipe cannot select a handoff.

## Discriminating measurement

The oracle run must pass a whole-RDRAM positive-control write watch, reach
retail title `0x00790400` and hangar `0x006AB400`, and collect a bounded
`osViSwapBuffer` predecessor histogram plus phase-gated execution rows. A
new post-boot predecessor selects H-ExternalCallsite or H-WrapperChain;
missing title/hangar phases selects H-NoTarget and makes the handoff null
unevaluable. Do not add port instrumentation until the oracle supplies a
ground-truth PC.

## Exact commands

1. Confirm the oracle binary and ROM paths, then run one 180-second retail
   capture from the repository root with `--watch-write 0x0:0x800000` as the
   positive control, `--watch-pc 0x80035500`, `--pc-hist-phase 0x00790400:1024`,
   `--pc-hist-phase 0x006AB400:512`, `--press` using the validated named
   button schedule from `tools/oracle/README.md`, and a Rice video plugin.
2. Save the output under `scratch/agent/` with a non-dot final path
   component; report the positive-control count, VI phases, and predecessor
   table before deciding whether a port-side instrument is justified.
