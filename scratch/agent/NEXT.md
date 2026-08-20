# NEXT work unit (s2063)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Narrow the opt-in image arm's broad RDRAM DMA band into exact phase-keyed
DMA-to-PCM joins. s2062 established from the independent retail ROM that
`0x166000..0x17A000` is written by named MusyX mixer/command-list PCs, but
that band is too broad to prove final PCM. Extend the existing
`AudioDmaRange`/PCM boundary census with one joined table per image task:
task ordinal and VI phase; DMA direction, DMEM source, guest address, length,
payload FNV, and nonzero-byte count; matching `queue_audio_buffer` and
`queue_samples` address/count/FNV/nonzero fields; temporal order; and the
reserved-DMEM/canary result. Do not change dispatch, the guest gate, C88,
wait/slot guards, the canary contents, or default behavior.

## Competing hypotheses and discriminator

- **H-ImageDmaFeedsPcm** — an image-arm DMEM-to-RDRAM range with nonzero
  payload joins the same phase/task's `queue_audio_buffer` and
  `queue_samples` rows on address, byte count, FNV, and nonzero count, in
  producer-before-consumer order. The image output is real at that scope;
  the remaining issue is task exit/canary semantics.
- **H-ImageDmaStagingOnly** — image DMA ranges do not join the PCM source or
  consumer rows, or only join zero/retained rows. The retail-owned band is
  audio work/state storage, not the current task's PCM output.
- **H-ImageOutputDiscarded** — image DMA joins the source but not the
  consumer, or joins with a mismatched span/hash/order. The image produces a
  candidate buffer that the guest/host boundary discards or replaces.
- **H-RouteUnevaluable** — the same-run image task, `[audtask-dispatch]`,
  `[pad-host]`, title VI 1024, or hangar VI 512 controls are absent; no PCM
  interpretation is allowed.

The discriminator is the complete phase-keyed join table, not a new scalar
counter. H-ImageDmaFeedsPcm requires at least one nonzero exact join and no
unexplained nonzero image range in the target phases; H-ImageDmaStagingOnly
requires live task/PCM controls but zero exact joins; H-ImageOutputDiscarded
requires a source-only, consumer-mismatch, or ordering-mismatch pattern.
Missing controls select H-RouteUnevaluable.

## Exact commands

Before editing, read the Factor 5 command reference and locate the existing
range/boundary fields:

```sh
sed -n '1,220p' docs/F5-UCODE-REFERENCE.md
rg -n 'AudioDmaRange|queue_audio_buffer|queue_samples|PCM_BOUNDARY|audtask-abi' \
  lib/N64ModernRuntime/librecomp/src lib/N64ModernRuntime/ultramodern/src src
```

After the single batched instrumentation change, export any submodule patch,
build once, and run the already-qualified image recipe from the build
directory. Preserve the full log and use phase-gated frame keys; do not use a
stopwatch as a phase substitute:

```sh
./submodule-patches/export.sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_POSTWAIT=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  PROBE_PHASE_WIDTH=640 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='6:start 11:start 16:start 21:start 24:a 25:start 26:a 27:start 29:a' \
  zsh tools/probe.sh scratch/agent/s2063_audio_image_join 180 0.6 \
  > scratch/agent/s2063_audio_image_join_launcher.log 2>&1
```

Read the resulting run with `rg`, never `cat`; require both target VIs,
`[audtask-dispatch]`, `[pad-host]`, and the joined task/PCM rows before
selecting a hypothesis. If a run fails the controls, fix the runner or
instrument and rerun it in this iteration. ORIGIN: s2062 changed no port
behavior; this unit is attribution of already-observed image writes only.
