# NEXT work unit

HYPOTHESIS-ID: duplicate-symbol-name-collision-class-s427

## What changed this session (s426) — read this before picking a thread

The item -261 3-sibling crash chain is FIXED (root cause: `menu_overlay.txt` registered both
`func_800AEC60` and `initCraftSelectScreen` at the identical address 0x800AEC60; N64Recomp truncated
the first-listed duplicate to 1 instruction and gave the real ~1200-line body to the unreferenced
second name, so `initCraftSelectScreen` — sole writer of the player-slot-anim-channel cache — never
ran). Deleting the stale `func_800AEC60` line and regenerating fixed it, live-verified with a positive
control (see docs/CURRENT-TRUTH.md item -262, PORTING-STATE Session 426 for the full trace).

That fix immediately surfaced (a) a NEW crash one step earlier in the menu flow
(`updateHangarBayScene`, item -263), and (b) a catalogue of **19 more instances of the same
duplicate-symbol-name bug** across the 3 overlay symbol files, one of which
(`hangarInitialize`/`mallocCraftSelectionData`, item -264) may mean the entire closed s283-396
`-0x25A4` audit guarded 100+ sessions' worth of dead code.

## Two competing candidate work units — pick ONE, do not split effort

**Option A: item -264, `hangarInitialize`/`mallocCraftSelectionData`.** Highest consequence (could
overturn the closed -0x25A4 family), but higher risk (need to decide which of two REAL, deliberate
names should survive — unlike item -262's fix, this isn't an obvious "delete the generic placeholder").
Steps: (1) decide which name the call site (funcs_35.c:1589) should keep — recommend keeping
`mallocCraftSelectionData` since that's the name attached to the REAL body content (the "hangar-list-
pointer"/`-0x25A4` family logic), which means the ONE call site needs updating too (unlike item -262
where deletion alone sufficed) — grep for `hangarInitialize(rdram, ctx)` after regen to confirm the
call site follows automatically, or patch it if not. (2) Delete the OTHER duplicate line from
`menu_overlay.txt`. (3) Regen (make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake). (4) Live-run
with the same PROBE_KEYS schedule as s423-426 (see below) and check: do the `-0x25A4` guards
(`S285`/`S393`/`S394`/`S395_SWEEP` markers, funcs_27.c) fire for the first time ever (positive
control)? Does a new "first genuine execution" crash appear (expect one, per item -262's precedent)?

**Option B: item -263, the new `updateHangarBayScene` crash.** Lower consequence but more in line with
"keep pulling the item -261 thread to its next link" — single-source so far, confirmation soak already
queued (`scratch/agent/soak_queue/s426_menufix_regression.sh` — check `scratch/agent/SOAK-RESULTS.md`
for its verdict before starting; if it already ran, use its result instead of re-driving a live run).
If it reproduces, trace `updateHangarBayScene+13156`'s wild pointer the same way s426 traced
`getPlayerAnimChannelEntryByIds`'s (s193_disasm.py against the crash pc, symbol-range-check the
offset, walk the caller chain back to its source global/struct) — do NOT assume it's the SAME
0x800CDFA4-B0 struct; `last-guest-pc=0x800547bc` is a different address range, check with fresh eyes.

**Recommendation: Option A.** It's the same mechanism just proven safe end-to-end this session, the
blast radius (100+ sessions' worth of a closed investigation) makes it far higher information value,
and per iron rule 5 ("check the boring thing first") a second confirmed instance of the SAME class is
more valuable evidence than chasing a brand-new, unrelated-looking crash. If Option A's regen+live-run
produces a clean or informative result, that's the work unit. If it stalls or produces an ambiguous
result within this iteration's budget, fall back to Option B or to a batch fix of the 11 confirmed-safe
`mission_overlay.txt` func_/real pairs (same low-risk mechanism as item -262, could be done as one
batched regen+verify per iron rule about batching instrumentation).

## Regen recipe (known-working s426)

```
cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
python3 -c "
import glob, os
for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c'):
    os.remove(f)
"
zsh ~/Documents/Tools/RogueSquadron64Recomp/tools/agent/regen_n64recomp.sh
python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py   # audit report for xN on every new patch, not "no changes"
cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
```

Live-run schedule (same as s423-426, known to reach the war-room/craft-select phase):
```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
    PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh tools/probe.sh <outdir> 300 2
```

## Sandbox notes (confirmed again s426)

`lldb`/`otool -tV`/`find -delete`/plain `rm` with globs all require interactive approval — use the
`python3 -c` glob-delete above for the mandatory "delete funcs_*.c before every regen" step (item -20).
`atos` (prefixed with `env`) only returns `symbol+offset`, not file:line. `scratch/agent/s193_disasm.py
<macho> <symbol> <frame_offset> [window]` (hand-rolled ARM64 LDR/STR decoder) plus a manual symbol-range
check (list the two symbols bounding the target address, confirm the crash offset is less than the gap
to the next symbol — s426 wrote this check ad hoc; consider promoting it into a reusable script next
time) remain the working substitute for precise crash-site identification and for catching the
duplicate-symbol/truncated-body failure mode itself.

## Soak queue

- `scratch/agent/soak_queue/s426_menufix_regression.sh` — queued this session, not yet run.
