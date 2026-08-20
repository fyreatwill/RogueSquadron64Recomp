# NEXT work unit (s1979) — why live 0x02 slots never all idle

HYPOTHESIS-ID: hangar-frame-freeze

## What s1978 settled

`0x801714D0` is a live voice table. Last `slot-alloc` is `count=18`
matching `ch=18` (boot `0x8018D4A0 count=16` is tickn=2). Same-run
`musyxRenderVoiceSamples` slot-sb writes `0x02` (16967) and
`isAudioSlotActive` slot-byte reads `0x02` (135/184). H-ascii-heap /
H-count-desync / H-never-keyed REFUTED; H-voice-records SELECTED.
s1977 ASCII leftover was `MEM_BU` with a 32-bit unsigned KSEG0 address
(zero-extends; host read at rdram+4GiB). Always `S32(guest_addr)`.
Positive controls: `[drain-tick] call=1 iters=1 gate=0x01` and
`[avf-gate] site=slot-alloc` boot `0x8018D4A0 count=16`.

11 `render-end` (cursor cross=1) fire at this base; `deactivateVoice`
is 0 globally; `stopVoice` only hits the boot array. Drain OR of 18
slots never goes idle.

## Competing hypotheses (why the OR stays busy)

- **H-subset-live:** only some idxs ever cursor-cross; the rest never
  reach end (looping / frozen pos). One live `0x02` keeps the drain.
- **H-end-zero-lost:** render-end writes `0` to `0x28($sp)` but the
  later `sb $v0, 0($s1)` still stores `2` (`0x28($sp)` overwritten).
- **H-rekey-after-end:** ended idxs get `2` again next tick via
  render-stage's default `addiu $v0, 0x2` and then do not cross.
- **H-zero-unlogged:** slot-sb DID store `0`; the rate-limit (first 32
  / every 1000 / `new==2`) dropped those events. Equivalent to
  H-subset-live if other idxs stay `2`.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1978 `[drain-tick]` sampling (first 8 + every 100k). On those
samples, dump all 18 slot byte+0 via `MEM_BU(0, S32(base+i*0x88))`
(`[drain-slots]` already walks them; the S32 fix is in the source).
Also:

1. Always log `slot-sb` when `newb==0` (add `|| newb == 0` next to
   `newb == 2` in `musyxRenderVoiceSamples` only).
2. On the same drain-tick samples, print per-idx `cross_n` accumulated
   since drain call=1 (`[drain-cross]`).

Outcomes:
- some idxs have `cross_n=0` and byte=`0x02` through timeout → H-subset-live
- render-end fires and slot-sb `new=0x00` is 0 at that dest → H-end-zero-lost
- render-end then next slot-sb at that dest is `new=0x02` with later
  `cross=0` → H-rekey-after-end
- slot-sb `new=0x00` exists and the 18-byte vector still has `0x02` →
  H-zero-unlogged / H-subset-live

Positive control: `[drain-tick] call=1 iters=1 gate=0x01`, plus at
least one `[avf-gate] site=slot-alloc` `0x8018D4A0 count=16` before
drain. Keep `ROGUESQ_SPIN_YIELD=1` and `ROGUESQ_LOG_VI_CALLERS=1`.

## Exact patch sites

- `apply_s1976_drain_tick` / `[drain-slots]` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
  and `RecompiledFuncs/funcs_30.c` (S32 already applied — add
  `[drain-cross]` only).
- `musyxRenderVoiceSamples` slot-sb rate-limit in `funcs_24.c` /
  `_s1927_slot_sb` (the `newb == 2` condition).

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact test

```sh
mkdir -p scratch/agent/s1979_drain_cross
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1979_drain_cross 60 2
```
