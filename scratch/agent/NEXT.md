# NEXT work unit (s2057)

HYPOTHESIS-ID: m5-service-store-edge

## Work unit

Add one regeneration-stable, diagnostic-only join to the service worker and
status-store anchors in `N64Recomp/fixup_game_funcs.py`. Regenerate in the
required order, build once, and run one qualified C88=1 port arm. The event
table must be phase-scoped and join slot 0's status-3 read, service entry and
exit, the exact status-zero store at guest `0x8009B7EC`, the store address and
old value, shutdown ordinal/return, and callback/PCM controls. Do not change a
guest store, wait, guard, audio task result, callback, or default behavior.

## Competing hypotheses and discriminator

- **H-S — worker clears:** the qualified status-3 interval is the real worker
  contract. A slot-0 status-3 read is followed by service entry, the exact
  worker status-zero store for the same slot, and a clean shutdown/reaping
  return.
- **H-N — worker does not clear:** service entry/exit may be live, but no
  status-zero store follows the status-3 read; the same slot remains `0x03`
  and shutdown does not return.
- **H-W — alternate writer:** the status-3 read is real but the zeroing store
  comes from a different writer or address. Retail writer-PC/watch evidence and
  the port event table identify that writer rather than the service worker.
- **H-J — join/instrument failure:** the existing `[s2020-svc]` status-3
  positive control fires, but the new phase/slot join cannot observe the
  expected read or store. This selects a measurement defect and blocks any
  worker conclusion.

The discriminator is one phase-keyed chain table:
`status3-read(slot=0,address,status=3)` -> `service-entry/exit` ->
`service-store(pc=0x8009B7EC,slot,address,old,new=0)` -> status-zero read and
shutdown return. H-S requires the same slot/address chain and return. H-N
requires a live status-3 control with persistence and no store. H-W requires
an independent writer PC/address. H-J is selected only when the existing
service positive control fires but the new join's control row is absent.
Same-run positive controls are the retail whole-RDRAM watch, retail service
PC/write watches, port title VI 1024, hangar VI 512, `[s2020-svc]` status-3,
audio-task dispatch, and PCM source/consumer rows.

## Commands

```sh
# Ground truth first: whole-RDRAM control, slot-0 status word, worker/store PCs.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x154620:0x154624 \
  --watch-pc 0x8009B5A8,0x8009B8A0,0x8009B7EC,0x8009B2C4 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start \
  > scratch/agent/s2057_oracle.log 2>&1

# Regeneration-stable diagnostic change, then the one build.
cd /Users/williambuckley/Documents/Tools/rogue_squadron64
splat split roguesquadron.yaml
python3 tools/make_elf.py
cd /Users/williambuckley/Documents/Tools/N64Recomp
../RogueSquadron64Recomp/build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
cmake --build build --config Debug --target RogueSquadron64Recomp

route_keys='640@6:start 640@11:start 640@16:start 640@21:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'
env REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2057_m5_service_edge \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_S2028_A11=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2057_m5_service_edge 180 \
  > scratch/agent/s2057_m5_service_edge_driver.log 2>&1
```

Inspect the oracle positive-control and target-watch counts first. Then use
the port verdict and an `awk`/`rg` phase table to verify title/hangar anchors,
the status-3 control, event ordering, same-slot/address identity, shutdown
return, task controls, and PCM values. A missing new join with a live
`[s2020-svc]` control is H-J, not a null worker result.

ORIGIN: no guest writer, value, wait, guard, skip, audio task, callback, or default behavior changes; the work unit adds only regeneration-stable diagnostics.
