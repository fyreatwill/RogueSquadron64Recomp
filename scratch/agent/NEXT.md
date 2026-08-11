# NEXT work unit

HYPOTHESIS-ID: cimg-origin-desync

## Single work unit

**Productize `ROGUESQ_DROP_GARBAGE_CIMG` default ON** and scored freeroll
with freelist restore OFF (start retiring restore layers).

s665 landed the filter env-gated OFF and proved Outcome A (B v2: exact
killer + freelist-shaped to_zero = 0 with restore OFF; C control still
stomps). Hangar content LIVE both arms.

## Hypotheses

| ID | Claim | Killed if |
|----|-------|-----------|
| H-product-drop-safe | Default-ON drop preserves hangar/cinematic/title content and OK posctrl | Default ON: content dies, OK dies, or crash rate >> control |
| H-restore-redundant | With product drop ON, `FL_HDR_RESTORE=0` freeroll still has freelist-shaped to_zero=0 and recov/thr11d rate ≥ historical product-restore baseline | Restore OFF + drop ON: freelist to_zero returns OR recov drought vs restore ON |
| H-skip-fl-redundant | `SKIP_FL_HDR` no longer needed once drop is product ON | Allow FL_HDR writeback under drop ON still sees freelist stomp |

## Discriminating measurements (batch in ONE build)

1. Flip `ROGUESQ_DROP_GARBAGE_CIMG` default to ON (or always-on product path
   with `ROGUESQ_ALLOW_GARBAGE_CIMG=1` opt-out — prefer opt-out shape like
   other product guards).
2. Same binary freeroll arms (force6+inject hangar path, HOLD≥210):
   - **A:** product drop ON + product restore ON (baseline)
   - **B:** product drop ON + `ROGUESQ_FL_HDR_RESTORE=0`
   - **C:** product drop ON + restore OFF + `ROGUESQ_ALLOW_FL_HDR=1` (if
     SKIP_FL_HDR still exists as separate gate)
3. Watch: exact 1F0D74 / freelist to_zero / recov768 / thr11d_new /
   fail136c / craft_stable content / OK posctrl / crash class.

## Outcomes

- **A)** B matches A on freelist+pipeline scores → start retiring restore
  (mode=headers default OFF or hard-skip path).
- **B)** B freelist survives but recov drought → restore still co-gates
  recovery for non-cimg reasons; keep restore, productize drop only.
- **C)** B freelist stomp returns → drop heuristic incomplete; do not
  retire restore; deepen filter.

## ORIGIN (cite when productizing)

```
ORIGIN: freelist stomp host writer = RT64 copyNativeToRAM color writeback of
SETCIMG addr=0x1F0D74 w=1161 (covers freelist phys 0x1F3CC0). Operands are
NOT legitimate — length-respecting RDP walk over just-wrapped DPC ring.
s665 DROP_GARBAGE_CIMG at processRDPLists stops apply of wild+garbage
SETCIMG; B v2 restore OFF confirmed freelist-shaped to_zero=0.
```

## Standing rules

- Editing `lib/rt64` → `./submodule-patches/export.sh` + commit same session.
- Kill with SIGKILL; run from build/ with ROM.
- Recipe scaffold: `scratch/agent/s665_drop_garbage_cimg_ab.sh`.
