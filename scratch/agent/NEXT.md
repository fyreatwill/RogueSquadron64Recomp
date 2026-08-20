# NEXT work unit (s1977) — dump leftover drain slot bytes

HYPOTHESIS-ID: hangar-frame-freeze

## What s1976 settled

`anyAudioSlotActive` returns 1 when idle. Drain call=1 at craft-select origin
`0x00656400` spun 10M iters with in-loop `tickMusyXIfActive` (gate=0x01,
positive control `[drain-tick]`). Timeout forced idle; `fs` stayed 1215;
zero `[lle task]` after `[drain-exit]`. H-reap-in-loop / H-tick-skips
REFUTED. H-stuck-slot SELECTED. Force-idle is not a fix.

s1975 "drain #17" was slot-ret-caller n, not a 17th function call.

## Competing hypotheses (why bytes stay nonzero)

- **H-one-zombie:** one idx keeps a nonzero slot byte; others are 0.
- **H-all-stuck:** every live idx has a nonzero byte.
- **H-chCount-wild:** `MEM_BU(0x80141AD0)` is huge / non-sane, so the walk
  reads OOB bytes that look active (`isAudioSlotActive` guards the base
  pointer, not dest+idx).
- **H-tick-rekeys:** some bytes go 0 then become nonzero again after the
  in-loop `tickMusyXIfActive` (ticking songs re-keys voices; the extra
  tick is why idle never arrives).

## Discriminating measurement (one instrument, one build, one 120s probe)

Extend the existing s1976 `[drain-tick]` block (already first 8 + every
100k of the first 64/every-1000 ticks). On each of those samples log:

- `chCount` = `MEM_BU(0x1AD0, 0x80140000)`
- for idx in `0 .. min(chCount, 32)-1`: slot byte at
  `base + idx*0x88` where `base = MEM_W(-0x6908, 0x80150000)`
  (`isAudioSlotActive` addressing). Print idx+byte for nonzero only,
  plus `nz` count.

Do not add a new run-lifetime counter. Scope to drain call=1 samples
already produced by `[drain-tick]`.

Outcomes:
- one idx always nonzero, others 0 → H-one-zombie
- every idx nonzero → H-all-stuck
- chCount > 32 or dest OOB → H-chCount-wild
- a byte is 0 on one sample and nonzero on the next → H-tick-rekeys

Positive control: `[drain-tick] call=1 iters=1 gate=0x01` still fires
(same path as s1976). Keep `ROGUESQ_SPIN_YIELD=1`. Leave the 10M timeout
in place so the probe still exits the spin.

## Exact patch site

`apply_s1976_drain_tick` in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
and the matching block in `RecompiledFuncs/funcs_30.c` (SENTINEL is
already applied — incremental edit, do not rerun full fixup).

Log tag: `[drain-slots]`.

## Exact test

```sh
mkdir -p scratch/agent/s1977_drain_slots
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1977_drain_slots 60 2
```

60s after hangar is enough: s1976 hit 10M / timeout well before that.
