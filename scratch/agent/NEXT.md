# NEXT (s7774)
HYPOTHESIS-ID: ovl-stale-npc-slot
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Unit (one instrument, one build, one run): s7773 closed the overlay fn-pointer class for SILENT divergence, but whether mission NPC
slots (handler set by .text setupNpcUpdateFunctions -> spawnNpcOfType 0x8003FFEC) are cleared before the mission overlay is
swapped out was witnessed only by 2 mission>menu swaps with 0 aborts.
Hypotheses: H-cleared (slot table freed/zeroed on mission exit: 0 live slots with an overlay-window handler at the swap),
H-dormant (live slots keep stale handlers but are never dispatched outside a mission), H-stale (dispatched after swap -> abort;
would show as "Failed to find function" on the abort->hangar route).
Step 1 offline: read spawnNpcOfType (0x8003FFEC) disassembly (`mips64-elf-objdump -d --start-address=0x8003FFEC
--stop-address=0x80040100 -j .text ../rogue_squadron64/build/roguesquadron.elf`) to get the slot array base/stride/handler offset.
Step 2: in load_overlay (overlays.cpp, s7528 pre hook; lib/ edit -> export.sh + commit), when ROGUESQ_S7774_SLOTS=1, before the
eviction count slots whose handler is in [0x800A5130,0x8010B6D0) and whether each is a start in the departing/arriving section;
print `[s7774] swap from=.. to=.. live=.. ovl_handlers=.. start_in_arriving=..`. Positive control: the same scan at mission
start (after setup) must show ovl_handlers>0.
Run: forced level L1 (s5705 recipe) -> fly 60 s -> abort to hangar (G5i route) -> re-enter, once.
Outcome: ovl_handlers=0 at the mission>menu swap -> H-cleared, class fully closed; >0 -> H-dormant/H-stale, then check dispatch.
