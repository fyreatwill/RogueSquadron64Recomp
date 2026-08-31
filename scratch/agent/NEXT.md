# NEXT work unit — capture retail title transition with all-width latches

HYPOTHESIS-ID: retail-title-transition-all-width

Session 3322 showed the 4096-row any-VI join is live and not overflowing,
but its 640-only latch filter retained no 640→1024 row. The configured
Windows/MIPS PatchesLib host remains an external dependency.

## Competing hypotheses

- `H-ImmediateTitleSwap`: an all-width latch retains a row with pre-width 640
  and next width 1024, identifying the exact retail publication ordering.
- `H-NonImmediateTitleSwap`: title 1024 occurs, but no 640-pre-width latch
  joins to it, so the mode transition is not immediately after that swap edge.
- `H-OtherCaller`: the target transition follows a swap from a different
  caller or width, naming a distinct retail publication path.

## Discriminator

Change the oracle post-swap latch to accept every watched swap width while
recording and printing the pre-width. Build once and run the same Rice-backed
90-second capture. The whole-RDRAM watch and VI trace are positive controls.
Classify rows where `pre_width=640` and `next_width=1024`, retaining swap
caller/origin and pending/dropped/overflow counts. A matching row selects
`H-ImmediateTitleSwap`; no matching row with title 1024 live selects
`H-NonImmediateTitleSwap`; a matching row with a different caller selects
`H-OtherCaller`.

## Exact command

```sh
apply_patch  # latch all swap widths, retain/report pre_width
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core "$PWD/../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom "$PWD/../rogue_squadron64/rogue_squadron.z64" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 90 --watch-write 0x0:0x800000 --watch-pc 0x80035500 --pc-phase-log-width 0x00790400:1024 --post-swap-table-pc 0x80035500 --post-swap-any-vi --vi-trace
```

No M5 Step 3 or port behavior change is authorized by this capture alone.
