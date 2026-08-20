# NEXT work unit (s1981) — which musyxRenderVoiceSamples branch the 12 take

HYPOTHESIS-ID: hangar-frame-freeze

## What s1980 settled

The 12 still-live `0x02` idxs at `0x801714D0` (0–4, 6, 7, 13–17) have
`vis=0` at `L_80090150` through 108 drain-tick samples. They still
take 155 `musyxRenderVoiceSamples` `slot-sb new=0x02` each on that
table. The four that ended (5/8/10/11) show `vis>0`, `dpos>0`, last
`pos+step >= cur`, `mem38==cur`. H-frozen-pos / H-huge-end /
H-looping REFUTED; H-not-at-cursor SELECTED.

Static: `0x80090084` loads `$a3 = slot+0x40`. Zero goes to the
cursor; nonzero falls through `0x8009008C..B0` and can
`beq L_80090188`, skipping the compare and still reaching the
`sb 0x28($sp)` tail that writes `0x02`.

## Competing hypotheses (which skip)

- **H-slot40-skip:** `slot+0x40 != 0` on the 12, `== 0` on the four
  ended. They take `0x80090084` fallthrough then `0x800900B0` to
  `L_80090188`.
- **H-loop-wrap:** `slot+0x40 != 0` and they take `0x800900B8`
  (`lw 0x3C($s1)` loop-point) instead of `L_80090188` or cursor.
- **H-a2-gate:** `slot+0x40 != 0` but the skip is `$a2 >= $a0+$s4`
  at `0x800900B0`, not the +0x40 flag itself.
- **H-idx-unmapped:** they do execute `L_80090150` but dest does
  not map to drain-table idxs so `vis` stays 0. Unlikely (`n_cur`
  growth matches the four ended) — dump unmapped dests to close it.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1980 `[drain-cursor]`. On the same drain-tick samples, dump
`[drain-path]` for all 18 idxs:

`idx=N b= vis= w40= w3c= b1= to_cur= to_188= to_0b8=`

where `w40`/`w3c`/`b1` are `MEM_W(0, S32(dest+0x40))`,
`MEM_W(0, S32(dest+0x3C))`, `MEM_BU(0, S32(dest+1))`, and the
three counters increment at:

- `to_cur`: each `goto L_80090150` (sites `0x80090084/9C/A4` plus
  fallthrough into the label)
- `to_188`: `goto L_80090188` at `0x800900B0`
- `to_0b8`: fallthrough into `0x800900B8`

Also increment an unmapped-dest counter at the cursor site when
`idx == 0xFFFFFFFF`.

Outcomes:
- 12 have `w40!=0` and `to_188>0` / `to_cur=0`; ended have
  `w40==0` and `to_cur>0` → H-slot40-skip
- 12 have `to_0b8>0` / `to_cur=0` → H-loop-wrap
- 12 have `w40!=0` but `to_188` tracks `$a2` not the flag → H-a2-gate
- unmapped dests ≈ slot-sb count for the 12 → H-idx-unmapped

Positive control: `[drain-tick]`/`[drain-cross]`/`[drain-cursor]
call=1 iters=1 gate=0x01`, boot `[avf-gate] site=slot-alloc
0x8018D4A0 count=16`, and the four ended idxs must show `to_cur>0`
plus last `pos+step >= cur`. Keep `ROGUESQ_SPIN_YIELD=1` and
`ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Branch counters in `RecompiledFuncs/funcs_24.c` at `0x80090084` /
  `9C` / `A4` / `B0` / `B8` and unmapped dest at the cursor site;
  `_cur_new` / new incremental `apply_s1981_drain_path` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- `[drain-path]` dump next to `[drain-cursor]` in `funcs_30.c`.

## Exact test

```sh
mkdir -p scratch/agent/s1981_drain_path
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1981_drain_path 60 2
```
