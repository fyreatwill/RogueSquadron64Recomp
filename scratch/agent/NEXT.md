# NEXT work unit (s1988) — drain-path dump of fade +0x58 working timer

HYPOTHESIS-ID: hangar-frame-freeze

## What s1987 settled

Hangar `sh` to slot+0x30 during drain is only `beginVoiceFadeRelease`
val=`0x14` (narmed=135611, nlt14=0). Render 90570 n=0; render 90688
nhangar=0; ADSR narmed=0 val=`0xDBDA` pre-drain only. H-no-decrement
SELECTED; H-dec-then-rewrite REFUTED. Fade then copies +0x30 into
slot+0x58 (`0x800924E4`) after `+0x6C=3`.

## Competing hypotheses (why slot+0 stays 0x02)

- **H-working-timer-is-0x58:** +0x30 is the reload; +0x58 counts
  `0x14`→0 on loopers while drain-path `h30` stays `0x14`.
- **H-envelope-fields-stuck:** +0x58 / +0x60 / +0x64 / +0x68 stay
  at the fade-written values through 10M (envelope never ticks).
- **H-b6c-skips-tick:** +0x6C=3 takes a render path that never
  updates those fields; equivalent to H-envelope-fields-stuck
  unless a +0x58 write exists from a skipped site.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1987 `[h30-sum]`/`[h30-uniq]` and s1986 `h30=`/`b6c=`. Add
to each `[drain-path]` idx row: `h58=` (`MEM_HU` +0x58), `w60=` /
`w64=` / `w68=` (`MEM_W`). Dest bound already +0x70. `S32`. No
store changed.

Outcomes (hangar idxs that stay `b=0x02`):
- `h58` drops through `0x13..0` (or any monotone drop) while
  `h30=0x0014` → H-working-timer-is-0x58
- `h58=0x0014` and w60/w64/w68 frozen on every sample →
  H-envelope-fields-stuck (H-b6c-skips-tick still open as why)
- `h58` jumps (not a countdown) → neither; log unique h58 and
  redesign

Positive control: `[drain-path] call=1 unmap=0` 18 idx rows with
`h58=` at iters=1 (expect `h58=0x0014` matching the fade copy);
`[drain-stop-sum] entry=1` fade n>=154; last alloc tickn=4
`0x801714D0 count=18`; `[h30-sum]` fade narmed>0; `[drain-timeout]`
10M. Keep `ROGUESQ_SPIN_YIELD=1` and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Incremental `apply_s1988_drain_h58` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Extend the s1986 `[drain-path]` idx-row dump in `funcs_30.c`.

## Exact test

```sh
mkdir -p scratch/agent/s1988_drain_h58
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1988_drain_h58 60 2
```
