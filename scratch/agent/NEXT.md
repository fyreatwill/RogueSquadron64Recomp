# NEXT work unit (s2158) — A1 image-arm isolator census

HYPOTHESIS-ID: m5-image-arm-isolators

## Work unit

s2157 selected `H-CanaryLogOnly`: every `canary_ok` site in `rsp.cpp` is
storage or a fprintf/probe field; `run_task` completes on `Broke` alone;
DMA recording ignores the flag. Do not move the canary, change canary
prefill, default the image arm, or change `osAiGetStatus_recomp` /
`osAiSetNextBuffer_recomp`.

The remaining A1 question is what still keeps `factor5_ucode_b` opt-in
now that `canary_ok` is not a host gate. Next unit is one host-only
table of every `ROGUESQ_AUDIO_UCODE` / `musyx_stub` / `factor5_ucode_b`
site in `src/main/main.cpp` and `lib/N64ModernRuntime/librecomp/src/rsp.cpp`
(and any other translation unit that selects the audio ucode). Classify
each hit as dispatch-arm, probe wrapper, log label, or other
control-flow. No port build, game run, default-arm, canary, task-exit,
or output-route change.

Positive control: a named site that *assigns* the live audio ucode
function pointer from `ROGUESQ_AUDIO_UCODE`, plus a named site that
*calls* that pointer (or `musyx_stub` / `factor5_ucode_b` directly).

## Competing hypotheses and discriminator

- `H-IsolatedOnlyByEnv`: the only control-flow isolator is the
  `ROGUESQ_AUDIO_UCODE` branch in `get_rsp_microcode` choosing
  `factor5_ucode_b_probe` vs `musyx_stub_probe`; `run_task` does not
  further branch on the arm.
- `H-IsolatedByRunTask`: `run_task` has a second image-arm branch besides
  calling the already-selected `ucode_func` (early return, skipped
  writeback, or forced `Broke`).
- `H-IsolatedByStubBody`: `musyx_stub` remains reachable on the image
  path (the env-true arm still calls the stub).
- `H-CoverageFailure`: the assignment site that reads
  `ROGUESQ_AUDIO_UCODE` into the live function pointer is missing, or a
  dispatch site is unclassified.

The discriminator is one table: every assignment and every read of
`ROGUESQ_AUDIO_UCODE`, `musyx_stub`, `musyx_stub_probe`,
`factor5_ucode_b`, and `factor5_ucode_b_probe`, classified
dispatch-arm vs probe/log vs other control-flow. Env-only dispatch
selects `H-IsolatedOnlyByEnv`; a `run_task` arm branch selects
`H-IsolatedByRunTask`; image-path stub reachability selects
`H-IsolatedByStubBody`; a missing or unclassified dispatch site
selects `H-CoverageFailure`. Do not treat prior `canary_ok` rows as
this table, and do not default the image arm from the table alone.

## Exact commands

    python3 - <<'PY'
    from pathlib import Path
    files = [
        Path('src/main/main.cpp'),
        Path('lib/N64ModernRuntime/librecomp/src/rsp.cpp'),
    ]
    needles = ['ROGUESQ_AUDIO_UCODE', 'musyx_stub', 'factor5_ucode_b']
    for p in files:
        text = p.read_text()
        print(p, 'bytes', p.stat().st_size)
        for n in needles:
            print(' ', n, text.count(n))
    PY

Grep those needles in `*.c *.cpp *.h *.hpp`. Classify each hit.
Write `scratch/agent/s2158_image_arm_isolators.txt`.

Do not edit `get_rsp_microcode`, `musyx_stub`, `osAiSetNextBuffer_recomp`,
or the default audio arm.
