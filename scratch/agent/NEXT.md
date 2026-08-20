# NEXT work unit (s1987) — dest-map hangar slot+0x30 stores during drain

HYPOTHESIS-ID: hangar-frame-freeze

## What s1986 settled

`h30=`/`b6c=` on `[drain-path]`: every idx 0–17, 108 samples
(iters 1–10M), `h30=0x0014`. `b6c=0x03` except idx 8 (`0x02`).
Loopers 0–4, 6, 7, 13–17 stay `b=0x02`. Dump is after in-loop
`tickMusyXIfActive`. H-fade-timer-stuck SELECTED;
H-fade-counts-no-zero / H-fade-zeros-rekey REFUTED.
`beginVoiceFadeRelease` n 155→181333 during the spin.

## Competing hypotheses (why h30 stays 0x14 after every tick)

- **H-no-decrement:** the only hangar `sh` to slot+0x30 during
  drain is fade/release writing `0x14`. Nothing counts the
  envelope down.
- **H-dec-then-rewrite:** some site writes `h30` in `1..0x13`
  (or 0) and fade then writes `0x14` later in the same
  `tickMusyXIfActive`, so the dump-after-tick still reads `0x14`.
- **H-fade-rearms-only:** fade is re-entered ~18 times per tick
  (already observed as n-growth) and is the last +0x30 writer;
  equivalent to H-no-decrement unless a mid-tick decrement exists.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1986 `[drain-path]` h30/b6c and s1985 `[stop-dest]`. Add a
store census on hangar-mapped `MEM_H` to slot+0x30 (`dest` in
`0x801714D0` + idx*0x88, idx<18) while `s1979_drain_cross_armed`:
site, n, idx, val. Sites (all `sh ?, 0x30($slot)` in funcs_24.c):

- `beginVoiceFadeRelease` `0x800924BC` (known `0x14`)
- `musyxStartVoiceRelease` `0x80092298` (known `0x14`)
- `musyxRenderVoiceSamples` `0x80090570`, `0x80090688`
- `musyxStoreVoiceAdsrParams` `0x80092318`

Log first 8 plus every hangar-mapped store. Summarize unique
(site,val) at `[drain-timeout]`. No store changed.

Outcomes (hangar idxs that stay `b=0x02`):
- only val=`0x14` from fade/release, 0 stores from render/ADSR
  → H-no-decrement (H-fade-rearms-only for the n-growth)
- render/ADSR (or other) val in `0..0x13` then fade `0x14` in
  the same tick → H-dec-then-rewrite
- fade n does not grow / no hangar +0x30 store after entry →
  H-fade-rearms-only REFUTED; timer stuck without rewrite

Positive control: `[drain-path] call=1 unmap=0` 18 idx rows
`h30=0x0014` at iters=1; `[drain-stop-sum] entry=1` fade n>=154;
MarkRetrigger n=1 dest=`0x8018D4A0`; last alloc tickn=4
`0x801714D0 count=18`; at least one `[h30-store] site=beginVoiceFadeRelease
val=0x14` after drain-sum. Keep `ROGUESQ_SPIN_YIELD=1` and
`ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Incremental `apply_s1987_h30_store` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Insert after each of the four `MEM_H(0X30, ...)` sites in
  `funcs_24.c`.

## Exact test

```sh
mkdir -p scratch/agent/s1987_h30_store
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1987_h30_store 60 2
```
