# NEXT work unit (s2156) — A1 host canary-effect census

HYPOTHESIS-ID: m5-image-canary-host-effect

## Work unit

s2155 selected `H-CanaryOnlyInUcodeData`: mix occupies `0xE50..0xFCF`
continuously, the `0xF7F..0xFC0` gap has no unused byte, and leftover
`>=0x10` holes sit only in ucode-data. A relocated host canary has
nowhere to live in DMEM. Do not move the canary, change canary prefill,
default the image arm, or change `osAiGetStatus_recomp` /
`osAiSetNextBuffer_recomp`.

The remaining A1 question is whether `canary_ok=0` (now expected mix)
changes host task completion, writeback, or DMA, or is log-only.
Next unit is one host-only table of every `canary_ok` / `audio_canary_*`
consumer in `lib/N64ModernRuntime/librecomp/src/rsp.cpp` (and any
direct reader of the probe field). No port build, game run, canary
move, task-exit mapping, default-arm, or output-route change.

Reuse s2154/s2155 same-file image controls only as citations: this
unit's positive control is a named host site that *assigns*
`canary_ok` from the `0xF80` pre/post hash, plus a named site that
*reads* it.

## Competing hypotheses and discriminator

- `H-CanaryLogOnly`: every `canary_ok` read is a fprintf / probe-row
  field; exit reason, DMA writeback, and task completion do not branch
  on it.
- `H-CanaryGatesExit`: a `canary_ok==0` path changes `RspExitReason`
  or returns early from `run_task`.
- `H-CanaryGatesWriteback`: a `canary_ok==0` path skips DMEM-to-RDRAM
  writeback or audio DMA recording.
- `H-CoverageFailure`: the assignment site at the `0xF80` pre/post
  hash is missing, or a `canary_ok` read exists outside the table.

The discriminator is one table: every assignment and every read of
`canary_ok` / `audio_canary_post` / `audio_canary_pre`, with
"log/probe field" versus "control-flow/writeback" classified per
site. Log-only selects `H-CanaryLogOnly`; an exit-reason or early
return branch selects `H-CanaryGatesExit`; a skipped DMA/writeback
branch selects `H-CanaryGatesWriteback`; missing assignment or an
unclassified read selects `H-CoverageFailure`. Do not treat prior
`canary_ok=0` rows as this table.

## Exact commands

    python3 - <<'PY'
    from pathlib import Path
    p = Path('lib/N64ModernRuntime/librecomp/src/rsp.cpp')
    text = p.read_text()
    print('bytes', p.stat().st_size)
    print('canary_ok assigns', text.count('canary_ok'))
    print('audio_canary_offset', 'audio_canary_offset' in text)
    PY

Grep `canary_ok`, `audio_canary_pre`, `audio_canary_post`,
`audio_canary_offset`, and `ROGUESQ_AUDIO_CANARY_AB`. Classify each
hit. Write `scratch/agent/s2156_canary_host_effect.txt`.

Do not edit `rsp.cpp` canary prefill, `osAiSetNextBuffer_recomp`, or
the default audio arm.
