# NEXT work unit (s2288) — M5 Step 2 default audio arm qualification

HYPOTHESIS-ID: m5-step2-default-audio-arm

## Work unit

Make the Factor 5 audio image the default `M_AUDTASK` dispatch arm while
retaining an explicit `ROGUESQ_AUDIO_UCODE=0` stub escape. Build once, then
run both arms from that same executable: launch the stub control first and
launch the default-image arm only after the stub reaches the title and hangar
VI phases. This is the first behavior change in the M5 plan; do not add a
guard, skip, writeback, C88 override, or route workaround.

## Competing hypotheses and discriminating measurement

- H-DefaultSafe: the default image reaches the same title/hangar route as the
  stub control, completes its task, and preserves the already qualified
  image-stage and PCM joins without a new crash or task failure.
- H-ImageContractGap: both arms reach the target phases, but the default image
  still lacks a task/DMEM/DMA, service, slot/voice, or PCM source/consumer
  relation that the complete row requires. Keep the image opt-in and name the
  missing contract edge.
- H-DefaultRouteRegression: the stub control reaches title and hangar but the
  default image loses a route phase or introduces a new task/DMEM failure.
  Revert the default flip; this is a default-arm regression, not permission
  to add a mitigation.
- H-RouteInvalid: the retail positive control or stub title/hangar gate is
  absent. The default arm is not interpretable and must not be launched or
  promoted.

The discriminator is one table per arm, keyed by VI phase and route ordinal:
`audtask-dispatch → task ABI/source → DMEM change → DMA/readback → image
exit → SP completion → service entry/return → status/slot → voice/reap →
PCM source/consumer → title/hangar phase`. The independent retail oracle
must first pass the whole-RDRAM threshold and title/hangar controls. A stub
dispatch or an image `Broke` return alone is only a branch control, not a
successful audio result.

## Exact commands

1. Use `apply_patch` to change `src/main/main.cpp` in the cached
   `M_AUDTASK` selection block. Preserve the existing `=0` stub arm and make
   the selection equivalent to:

   ```cpp
   const char* e = getenv("ROGUESQ_AUDIO_UCODE");
   s_use_real_audio_ucode = !(e && e[0] == '0');
   ```

   Update the nearby stale “default remains musyx_stub” wording to describe
   the new default and the explicit stub escape; do not alter the image
   implementation or any downstream gate.

2. Build the single comparison executable:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

3. Use `apply_patch` to create
   `scratch/agent/run_s2288_m5_audio_default_step2.sh`. It must run from the
   repository root, check `build/RogueSquadron64Recomp` and the ROM, launch
   one independent retail oracle using the s2285 eleven-Start recipe and
   `--watch-write 0x0:0x800000 --vi-trace`, and require the oracle's
   `positive-control threshold reached: watch index 0 callbacks=10000` plus
   title `0x00790400`/1024 and hangar `0x006AB400`/512 before interpreting
   port rows. Arm the common route and bounded M5 diagnostics used by s2285:
   `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
   `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_M5_C88_VALUE=0`,
   `ROGUESQ_STUB_MISSING_FUNCS=1`, `ROGUESQ_LOG_PHASE=1`,
   `ROGUESQ_LOG_AUDIO_RETURN=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`,
   `ROGUESQ_LOG_PCM_BOUNDARY=1`, `ROGUESQ_LOG_M5_GATE_CONTRACT=1`,
   `ROGUESQ_LOG_FILTER_VOICE_AUDIT=1`, `ROGUESQ_LOG_M5_B40_ROUTE=1`,
   `ROGUESQ_LOG_M5_ROUTE_STATE=1`, `PROBE_PHASE_WIDTH=1024`, and
   `PROBE_KEYS_FROM_PHASE=1`.

   Launch the stub arm with `env ... ROGUESQ_AUDIO_UCODE=0`; after its
   `vi_width=512 origin=0x006AB400` gate, launch the default arm with
   `env ...` and no `ROGUESQ_AUDIO_UCODE` variable. Keep both captures,
   watchdog each arm, SIGKILL every remaining game/oracle process, and exit
   nonzero when a required gate is absent. Run the arms from `build/` with
   the ROM present; do not use SIGTERM.

4. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2288_m5_audio_default_step2.sh`

   `zsh scratch/agent/run_s2288_m5_audio_default_step2.sh`

5. Summarize only bounded driver summaries and marker counts for both arms:
   retail controls, arm route phases, task ABI/DMA/image rows, audio return,
   service/gate/slot/voice rows, PCM source/consumer rows, `[missing-func]`,
   `[CRASH]`, and `[ABORT]`. Do not interpret default-image nulls if either
   retail controls or the stub title/hangar gate is absent.

No image default promotion is complete until H-DefaultSafe is selected by the
full table and a later soak is queued with the same passive breadcrumbs.
