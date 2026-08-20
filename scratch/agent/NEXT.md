# NEXT work unit (s1980) — why 12 live 0x02 slots never cursor-cross

HYPOTHESIS-ID: hangar-frame-freeze

## What s1979 settled

Of 18 slots at `0x801714D0` (last alloc count=18, ch=18), drain
call=1 sees 16 live `0x02`. Only idxs 9, 12, 11, 10 (in that order)
cursor-cross once; each lands `slot-sb new=0x00` and stays idle.
The other 12 (0–4, 6, 7, 13–17) stay `0x02` with `cross_n=0` through
the 10M timeout and take 162 further `new=0x02` stores each.
idx 5 and 8 are already idle. H-end-zero-lost / H-rekey-after-end /
H-zero-unlogged REFUTED; H-subset-live SELECTED.

The four that ended had `cur` in {0x453C, 0x7601}, `pos` just below,
`step` 0x6F–0xA3. The 12 never-cross idxs produced no cursor log
after drain (site rate-limit: first 8 globally + every 1M + cross).

## Competing hypotheses (why those 12 never reach end)

- **H-frozen-pos:** `pos`/`step` do not advance (step=0, or in-loop
  tick does not update these voices' positions).
- **H-huge-end:** `cur` is 0 or far above `pos+step*remaining`; they
  would finish only after many more ticks.
- **H-looping:** `pos` wraps or restarts before `cur`; `sltu` stays
  true forever.
- **H-not-at-cursor:** these dests take `slot-sb` but skip the
  `L_80090150` cursor compare (different render path). Unlikely —
  `slot-sb` is after that compare in the same function — but dump
  per-idx cursor-visit count to close it.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep s1979 `[drain-cross]`. At the cursor site, always record last
`cur`/`pos`/`step` and a visit counter per idx (no rate-limit on the
record). On the same drain-tick samples, dump `[drain-cursor]` for
all 18 idxs: `idx=N vis=V cur= pos= step= dpos=` where `dpos` is
`pos - pos_at_previous_sample` (0 on first sample).

Also dump slot+0x38 via `MEM_W(0, S32(base+i*0x88+0x38))` as a
second source for `cur`.

Outcomes:
- `vis=0` on a live `0x02` idx → H-not-at-cursor
- `vis>0` and `step=0` or `dpos=0` throughout → H-frozen-pos
- `vis>0`, `dpos>0`, `pos+step < cur` and `cur` is huge / 0 → H-huge-end
- `vis>0` and `dpos<0` or `pos` wraps while `cur` fixed → H-looping
- `vis>0`, `dpos>0`, `cur` similar to the ended idxs (~0x7601) and
  `pos` still well below → still H-huge-end (they are just slow);
  compare `pos` vs the 4 ended idxs' start to see remaining distance

Positive control: `[drain-tick]`/`[drain-cross] call=1 iters=1
gate=0x01`, plus `[avf-gate] site=slot-alloc` `0x8018D4A0 count=16`
before drain. The four ended idxs must show `vis>0`, `dpos>0`, and
a last sample with `pos+step >= cur`. Keep `ROGUESQ_SPIN_YIELD=1`
and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Cursor site in `RecompiledFuncs/funcs_24.c` / `_cur_new` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
  (record last cur/pos/step/vis per idx).
- `[drain-cursor]` dump next to `[drain-cross]` in `funcs_30.c` /
  `apply_s1979_drain_cross`.

## Exact test

```sh
mkdir -p scratch/agent/s1980_drain_cursor
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1980_drain_cursor 60 2
```
