# NEXT work unit — independent retail target publication capture

HYPOTHESIS-ID: m5-retail-target-publication-capture

Session 3319 rescoped the configured-host PatchesLib validation. The host
build remains an open dependency, but this next discriminator does not
require it. Do not repeat the local missing-target build or MIPS inventory.

## Competing hypotheses

- `H-RetailTargetSwap`: retail publishes the target framebuffer through the
  watched `osViSwapBuffer` edge and the post-swap join closes.
- `H-RetailTargetModeOnly`: retail changes the target mode/context but no
  watched target swap joins, so publication is a separate edge.
- `H-RetailTargetUnreached`: the controlled run does not reach the target
  phase, so a null cannot classify publication.

## Discriminator

Run the existing retail oracle once with a whole-RDRAM write positive control,
phase-gated target execution watch, and post-swap join. Joined rows containing
the target transition select `H-RetailTargetSwap`; target mode rows without a
swap select `H-RetailTargetModeOnly`; no target transition with controls
passing selects `H-RetailTargetUnreached`.

## Exact command

```sh
tools/oracle/build/rs64_oracle --core <debugger-core.dylib> \
  --rom <retail-rom.z64> --secs 90 \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x80035500 --pc-phase-log-width \
  --post-swap-any-vi
```

Record the positive-control count, VI transition, watched caller/GPR row, and
post-swap joined table in a new evidence file. No M5 Step 3 or behavior
change is authorized by this capture alone.
