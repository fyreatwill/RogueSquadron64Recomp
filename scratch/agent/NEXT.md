# NEXT work unit

HYPOTHESIS-ID: m3-dod-craft-stick-hold

## s573 recap (read this first)

**Item -7 offline: H1 CONFIRMED — craft-leave never enters mission.**

- s572 runlog: overlay sections 0,1 boot; start-match 3 (menu) → 4 (cinematic) → 3 (menu).
  **Mission section idx=2 rom=0xA5D30 never start-matches.** 0 mission* / gracefulMenu* tags.
  hangarbay-entry n=1000 through death; stack still `runHangarSelectionFrame`.
- Source hangar exit is a **multi-frame state machine**, not "Start leaves":
  1. A|START (0x9000) in `updateHangarBayScene` writes craft idx → `0x800CD6D4` **iff**
     `isPlayerShipActive()` is 0 (gPlayerShip `0x800CC85C` null).
  2. `runHangarSelectionFrame` returns non-`0x00FFFFFF` **iff**
     `accumulateShipThrottleCharge()` nonzero (needs gPlayerShip live + charge counter ≥7).
  3. `runHangarMenuFromOverlay` then `gracefulMenuShutdown` and returns to menu overlay.
- Synthetic Start correctly maps to N64 0x1000 (`main.cpp`). s74 A-no-op / s572 camera-only
  leave fit gate (a) and/or (b) stuck.

## This iteration's work unit

**Item -7 — which hangar-exit gate is stuck? (one instrumented leave run)**

Batch all counters in ONE fixup + ONE cmake + ONE leave run (HOLD_S=20 enough; full 60s not
required). Do not chase crashes.

### Hypotheses
- H-exit1: `isPlayerShipActive` stays 1 during craft display → A|START never writes selection
  (matches s74 A no-op).
- H-exit2: selection writes (0x800CD6D4 changes) but `accumulateShipThrottleCharge` always 0
  → poll never exits (ship null or charge stuck).
- H-exit3: both gates fire (selection non-0xFFFFFF, throttle nonzero, frame ret non-sentinel)
  but `gracefulMenuShutdown` / menu return fails → need post-exit path next.
- H-exit4: `getControllerNewButtonsPressed` never sees 0x9000 on leave Start (input path) —
  positive control: log raw new-buttons on leave frame.

### Discriminating measurements (ONE build)
In `fixup_game_funcs.py` (not hand-edit funcs_*.c), add rate-unlimited-after-leave or
always-on-first-N after hangar entry:

| counter | where | fields |
|---------|-------|--------|
| ship-ptr | `isPlayerShipActive` entry/ret | n, gPlayerShip, ret |
| hangar-sel | after confirm store `0x800CD6D4` / every frame tail | n, value |
| throttle-ret | `accumulateShipThrottleCharge` exit | n, ret, ship non-null |
| frame-ret | `runHangarSelectionFrame` after_2 (existing ckpt) | extend to log ctx->r2 every iter (or 1/50 after n=20) |
| buttons | after `getControllerNewButtonsPressed` in updateHangarBayScene | n, raw v0, v0&0x9000 |

Positive control: hangarbay-entry must keep firing; at least one buttons sample must show
Start bit when console says `[keys] probe p1 start`.

### Exact commands
```bash
# After fixup lands (edit fixup_game_funcs.py only):
# regen if needed, or if patch is pure fixup-on-existing: just cmake if fixup already applied
# Prefer: re-run fixup on existing RecompiledFuncs then cmake — only full regen if fixup requires clean.

python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py   # if patches are additive/idempotent
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
cmake --build build -j8 --target RogueSquadron64Recomp

# Leave-only short hold (entry proof, not stick DoD):
env PROBE_MODE=start_only HOLD_S=20 \
  ROGUESQ_LOG_ALL=0 \
  zsh tools/run_mission_keys.sh   # or whatever recipe s571 used — match s572 env

# Analyze:
grep -E 'ship-active|hangar-sel|throttle-ret|hangarmenu-ckpt|buttons-hangar|hangarbay-entry' run.log | head -80
# After leave wall-time: did 0x800CD6D4 leave 0xFFFFFF? did throttle ret ever 1? did frame ret exit sentinel?
```

### Expected outcomes
- H-exit1: ship-ptr always non-null on confirm frames → next unit = who sets gPlayerShip and when
  it should clear for craft confirm.
- H-exit2: sel writes, throttle always 0 → next unit = charge path / ship setup for hangar.
- H-exit3: hangar exits (gracefulMenu + after_3) but no mission overlay → next unit = menu→mission
  transition after hangar return.
- H-exit4: Start never in new-buttons → fix input path for hangar phase.

### Do NOT
- Chase 0x8000afa0 / -338 (wait 3rd occ).
- Blind HOLD_S=60 stick soaks.
- Reopen M5 unless a new audio signature appears (due recheck was s573; quick scan only if idle).
- Resume freelist/sibling residual (exhausted s569).
- Hand-edit funcs_*.c — fixup only.
