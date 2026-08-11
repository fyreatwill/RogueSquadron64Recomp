# NEXT work unit

HYPOTHESIS-ID: cimg-origin-desync

## Single work unit

**Garbage-prev wild SETCIMG drop** at decode site (processRDPLists /
setColorImage), env-gated, then A/B freelist restore OFF.

Do **not** productize or re-tune `ROGUESQ_DROP_WRAP_RDP` (s664 Outcome B:
task-lo∈sticky is fatally coarse). Keep it default OFF.

## Hypotheses

| ID | Claim | Killed if |
|----|-------|-----------|
| H-prev-garbage-kills-killer | Dropping wild SETCIMG when prev ring is garbage (zeros / op 0x3F / non-allowlist) zeroes exact KILLER + freelist-shaped to_zero with restore OFF | Filter ON still sees KILLER or freelist 0x2/0x60→0 |
| H-prev-garbage-false-drop | Same rule drops legitimate wild-looking but needed SETCIMGs (hangar black, content frames collapse, OK dies) | Filter ON: hangar content dies or OK posctrl dies |
| H-prev-window-too-short | Only prev-1/2 is insufficient (need deeper non-monotonic chain like s663's prev-8..prev-1 zeros) | Single-prev rule misses KILLER; multi-prev catches it |

## Discriminating measurements (batch in ONE build)

1. Land env-gated filter (suggest `ROGUESQ_DROP_GARBAGE_CIMG=1`, default OFF)
   at the site that already has `ROGUESQ_LOG_CIMG_RAW` prev-ring (rt64
   interpreter processRDPLists and/or setColorImage_filtered):
   - if op is SETCIMG (0x3F) AND width not in allowlist {320,512,640,1024}
   - AND prev-command pattern is garbage (e.g. ≥2 of last 4 prev ops are
     0x00 with zero payload, OR prev is op 0x3F with wild width, OR prev
     is nonsense op not in F5 RDP table)
   - then skip applying the SETCIMG (log `[cimg-garbage-drop]`) and do
     not update color image state.
2. Same binary, arms (sequential OK if Metal contends):
   - **A:** drop ON + product restore ON
   - **B:** drop ON + `ROGUESQ_FL_HDR_RESTORE=0`
   - **C:** drop OFF + restore OFF (expect KILLER + freelist to_zero)

Instruments (all free): `ROGUESQ_LOG_CIMG_RAW=1 ROGUESQ_LOG_CIMG=1
ROGUESQ_LOG_FL_ZERO_WATCH=1` + force6/inject hangar path (s662 recipe).

Watch:
- `[cimg-raw] KILLER` → 0 on drop ON
- freelist-shaped to_zero `0x2/0x60→0` after arm_fl with restore OFF
- `[cimg-raw] OK` early boot (posctrl — null filter worthless without OK)
- hangar wilds may drop (good if they are garbage) but hangar must still
  *render* (PNGs / content frames)
- `[cimg-garbage-drop]` fires near historical killer window (posctrl LIVE)
- cinematic must survive (s664 coarse filter failed here)

## Outcomes

- **A)** drop ON: KILLER=0, freelist to_zero freelist-shaped=0 with restore
  OFF, OK LIVE, hangar still renders → productize drop (default ON?) and
  start retiring freelist restore layers.
- **B)** drop ON kills KILLER but also hangar/cinematic → tighten prev
  heuristic or require in_wrap=1 AND garbage-prev.
- **C)** drop ON still sees KILLER → prev window too short / wrong site;
  deepen prev-ring check using s663 dump shape.

## ORIGIN (settled s663 — cite when landing filter)

```
ORIGIN: freelist stomp host writer = RT64 copyNativeToRAM color writeback of
SETCIMG addr=0x1F0D74 w=1161 (covers freelist phys 0x1F3CC0). Operands are
NOT legitimate — length-respecting RDP walk over just-wrapped DPC ring
(in_wrap=1, prev zeros/op 0x3F). Game never uses w=1161. s664 proved
submit_lo∈sticky is too coarse (false-drops legitimate ring reuse).
Decode-site garbage-prev drop targets the bad SETCIMG only.
```

## Standing rules

- Editing `lib/rt64` requires `./submodule-patches/export.sh` + commit same
  session. `src/rsp/dpc_bridge.cpp` needs no export.
- Kill with SIGKILL; run from build/ with ROM.
- One work unit = land garbage-prev drop + A/B/C this iteration.
- Recipe scaffold: `scratch/agent/s664_drop_wrap_rdp_ab.sh` (adapt EXTRA).
