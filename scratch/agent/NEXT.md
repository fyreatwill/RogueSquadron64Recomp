# NEXT work unit

HYPOTHESIS-ID: item-320-loadcutscene-sourcetrace

## s565 recap (read this first)

**Item -320 ROOT-CAUSED AND FIXED 1/2.**

- Guest `0x800AAFB8` = caller delay-slot nop (not the faulting insn). Host `+1860` =
  `L_800A92F0` `lw $v0,-0x25A4($s1)` inside `loadCutsceneAssetsByIndex`.
- Root cause: `projectModelBoundsToScreen` guard1/guard2 early-exit `goto L_80066204`
  restored `$s1` from unspilled stack garbage → caller SEGV.
- Fix: safe mini-epilogue in `fixup_game_funcs.py` + `funcs_15.c` (guard1/2 only;
  guard3 still full epilogue).
- 1st live-verify: hangarbay n=2600, 0 project-model-bounds fires, **no +1860 crash**;
  died on new breadcrumb item -346 `0x8000d6d0`.
- 2nd confirm queued: `scratch/agent/soak_queue/s565_item320_safe_early_exit_confirm.sh`
  (loop should run this between iterations).

**Item -346 filed (1 occ):** `heapFreeListDequeue` unguarded `MEM_W(0,r3)` at `0x8000D6D0`
immediately before existing R2 guard at `0x8000D6D4`. Free-list-pop neighbourhood of -331/-333.

## This iteration's work unit

1. **Fold** `s565_item320_safe_early_exit_confirm` from SOAK-RESULTS (if present).
2. If CLEAN (hangarbay double-digit+, no +1860/0x800aafb8 crash):
   - Mark item -320 **FULLY CLOSED 2/2**.
   - Pivot HYPOTHESIS-ID to next work: prefer **item -346 residual r3 write at
     `0x8000D6D0`** (DIRECT gap model, same-session source already mapped) OR any
     3rd-hit breadcrumb from soaks (-332 etc.).
3. If WEAK (hangarbay n<10 / item-306 early death): discard, re-queue confirm.
4. If +1860 **recurs** under the fix: the mini-epilogue theory is incomplete —
   re-open with fault address + whether guard2 fired same-run.

### Exact commands (after fold closes -320)
```bash
# Guard the unguarded r3 write at 0x8000D6D0 (both delay-slot copies), sharing
# a new or existing heaplistdeq env family; land in fixup + surgical funcs_3.c;
# one build; hangarbay double-digit+ live-verify.
grep -n '0x8000D6D0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c
```

### Do NOT
- Re-open freelist WRITE packing DEFERRED / campaign CLOSED items -341..-345.
- Treat last-guest-pc=0x800aafb8 as a site inside loadCutsceneAssetsByIndex body.
- Early-guard `goto` full epilogue unless every callee-save the epilogue restores
  has already been spilled (s565 standing gotcha).

## Iron-rule reminders
- Confirm free session number at START (next is s566).
- Weak early deaths on item -306: discard+retry.
- Kill with SIGKILL; run from build/ with ROM.
