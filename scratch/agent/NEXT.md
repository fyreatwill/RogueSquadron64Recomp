# NEXT work unit — map the retail VI selector region

HYPOTHESIS-ID: vi640-request-state-read-edge

Run one independent retail-oracle capture with a wider, aligned read watch
covering the selector's surrounding physical region. Session 3267 passed the
whole-RDRAM positive control and reached title 1024 plus hangar 512, but the
candidate selector range `0x00114A864..0x00114A86C` had zero reads. Do not
repeat the entry-only capture, add a port-side field, or change audio behavior.

## Competing hypotheses

- `H-SelectorAtNeighbor`: the selector is read at a nearby aligned address
  outside the narrow candidate range.
- `H-SelectorNotRead`: the selector is not read during the observed title and
  hangar phases; the current state-edge model is aimed at the wrong consumer.
- `H-SelectorWatchAliasing`: the oracle's physical watch boundary or detail
  attribution prevents observing the relevant load despite the positive
  control.
- `H-RequestState`: the selector is live but suppresses the target request;
  retain this only if a selector-region hit carries the expected boundary PC
  and state can be correlated with the VI transition.

## Discriminator

The run must pass the whole-RDRAM write control and reach title VI 1024 plus
hangar VI 512. Watch physical `0x00114A800..0x00114A900` with detail, plus
pending state `0x00128E94..0x00128E9C`, and correlate rows with
`0x8001B7F0`, `0x8001B8DC`, `0x800352D0` and VI transitions. A hit in the
neighbor region tied to the boundary selects `H-SelectorAtNeighbor`; zero
selector-region reads with positive control selects `H-SelectorNotRead`; a
watch hit that cannot be attributed or a positive-control boundary anomaly
selects `H-SelectorWatchAliasing`. A state-correlated selector hit that stays
on the 640 record selects `H-RequestState`.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --secs 60 --watch-write 0x0:0x800000 \
  --watch-read 0x114A800:0x114A900 --watch-read 0x128E94:0x128E9C \
  --detail-watch 1 --detail-watch 2 \
  --watch-pc 0x8001B7F0,0x8001B8DC,0x800352D0 \
  --pc-phase-log-width 0x0066A500:640 --vi-trace --hit-cap 256
```

Capture output under `scratch/agent/` with a non-dot final path. No port or
audio behavior change is authorized until the selector region is classified.
