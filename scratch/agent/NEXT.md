# NEXT work unit — widen retail post-swap join

HYPOTHESIS-ID: m5-retail-post-swap-transition

The configured Windows/MIPS PatchesLib host remains an external dependency.
The next target-phase discriminator addresses Session 3320's live but
overflowing post-swap join without changing the runtime.

## Competing hypotheses

- `H-TargetTransitionCaptured`: increasing the join capacity retains a
  target-origin next-VI row, making the port/retail target relation testable.
- `H-NextVIIsNonTarget`: the join remains live but all retained next-VI rows
  are non-target, separating callback timing/transition from row overflow.
- `H-NoNextVI`: the watched swap has no subsequent VI callback in the run,
  which would identify a publication/termination issue in the oracle route.

## Discriminator

Raise `MAX_MODE_DUMP_ROWS` in `tools/oracle/rs64_oracle.c` from 256 to 4096,
build the oracle, and run the existing target publication recipe with
`--post-swap-table-pc 0x80035500 --post-swap-any-vi` added. The whole-RDRAM
watch and VI trace are positive controls; classify the retained next-VI rows
by width/origin and verify the shutdown overflow is zero. A target row selects
`H-TargetTransitionCaptured`; only non-target rows select `H-NextVIIsNonTarget`;
no joined row with live latches selects `H-NoNextVI`.

## Exact command

```sh
apply_patch  # change only MAX_MODE_DUMP_ROWS to 4096
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core "$PWD/../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom "$PWD/../rogue_squadron64/rogue_squadron.z64" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 90 --watch-write 0x0:0x800000 --watch-pc 0x80035500 --pc-phase-log-width 0x00790400:1024 --post-swap-table-pc 0x80035500 --post-swap-any-vi --vi-trace
```

Record the phase/row table and controls in a new evidence file. No M5 Step 3
or behavior change is authorized by this capture alone.
