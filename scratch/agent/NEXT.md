# NEXT work unit (s1982) — which musyxKeyOnVoice store writes nonzero slot+0x40

HYPOTHESIS-ID: hangar-frame-freeze

## What s1981 settled

The 12 still-live `0x02` idxs skip `L_80090150` because `slot+0x40 != 0`
(`skip084=155` matching 155 `slot-sb new=0x02`, `to_cur=0`). Ended
idxs 5/10/11/12 have `w40==0`, `skip084=0`, `to_cur==vis>0`. After
skipping 084 they split `L_80090188` vs `0x800900B8` on `$a2 < $a0+$s4`;
that split is not why they miss the cursor. H-slot40-skip SELECTED;
H-loop-wrap / H-a2-gate / H-idx-unmapped REFUTED.

Static: `musyxKeyOnVoice` stores slot+0x40 twice — `sw` from sample+0x40
at `0x80090B68`, then `sh` from sample+0x44 at `0x80090C28`.

## Competing hypotheses (who writes nonzero w40)

- **H-keyon-sw:** `0x80090B68` copies a nonzero sample+0x40 word onto
  the 12; ended get 0 from the same store. The later `sh` does not
  change the live/ended split.
- **H-keyon-sh:** `0x80090C28` halfword from sample+0x44 is the nonzero
  that the 12 keep; the earlier `sw` is 0 or is overwritten. Ended
  get 0 from this `sh`.
- **H-later-overwrite:** both key-on stores write 0 (or the same value
  on live and ended); a later store (other `sw`/`sh` of slot+0x40)
  writes the live nonzero after key-on.
- **H-stale-word:** neither key-on store hits the 12 during this drain
  window; the nonzero is leftover from a previous table occupant.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1981 `[drain-path]`. On every `musyxKeyOnVoice` slot+0x40 store
(`0x80090B68` sw, `0x80090C28` sh) log:

`[keyon-w40] site=sw|sh idx=N dest=0x.. src=0x.. val=0x..`

plus any other voice-family `MEM_W/MEM_H(0x40, slot)` store found by
grep of `musyx*` in funcs_24.c. Count per idx since drain-cross armed.

On the same drain-tick samples, dump last keyon sw/sh val per idx next
to live `w40`.

Outcomes:
- 12 have last sw val == live w40, sh does not change it; ended sw=0
  → H-keyon-sw
- 12 have last sh val == live w40 (low 16 bits); ended sh=0 → H-keyon-sh
- both key-on vals 0 (or equal live/ended) and a later site writes the
  nonzero → H-later-overwrite
- zero key-on stores to the 12 after the last alloc of `0x801714D0`
  → H-stale-word

Positive control: `[drain-tick]`/`[drain-path] call=1 iters=1 unmap=0`,
boot `[avf-gate] site=slot-alloc 0x8018D4A0 count=16`, ended idxs
`to_cur>0` `w40==0`, and at least one `[keyon-w40]` line must fire
(mark-everything: log the first 8 stores regardless of dest). Keep
`ROGUESQ_SPIN_YIELD=1` and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Store logs in `RecompiledFuncs/funcs_24.c` at `0x80090B68` /
  `0x80090C28` (and any other musyx slot+0x40 stores the grep adds).
- Incremental `apply_s1982_keyon_w40` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Last-sw/sh fields on `[drain-path]` in `funcs_30.c` if cheap; otherwise
  the per-store log plus a drain-tick join on idx is enough.

## Exact test

```sh
mkdir -p scratch/agent/s1982_keyon_w40
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1982_keyon_w40 60 2
```
