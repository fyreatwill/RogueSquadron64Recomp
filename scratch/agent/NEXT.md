# NEXT work unit (s1029)

HYPOTHESIS-ID: m3-slot-sp-corruption

RESUME instruction — s1028 was a checkpoint close-out (ground-truth
verification + ledger repair), not a new run. Nothing changed in code this
session; the queued soak from s1027/pre-checkpoint is still pending.

## What is confirmed (do not re-verify)

- `ROGUESQ_LOG_SLOT_SP_GUARD` is genuinely landed: fixup patch at
  `N64Recomp/fixup_game_funcs.py:25156-25185` (s1005), present in generated
  `N64Recomp/RecompiledFuncs/funcs_8.c:34593` and in the compiled
  `build/RogueSquadron64Recomp` binary's strings. It dumps `sp`/`ra`/`a0`-`a1`/
  `s0`-`s7`/`fp`/`gp` when `ctx->r29` is outside `[0x80000000, 0x80800000)` at
  the `slotDispatcherIter` prologue spill (`0x8003E8DC`).
- That guard already ran once, pre-M4-detour: `SOAK-RESULTS.md`
  `20260814-013347` (s1009) — forced-LLE recipe (`ROGUESQ_LLE_FORCE=1
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1`), 57
  frames, crashed at `slotDispatcherIter+8592` — NOT the recurring `+872`
  prologue-spill site — with zero guard hits. Valid null, but UNEVALUABLE for
  `+872` because that run never reached it.
- `scratch/agent/soak_queue/s1028_slot_sp_guard.sh` is already queued (commit
  84095402) and is NOT a duplicate of the s1009 run: it drops the forced-LLE/
  stub flags (ordinary dispatch instead of forced/solo LLE), swaps
  `SLOT_DISPATCH`/`VTX_*`/`F5_STATE`/`SHADE_RAW` logging for
  `INPUT`/`DPC`/`THREADS`/`INIT`, and extends the key schedule to 10 events
  through frame 250 (vs 7 through 160). It has not run yet.

## Work unit

Let the loop consume `s1028_slot_sp_guard.sh` (it runs automatically between
iterations, up to 2 recipes, 600s cap). At the next iteration:

1. Read `scratch/agent/SOAK-RESULTS.md` tail for the `s1028_slot_sp_guard`
   verdict line(s).
2. If a `[slot-sp-guard] INVALID ...` record appears: classify it. Cross-
   reference the dumped `ra` against the 144 direct `slotDispatcherIter`
   call sites to identify the caller boundary. A dump whose caller/return
   path already carries the wild `$sp` selects `H-slot-caller-corrupts-sp`;
   a dump with a valid caller boundary but invalid entry state selects
   `H-slot-entry-or-runtime-corrupts-sp`.
3. If the run reaches `+872` (or any slot-dispatch-family crash) with zero
   guard hits, that is a real evaluable null this time (unlike s1009) — record
   it and decide whether a further recipe variant is needed or whether to
   pivot off this hypothesis.
4. If the run does not reach VI-1024-equivalent phase gating or the `+872`
   family at all (e.g., dies elsewhere, times out at an earlier phase), that
   is `H-no-sp-event` / unevaluable reachability — do not treat it as
   evidence for either corruption model. Do not requeue verbatim; adjust the
   recipe (key schedule, LLE flags) based on where it actually died.

Do not re-run the M4 accumulator probe (three controlled nulls already
recorded, s1025-s1027) unless a genuinely new discriminator is identified.

If the soak has NOT yet produced a `SOAK-RESULTS.md` line for
`s1028_slot_sp_guard` by iteration start (loop hasn't reached it), that is
itself fine to wait on — do not manually run it inline; the soak-queue
contract owns repeat/queued recipes, not the interactive session.
