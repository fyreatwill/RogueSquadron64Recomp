# NEXT work unit

HYPOTHESIS-ID: item-346-r6-r3base-gap

## s566 recap (read this first)

**Item -320 FULLY CLOSED 2/2** (s566 fold of `s565_item320_safe_early_exit_confirm`: hangarbay
n=2600, full ~300s rc=0, no +1860/0x800aafb8 crash). Same-run bonus on item -346 1st verify:
`project-model-bounds-guard2` n=0..179 (mini-epilogue actively catches bad args).

**Item -346 FIXED 1/2.** Residual r3-base write at `0x8000D6D0` (both delay-slot copies) guarded
via new `HEAP_FREE_LIST_DEQUEUE_R6_GUARD`. 1st live-verify: hangarbay n=2600, 0 r6 fires, no
0x8000d6d0 crash; died on new breadcrumb item -347.

**Item -347 filed (1 occ):** `transformSceneLights+2456` / `last-guest-pc=0x80010134`. Guest PC
is caller `submitSceneNodeRender` JAL delay-slot (same misattribution pattern as -320); host fault
inside callee +2456. Watch for recurrence.

## This iteration's work unit

1. **Fold** `s566_item346_r6_confirm` from SOAK-RESULTS (if present).
2. If CLEAN (hangarbay double-digit+, no 0x8000d6d0 crash):
   - Mark item -346 **FULLY CLOSED 2/2**.
   - Pivot HYPOTHESIS-ID: prefer any 3rd-hit breadcrumb (-332 etc.) OR a new DIRECT residual
     gap if the confirm's death site is adjacent to an existing guard; otherwise file and pick
     the highest-information systematic next (do not chase -347 on 1 occ).
3. If WEAK (hangarbay n<10 / item-306 early death): discard, re-queue confirm.
4. If 0x8000d6d0 **recurs** under R6: re-open with fault address + whether r6 fired same-run
   (wrong reg / incomplete cover).

### Exact commands (after fold closes -346)
```bash
# Only if a new DIRECT gap appears, or a 3rd-hit breadcrumb escalates.
# Otherwise re-tally SOAK-RESULTS breadcrumb occ counts and pick next class.
grep -cE '0x8001086c|0x8000d688|0x8000d698|0x80010134' scratch/agent/SOAK-RESULTS.md
```

### Do NOT
- Re-open freelist WRITE packing DEFERRED / campaign CLOSED items -341..-345.
- Treat last-guest-pc on a JAL delay-slot as the faulting insn inside the callee (s565/s566).
- Early-guard `goto` full epilogue unless every callee-save the epilogue restores is spilled.
- Chase item -347 on a single occurrence.

## Iron-rule reminders
- Confirm free session number at START (next is s567).
- Weak early deaths on item -306: discard+retry.
- Kill with SIGKILL; run from build/ with ROM.
