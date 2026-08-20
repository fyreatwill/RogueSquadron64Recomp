# NEXT work unit (s2019) — witness runtime service dispatch

HYPOTHESIS-ID: m5-service-runtime-dispatch-witness

## Work unit

Ask the retail oracle for an execution watch at `0x8009B5A8` with a same-run
whole-RDRAM write control. Then add one target-resolution witness in
`lib/N64ModernRuntime/librecomp/src/overlays.cpp:get_function` and run the
existing phase-valid port recipe `scratch/s73_post_a_scene/run_mission_keys.sh`
from one build. Do not change status, audio, spin, PI, guard, or mitigation
behavior. Export any lib submodule patch in the same iteration.

The s2018 crosswalk already established that this is base text, not an
overlay: `section_3_text_funcs` has `ROM 0x1040`, `RAM 0x80000440`, and the
`0x9B168` entry maps to `0x8009B5A8`; the generated definition and linked
symbol are present, but no incoming named reference or direct host branch was
found.

## Competing hypotheses and discriminator

- H1: The port route never requests the service function. The target branch of
  `get_function` is absent, while the existing `ROGUESQ_LOG_DMA_CALLER=1`
  resolution control fires and the service entry remains absent.
- H2: The route requests `0x8009B5A8`, but the runtime map is absent or returns
  a function other than `_serviceVoicePoolFrame`. The target-resolution row
  records a miss or wrong host pointer.
- H3: The audio-disabled guest path suppresses the request. The target branch
  is absent, the retail oracle execution watch hits in a phase-valid run, and
  the same port run shows the existing audio-gate rows without a service
  entry.

The discriminator is one table containing oracle whole-RDRAM-control count,
oracle target-PC hits, port positive-control resolution, target resolution and
returned host pointer, service entry, and audio-gate rows. Target resolve plus
entry selects live dispatch and closes this boundary; target resolve plus a
miss/wrong pointer selects a runtime map defect; no target request with both
positive controls live splits H1 from H3 using the oracle PC and gate rows. If
the table cannot split H1/H3, stop and redesign before another build/run.

## Exact commands

Ground truth first; build the oracle only if its executable is absent:

```sh
if [[ ! -x tools/oracle/build/rs64_oracle ]]; then
  (cd tools/oracle && ./build.sh)
fi
```

Run the retail control/watch from the repository root, using the existing
debugger-enabled core and the Rice path:

```sh
tools/oracle/build/rs64_oracle \
  --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom ../rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 80 --hit-cap 10000 --watch-write 0x0:0x800000 \
  --watch-pc 0x8009B5A8 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/soak_results/s2019-retail-service-watch.log 2>&1
```

Add the target-resolution row to `get_function` in one instrumented build;
retain the existing `ROGUESQ_LOG_DMA_CALLER` path as its same-run positive
control. Build and run the port recipe with all passive M5 breadcrumbs:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2019-runtime-dispatch 30 12
```

Capture the bounded rows without reading the full log:

```sh
rg -n -e '\[svc-resolve\]' -e '\[s2006-svc\]' -e '\[dma-ring-caller\]' -e '\[phase\]' -e '\[gate\]' scratch/s73_post_a_scene/s2019-runtime-dispatch/run.log
```
