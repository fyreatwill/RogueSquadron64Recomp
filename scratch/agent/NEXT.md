# NEXT work unit — census OSViMode table slots after the delay-slot fix

HYPOTHESIS-ID: m5-osvimode-table-census

Session 3277 selected `H-DelaySlotNotCausal`: swapBufferWithViMode now
requests copied-mode dest `0x80128C90` width 320, the width-2 phase is
gone, and the port still stops at `640 @ 0x0066A500` with no 1024 request.
`H-PortTargetPublicationAbsent` still holds. The remaining gap is whether
a 1024-width OSViMode template exists in the four-slot table and is simply
never applied, or the table is never rewritten to 1024.

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

## Discriminator

One host dump inside `osViSetMode_recomp` (already the live publisher log)
that, on every call, prints the four slot widths at
`0x80128D50+{0,0x50,0xA0,0xF0}+8`, pendingA/B, and selector bytes. One 60s
`ROGUESQ_LOG_ALL=1` run. A 1024 width in any slot with no later
`applyPendingViChanges` 1024 request selects `H-PendingBitGap`. All four
slots never 1024 selects `H-MissingTableRewrite`. Do not treat a 1024
`[osViSetMode]` as the predicted success of Session 3277.

Positive control: the dump prints on each of the four existing
`[osViSetMode]` rows (including swapBuffer `0x80128C90` width 320). A dump
that is silent on those rows is a failed instrument, not a missing table.

## Exact command

From the repository root:

```sh
# 1. In src/main/upstream_compat.cpp osViSetMode_recomp, after the existing
#    [osViSetMode] fprintf, dump:
#      for i in 0..3: width at MEM (0x80128D50 + i*0x50 + 8)
#      pendingA 0x80128E94, pendingB 0x80128E90,
#      sel 0x8011A865/64/62
#    Tag: [vi-mode-table]. Rate-limit: every call (there are four).
# 2. Rebuild and capture:
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 \
  zsh -c 'cd build && ./RogueSquadron64Recomp' \
  > scratch/agent/s3278_osvimode_table_census.log 2>&1 &
# after 60s: kill -9 the game (SIGKILL), not SIGTERM
```

Do not change audio behavior. Do not run M5 Step 3. Do not repeat the
local missing-target `PatchesLib` build.
