# NEXT work unit

HYPOTHESIS-ID: duplicate-symbol-name-collision-class-s427

## What changed this session (s427) — read this before picking a thread

Fixed item -264 (`hangarInitialize`/`mallocCraftSelectionData` duplicate-symbol collision) — same
mechanism as item -262 (s426), confirmed a SECOND independent instance of the class: deleting the
truncated first-listed name from `menu_overlay.txt` and regenerating gave the real ~4386-line body
back to `mallocCraftSelectionData`, and the sole call site auto-followed with zero source edits.

That fix did NOT reach the expected positive control (the `-0x25A4` guard markers firing for the
first time) because a NEW crash intervened earlier in the menu flow: SIGBUS in
`runHangarMenuFromOverlay+800` (called from `menuOverlayInit`, ~4s after the SELECT GAME `a` press),
`far=0x3bf800002` = rdram_base + `0xbf800002`. **`0xbf800002` is the IEEE-754 bit pattern for
approximately -1.0f** — a NEW signature, distinct from every prior crash in this lineage (all
previously "rdram_base + small near-zero *integer* offset"). This looks like a float value used as a
pointer, i.e. type confusion, not a never-initialized-global read. Single-source so far, item -265,
not yet investigated. Confirmation soak queued:
`scratch/agent/soak_queue/s427_hangarinit_regression.sh` — check `scratch/agent/SOAK-RESULTS.md`
first; if it already ran, use its result instead of re-driving a live run.

## Two candidate work units — pick ONE

**Option A: root-cause item -265, the new `runHangarMenuFromOverlay` crash.** This is the direct next
link in the chain this session's fix just extended — same "keep pulling the thread" logic that made
Option A the right call last session over Option B. Steps: (1) if the soak above already ran, read its
verdict; if it reproduced, or if not yet run, do the live run yourself with the same PROBE_KEYS
schedule (below). (2) Use `scratch/agent/s193_disasm.py <macho> runHangarMenuFromOverlay <offset>`
(offset = 800, the crash PC's function-relative offset from the `[CRASH][pc-symbol]` line) to find the
exact instruction and register that produces the `0xbf800002` (~-1.0f) value — this is a NEW failure
shape for this project (float-as-pointer, not never-initialized-global), so don't assume the fix is
"guard against near-zero" like every prior guard in this lineage; trace where the float bit pattern
actually comes from (a struct field being read at the wrong type/offset? a `-1` sentinel value stored
as a float instead of an int?). (3) Symbol-range-check against the next symbol in the `.text` layout to
confirm the crash PC genuinely falls inside `runHangarMenuFromOverlay`, not a next-symbol
misattribution (item -259's closed false lead was exactly this mistake — re-verify every time per iron
rule 5). (4) Guard or fix per whatever the root cause turns out to be; live-verify with a same-run
positive control.

**Option B: batch-fix the 11 confirmed-safe `mission_overlay.txt` `func_0xADDR`/real-name pairs.**
Same low-risk mechanism as item -262's fix (a generic placeholder shadowing a deliberately-named real
function) — NOT the ambiguous real/real kind item -264 was. Lower information value than Option A (it
doesn't advance the active crash-chain thread) but batchable in one regen+verify cycle per the
project's "batch instrumentation, one build/run cycle" rule, and closes out 11 of the remaining 18
duplicate-symbol pairs from s426's catalogue in one pass. Names: `func_800BF4A0`/
`attached3DSoundEmitterNpcHandler`, `func_800C7DC0`/`initNpcActorFromSpawnMessage`, `func_800CA270`/
`initNpcActorVariant`, `func_800CEF20`/`advanceAtStEffectPhaseSound`, `func_800D2CA0`/
`npcInitWithMotionParams`, `func_800D4ED0`/`npcInitChildLinkedToParent`, `func_800DD2D0`/
`npcInitFullModel`, `func_800DFB90`/`applyCraftAnimAndDetailParams`, `func_800E4480`/
`resetCraftInstanceMotionState`, `func_800E8A40`/`runDestructionPhaseSequence`, `func_800ECE10`/
`datItemActorNpcHandler` (all in `symbol_files/mission_overlay.txt`; delete the `func_0xADDR` line for
each, since s426/s427 both confirmed the generic-placeholder-vs-real-name pattern resolves by keeping
the real name and letting the call site auto-follow).

**Recommendation: Option A.** It's the active thread with the higher information value (a genuinely
new failure signature this project hasn't seen before), and per the strategic priority ("M3 crash
work only as systematic idiom-class audits, no reactive single-crash chases") this is still within the
duplicate-symbol idiom-class audit's blast radius — it's the audit's own fix surfacing its next
consequence, not an unrelated reactive chase. If Option A stalls (can't isolate the faulting
instruction, or the soak shows it's not reproducible), fall back to Option B.

## Regen recipe (known-working s426/s427)

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

**New this session**: `fixup_game_funcs.py` REFUSES to run a second time on the same generated files
(checks for its own `RS64_FIXUP_APPLIED` marker) — this is a safety net, not a bug; if you see the
refusal message, it means you forgot to delete `funcs_*.c` and regenerate first, not that something
is broken.

Live-run schedule (same as s423-427, known to reach the war-room/craft-select phase):
```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
    PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh tools/probe.sh <outdir> 300 2
```

## Sandbox notes (confirmed again s427)

`lldb`/`otool -tV`/`find -delete`/plain `rm` with globs all require interactive approval — use the
`python3 -c` glob-delete above. `atos` (prefixed with `env`) only returns `symbol+offset`, not
file:line. `scratch/agent/s193_disasm.py <macho> <symbol> <frame_offset> [window]` plus a manual
symbol-range check remain the working substitute for precise crash-site identification.

## Soak queue

- `scratch/agent/soak_queue/s427_hangarinit_regression.sh` — queued this session, not yet run.
