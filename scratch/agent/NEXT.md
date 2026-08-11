# NEXT work unit

HYPOTHESIS-ID: cimg-origin-desync

## Single work unit

**Env-gated wrap-tail RDP submit filter** (−416), then A/B freelist
mitigation OFF to prove stomp elimination without defense layers.

Do not expand freelist restore. Origin is settled (s663 Outcome A).

## Hypotheses

| ID | Claim | Killed if |
|----|-------|-----------|
| H-wrap-filter-kills-killer | Dropping RDP submits whose task address sits in the just-wrapped ring (start..seen sticky) zeroes exact KILLER + freelist-shaped to_zero when restore is OFF | Filter ON + restore OFF still sees KILLER or freelist 0x2/0x60→0 |
| H-wrap-filter-false-drop | The same filter drops legitimate post-wrap work (posctrl OK dies, hangar black, content frames collapse) | Filter ON keeps OK×N, hangar content, only wild/killer vanish |
| H-filter-needs-byte-granularity | Task-address in_wrap is too coarse (whole submit ranges include both garbage and legit) | Filter ON kills hangar wilds but also legitimate SETCIMGs in same task |

## Discriminating measurements (batch in ONE build)

1. Land env-gated filter (suggest `ROGUESQ_DROP_WRAP_RDP=1`, default OFF):
   at `submit_rdp_range` / dpc_bridge live+deferred commit, if submit_lo is
   inside last wrap sticky `[start, seen)` log `[dpc-wrap-drop]` and skip
   submit. Keep wrap sticky updates even when dropping.
2. Same binary, two concurrent arms (or one arm with mid-run toggle if easy):
   - **A:** filter ON + product restore ON (posctrl path)
   - **B:** filter ON + `ROGUESQ_FL_HDR_RESTORE=0` (+ hard-skip if needed)
   - **C (optional control):** filter OFF + restore OFF (expect stomp back)

Arm instruments (all free): `ROGUESQ_LOG_CIMG_RAW=1 ROGUESQ_LOG_CIMG=1
ROGUESQ_LOG_FL_ZERO_WATCH=1` + force6/inject hangar path as s662 recipe.

Watch:
- `[cimg-raw] KILLER` count (must be 0 on filter ON for Outcome A)
- freelist-shaped to_zero `0x2/0x60→0` after arm_fl
- `[cimg-raw] OK` early boot (posctrl — null filter is worthless without OK)
- hangar/title content still present (not black)
- `[dpc-wrap-drop]` fires when wraps happen (posctrl that filter is LIVE)

## Outcomes

- **A)** filter ON: KILLER=0, freelist to_zero freelist-shaped=0 with restore
  OFF, OK LIVE, hangar OK → productize filter (default ON?) and start
  retiring freelist restore layers.
- **B)** filter ON kills KILLER but also OK/hangar → refine to byte-offset
  desync detect or garbage-prev SETCIMG drop only (narrower).
- **C)** filter ON still sees KILLER → in_wrap sticky mismatch at submit
  time; re-check sticky timing vs submit.

## ORIGIN (settled s663 — cite when landing filter)

```
ORIGIN: freelist stomp host writer = RT64 copyNativeToRAM color writeback of
SETCIMG addr=0x1F0D74 w=1161 (covers freelist phys 0x1F3CC0). Operands are
NOT legitimate — length-respecting RDP walk over just-wrapped DPC ring
(in_wrap=1, prev zeros/op 0x3F). Game never uses w=1161. Same class as hangar
wild SETCIMG (s662). Filter targets the wrap-stale submit, not freelist.
```

## Standing rules

- Export submodule patches if editing lib/ or src that is patched via lib/.
  `dpc_bridge.cpp` is under `src/` — no export. If touching `lib/rt64` for
  complementary guards, `./submodule-patches/export.sh` same session.
- Kill with SIGKILL; run from build/ with ROM.
- One work unit = land filter + run A/B comparison this iteration.
