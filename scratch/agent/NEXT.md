# NEXT work unit (s1986) — drain-path fade timer + ADSR state

HYPOTHESIS-ID: hangar-frame-freeze

## What s1985 settled

Remaining stop/release family dest-mapped. tickn=4→drain:
`musyxStartVoiceRelease` 2 hangar (idx 2,5; note key-off via
`tickAudioChannel` / `soundMacroOpKeyOff`), `stopVoiceByKey` 1
dest=`0xFF`, MarkRetrigger 8 retrigger, fade/handle/slot-synced
/`stopVoiceByHandle`/`Locked` 0. At drain start, `stopVoicesByHandle`
8 song handles (`0x17`..`0x11`) each followed by
`beginVoiceFadeRelease` on hangar idxs; static caller is
`stopSongByHandle` `0x8009582C`. Fade then sweeps all 18. Slot+0
stays `0x02` on looping voices through 10M. `ra=0` on every dump:
N64Recomp jal omits `ctx->r31`. H-missing-song-stop REFUTED;
H-song-stop-unmapped SELECTED for the handle; drain starts the
song fade and waits.

## Competing hypotheses (why fade does not idle looping slot+0)

- **H-fade-timer-stuck:** slot+0x30 stays `0x14` (the value fade
  writes) through the 10M timeout — the release envelope never
  counts down, even with in-loop `tickMusyXIfActive`.
- **H-fade-counts-no-zero:** +0x30 counts toward 0 and +0x6C is
  the fade-written ADSR-release state (3), but slot+0 stays
  `0x02` because the loop-length skip never takes the render-end
  zero path.
- **H-fade-zeros-rekey:** slot+0 does hit 0 on faded loopers and
  is re-keyed `0x02` before the next drain-path sample
  (MarkRetrigger retrigger during drain).

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1985 `[stop-dest]` / `[drain-stop-sum]` and existing
`[drain-path]`. Add `h30=` (slot+0x30, `MEM_HU`) and `b6c=`
(slot+0x6C, `MEM_BU`) to the per-idx `[drain-path]` row. Read
with `S32(dest+off)`. No store changed.

Outcomes (compare iters=1 vs last 10M sample, idxs that
`beginVoiceFadeRelease` hit at drain start: 0–17):
- h30 stays `0x14` (or unchanged) on loopers with b=`0x02` →
  H-fade-timer-stuck
- h30 drops, b6c=3, b stays `0x02`, no `slot-sb new=0x00` on
  those idxs → H-fade-counts-no-zero
- drain-path b flickers 0 or `slot-sb new=0x00` then `0x02` on
  a faded looper → H-fade-zeros-rekey

Positive control: `[drain-path] call=1 unmap=0` with 18 idx
rows at iters=1; `[drain-stop-sum] entry=1` fade n>=154 and
`stopVoicesByHandle` n>=23; MarkRetrigger n=1 dest=`0x8018D4A0`;
last alloc tickn=4 `0x801714D0 count=18`. Keep
`ROGUESQ_SPIN_YIELD=1` and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Incremental `apply_s1986_drain_fade` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Extend the per-idx `[drain-path]` fprintf in `funcs_30.c`
  (existing `b=` / `w40=` row).

## Exact test

```sh
mkdir -p scratch/agent/s1986_drain_fade
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1986_drain_fade 60 2
```
