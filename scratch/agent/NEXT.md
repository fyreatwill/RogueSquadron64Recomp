# NEXT work unit (s1983) — classify desc+0x14 / slot+0x40

HYPOTHESIS-ID: hangar-frame-freeze

## What s1982 settled

`musyxInitVoiceFromSample` `sw $v0, 0x40($a0)` at `0x80092230` writes
the live `slot+0x40` (`last_init==w40` on all 18 idxs, `ninit` 1..22,
all `armed=0`). `musyxKeyOnVoice` `0x80090B68`/`0x80090C28` write a
different ~0x50-stride structure (`nsw=nsh=0` on idxs 0–17,
`keyon_unmap` 18366→20372). H-later-overwrite SELECTED; H-keyon-sw /
H-keyon-sh / H-stale-word REFUTED.

Static neighbors in the same init: `desc+0x0C` → slot+0x38 (end
cursor / `mem38`), `desc+0x10` → slot+0x3C, `desc+0x14` → slot+0x40,
`desc+0x18` byte → slot+0x6D.

## Competing hypotheses (what desc+0x14 is)

- **H-loop-flag:** `desc+0x14` is a loop/stream extra-data flag or
  pointer. Nonzero means "do not use the one-shot cursor"; those
  voices need `stopVoice`/`deactivateVoice` (currently 0 / boot-array
  only). Ended idxs have `desc+0x14==0` as one-shots.
- **H-rate-as-flag:** `desc+0x14` is a pitch/rate/length scalar
  (live values `0x092E..0x9241` fit 16-bit rates, not KSEG0
  pointers). Render's `bnez slot+0x40` then skips the end-compare
  for almost every sample; only the few inits that wrote 0 can end.
- **H-start-end-triplet:** `+0x0C/+0x10/+0x14` are a start/end/loop
  sample-offset triplet; `+0x14` is a loop point that is supposed to
  be consumed/cleared during playback and is not.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1982 `[keyon-w40]` / `[drain-path]`. On every mapped init store
(`idx<32`, dest on the current `-0x6908` table) dump:

`[init-desc] idx=N dest=0x.. desc=0x.. d00=0x.. d04=0x.. d08=0x.. d0c=0x.. d10=0x.. d14=0x.. d18=0x.. after=0x..`

Use `S32(guest_addr)` for every `MEM_*`. First 8 always (positive
control); then every mapped init with `idx<18` (ninit is ~250, fine).

Join last `[init-desc]` per idx with drain-path `last_init`/`w40`/
ended-vs-live.

Outcomes:
- ended `d14==0` and live `d14` is a KSEG0 pointer (or a 0/1 flag
  with pointer neighbors) → H-loop-flag
- ended `d14==0` and live `d14` is a small scalar in the same band
  as `d0c`/`d10` (or as pitch/rate copies elsewhere in init) →
  H-rate-as-flag
- `d0c`/`d10`/`d14` look like start/end/loop offsets and live `d14`
  is never cleared during drain (`ninitd=0` already) →
  H-start-end-triplet

Positive control: `[keyon-w40] site=init` fires, at least one
`[init-desc]` line, `[drain-path] call=1 unmap=0`, last alloc
`0x801714D0 count=18`, ended idxs `w40==last_init==0`. Keep
`ROGUESQ_SPIN_YIELD=1` and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Descriptor dump in `RecompiledFuncs/funcs_24.c` at the s1982
  `site=init` block (after the store, dest already computed).
- Incremental `apply_s1983_init_desc` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.

## Exact test

```sh
mkdir -p scratch/agent/s1983_init_desc
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1983_init_desc 60 2
```
