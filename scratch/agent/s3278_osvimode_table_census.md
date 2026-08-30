# Session 3278 — OSViMode table census after the delay-slot fix

HYPOTHESIS-ID: m5-osvimode-table-census

## Competing hypotheses

- `H-PendingBitGap`: at or after the 640 commit, at least one of
  `0x80128D50+{0,0x50,0xA0,0xF0}` has width 1024 at +8, but
  `applyPendingViChanges` does not publish it (pending bits never include
  `0x9`).
- `H-MissingTableRewrite`: none of the four slots has width 1024 at +8
  during the 60s run, including after the 640 commit.
- `H-RequestMaskNever1024`: `requestViFeatureChange` / `beginSceneRenderFrame`
  `$a0` after the 640 commit never sets the pending bits that would select
  a 1024 slot (informative if a 1024 template exists).

## What ran

Host dump `[vi-mode-table]` in `osViSetMode_recomp` immediately after each
existing `[osViSetMode]` row: four slot widths, pendingA/B, `(pendingA|pendingB)&0x9`,
selector bytes `0x8011A865/64/62`. Debug rebuild. One 60s
`ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1` run from `build/`,
killed with SIGKILL. Capture:
`scratch/agent/s3278_osvimode_table_census.log`.

No audio behavior change. No M5 Step 3.

## Same-run positive controls

- `[osViSetMode]` printed four rows, including swapBuffer dest `0x80128C90`
  width 320.
- `[vi-mode-table]` printed on the next line of each of those four rows
  (deltas 1, 1, 1, 1). A silent dump would have been a failed instrument.
- `[m5-port-vi-control]` fired at requested/committed width 640 origin
  `0x66A500`.

## Table

| Call | site | mode_ptr | req | slot0 | slot1 | slot2 | slot3 | pendingA/B | mask9 | sel |
|---:|---|---|---:|---:|---:|---:|---:|---|---:|---|
| 1 | initVideoSubsystem | `0x80128DA0` | 320 | 320 | 320 | 320 | 320 | 0/0 | 0x0 | 00/00/00 |
| 2 | swapBufferWithViMode | `0x80128C90` | 320 | 320 | 320 | 320 | 320 | 0/0 | 0x0 | 00/00/00 |
| 3 | initVideoSubsystem | `0x80128E40` | 640 | 640 | 640 | 640 | 640 | 0/0 | 0x0 | 00/00/00 |
| 4 | applyPendingViChanges | `0x80128DF0` | 640 | 640 | 640 | 640 | 640 | 0/`0x11` | 0x1 | 01/00/01 |

`[phase]` was `0 → 320 → 640/0x0066A500`. Zero width-2 rows. Zero 1024
`[osViSetMode]`, `[vi-mode-table]`, `[phase]`, or `[m5-port-retail-target]`
rows. No crash/abort/Bus-error/last-guest-pc.

Call 3 and call 4 requested different 640-wide types (`0x09000000` vs
`0x0B000000`); every slot width was uniform at each snapshot. The 320→640
rewrite is the `initVideoSubsystem` 4×0x50 copy at `0x8001B6A8` from stack
templates into `0x80128D50`. No third `initVideoSubsystem` `osViSetMode`
ran.

## Classification

- `H-PendingBitGap` is refuted: no slot was ever 1024, and at call 4
  `pending_mask9=0x1` so `applyPendingViChanges` did publish — it published
  the 640-wide slot `0x80128DF0`.
- `H-MissingTableRewrite` is selected (single-source port census): none of
  the four slots had width 1024 at any of the four publisher snapshots,
  including the post-640 applyPending call.
- `H-RequestMaskNever1024` is not selected. It is informative only if a
  1024 template exists. `pendingB=0x11` at call 4 shows
  `requestViFeatureChange` did set the 0x9-family bit; the live pending
  path selected a 640 slot because that is all the table contained.

`H-PortTargetPublicationAbsent` still holds. This does not yet say whether
retail's four-slot table ever contains 1024 at title; that is the next
independent ground-truth question.
