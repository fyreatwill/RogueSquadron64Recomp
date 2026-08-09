# NEXT work unit

HYPOTHESIS-ID: m3-dod-craft-stick-hold

## s576 recap (read this first)

**Item -7 breakthrough: synthetic case-5 Start exits hangar (state 5→8, VI 640).**

Real 2nd Start never reaches AC8C0 (`getControllerNewButtonsPressed` edge table).
Force at AC8C0 n=40: ship-active ret=0 → hangar-sel AC914 → state-write AC94C 5→8
→ graceful-menu + non-sentinel frame-ret → VI 512→640 origin 0x6A2900.

| Hyp | s576 |
|-----|------|
| H-exit6b real 2nd Start miss | CONFIRMED |
| H-exit6a Start@AC8C0→hangar-sel | CONFIRMED (force) |
| H-exit1 ship-active blocks | REFUTED at confirm (ret=0) |
| H-exit6c deeper gate | REFUTED |

## This iteration's work unit

**Item -7 — deliver a real Start edge during case 5 (or prove host never samples it).**

### Hypotheses
- H-edge1: SDL_GetKeyboardState never sees 2nd RETURN (CGEventPostToPid / pump race).
- H-edge2: `setNewAndPreviousButtonsPressed` runs but previous-buttons still has Start stuck
  (missed key-up) so new=0.
- H-edge3: hangar polls gNewButtonsPressed only after edge already cleared same frame by
  another reader (unlikely — poll is once at frame top).
- H-edge4: controller port index at -0x2930 is wrong in case 5 (different from case 3).

### Discriminating measurements (batch one build)
1. Log at AC8C0 (or setNewAndPreviousButtonsPressed): current buttons, previous, new, port.
2. Host log when `get_n64_input` sees START (rate-limit on/off edges).
3. Optional: if host sees START but guest new=0 → H-edge2; if host never sees → H-edge1.

Positive control: leave still produces AC0F0 a_start=1 + state 5; force path still works
with ROGUESQ_FORCE_CASE5_START as regression check if edge work regresses.

### Exact commands (sketch)
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
# After landing edge instrumentation:
env PROBE_MODE=double_start HOLD_S=12 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s577_item7_real_edge 5 12
grep -E 'case5-force-start|buttons-hangar.*a_start=1|hangar-sel|state-write|newbtn|host-start|hangar-state' \
  scratch/s73_post_a_scene/s577_item7_real_edge/run.log | head -80
```

### Expected outcomes
- Host START edge + guest new=0 → fix previous-button latch / readControllerInputs.
- Host never START on p2 → fix winctl/SDL pump or inject at get_n64_input.
- Guest new has Start but AC8C0 raw=0 → port/index (H-edge4).
- Real edge → hangar-sel without force → next unit = state-8 → mission overlay.

### Do NOT
- Chase 0x8000afa0 / -338.
- Treat ROGUESQ_FORCE_CASE5_START as a permanent product fix.
- Reopen freelist residual / M5.
- Blind stick HOLD before real edge works (force already proved exit gate).
