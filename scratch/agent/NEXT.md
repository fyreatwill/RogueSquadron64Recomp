# NEXT work unit (s2152) — A13 retail AI-status poll

HYPOTHESIS-ID: m5-ai-status-poll

## Work unit

s2151 closed remaining MORT reference classes (`H-MORTRemainingMatches`).
Do not re-run `mort_probe.py` or pad extra type-1/2 16000-Hz cells.

The next unit is M5 A13: one host-only generated/symbol presence table for
`osAiGetStatus` / `__osAiDeviceBusy` / `osAiSetNextBuffer`, plus one
retail-oracle execution census of `__osAiDeviceBusy` with `osAiSetNextBuffer`
as the same-run positive control. No port build, audio-arm change, task ABI,
output route, host-shortcut edit, guard, or default dispatch change.

## Competing hypotheses and discriminator

- `H-BusyIsThePoll`: retail `__osAiDeviceBusy` (`0x80029F30`) executes on
  the covered title/hangar route in the same run as live `osAiSetNextBuffer`.
- `H-StatusNeverPolled`: `osAiSetNextBuffer` control fires through hangar
  and `__osAiDeviceBusy` stays at zero (busy check inlined or unused).
- `H-GetStatusNamedLive`: the generated tree or TOML contains a named
  `osAiGetStatus` VRAM/caller, so the host `osAiGetStatus_recomp` is a live
  jal target (would contradict the current TOML absence).
- `H-CoverageFailure`: whole-RDRAM control or title/hangar VI gates miss,
  so a zero `__osAiDeviceBusy` count is unevaluable.

The discriminator is one table: TOML/generated presence of the three AI
symbols, same-run whole-RDRAM write control, title `1024` plus hangar
`512 @ 0x006AB400`, `osAiSetNextBuffer` execution count, and
`__osAiDeviceBusy` execution count. Named `osAiGetStatus` presence selects
`H-GetStatusNamedLive`; live busy-plus-set-next selects `H-BusyIsThePoll`;
set-next without busy after those gates selects `H-StatusNeverPolled`;
missing control/gates select `H-CoverageFailure`. Do not treat a silent
`AI_STATUS_REG` MMIO watch as evidence (the oracle's RDRAM breakpoint path
is not a positive control for MMIO).

## Exact commands

    python3 - <<'PY'
    from pathlib import Path
    import re
    roots = [
        Path('syms/rogue_squadron.syms.toml'),
        Path('../N64Recomp/RecompiledFuncs/funcs.h'),
    ]
    names = ('osAiGetStatus', 'osAiGetLength', '__osAiDeviceBusy', 'osAiSetNextBuffer')
    for path in roots:
        text = path.read_text(encoding='utf-8', errors='replace')
        print(f'=== {path} ===')
        for name in names:
            hits = [i+1 for i,line in enumerate(text.splitlines()) if name in line]
            print(f'  {name}: {len(hits)} lines {hits[:8]}')
    PY

    grep -n 'jal 0x80029F30\|jal 0x80029E80\|__osAiDeviceBusy\|osAiGetStatus' \
      ../N64Recomp/RecompiledFuncs/funcs_*.c \
      | head -80

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 70 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x80029E80,0x80029F30 \
      --first-watch 0 --vi-trace \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      > scratch/agent/oracle_s2152_ai_status.log 2>&1

If the first oracle run saturates `--hit-cap` before the PC watches log,
rerun the same command in this iteration with `--detail-watch` on the two
PC watches after the whole-RDRAM threshold, following the s2121/s2134
repair. Do not change `osAiGetStatus_recomp` or default the image arm.
