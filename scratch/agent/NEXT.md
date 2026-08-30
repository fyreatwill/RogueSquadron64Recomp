# NEXT work unit — align the retail VI selector read watch

HYPOTHESIS-ID: vi640-request-state-read-edge

Run one independent retail-oracle capture using an aligned selector-word
watch. Session 3266 proved the pending-state read surface is live, but the
byte watch at `0x8011A865..67` missed likely aligned word loads. Do not repeat
the entry-only capture, local inventory, or add a port-side field.

## Competing hypotheses

- `H-RequestState`: pending/selector state is live but never selects the
  title-width descriptor, suppressing the request.
- `H-BoundaryConsumer`: the target-width request is selected and issued, but
  the VI consumer fails to commit it.
- `H-Phase4SteadyState`: retail's state contract remains explicitly on the
  640 route and makes no target request.
- `H-SelectorWatchUnavailable`: aligned selector reads still cannot be
  attributed; this is an instrument result, not a runtime conclusion.

## Discriminator

The run must pass the whole-RDRAM write control and reach title 1024 plus
hangar 512. Detail aligned reads covering selector A/B/C at physical
`0x00114A864..0x00114A86C`, alongside pending A/B reads at
`0x00128E94..0x00128E9C`, and correlate their PCs with
`applyPendingViChanges`/`0x8001B8DC` and VI transitions. A selector state that
stays in the 640 record with no target request selects `H-RequestState`; a
target request with no target commit selects `H-BoundaryConsumer`; an explicit
stable terminal contract selects `H-Phase4SteadyState`; absent aligned rows
selects `H-SelectorWatchUnavailable`.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --secs 60 --watch-write 0x0:0x800000 \
  --watch-read 0x114A864:0x114A86C --watch-read 0x128E94:0x128E9C \
  --detail-watch 1 --detail-watch 2 \
  --watch-pc 0x8001B7F0,0x8001B8DC,0x800352D0 \
  --pc-phase-log-width 0x0066A500:640 --vi-trace --hit-cap 64
```

Capture output under `scratch/agent/` with a non-dot final path. No build or
port/audio behavior change is authorized until this aligned state edge is
classified.
