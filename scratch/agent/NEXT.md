# NEXT work unit

HYPOTHESIS-ID: m3-dod-craft-stick-hold

## s574 recap (read this first)

**Item -7: leave Start hits hangar case 3, never case 5 confirm.**

- Positive control: hangarbay-entry n=900, frame-ret n=950 all sentinel,
  buttons site 0x800AC0F0 n=716.
- Leave Start: `[buttons-hangar] site=0x800AC0F0 n=716 raw=0x00001000 a_start=1`.
- 0 hangar-sel writes, 0 non-sentinel frame-ret, 0 graceful-menu.
- Jump table on hangar state `0x800CC3E4` (`-0x3C1C` from 0x800D) at 0x800ABB74:
  - **case 3** → L_800AC024 → site **0x800AC0F0** (where leave landed)
  - **case 5** → L_800AC8B0 → site **0x800AC8C0** (isPlayerShipActive + write 0x800CD6D4)
  - case 5 site only saw n=0..4 early empty polls during whole run
- Case 3→5 transition: `sb 5` at 0x800AC1BC after Start, gated on bay-flag bit
  (`-0x2928` & (1 << table[`-0x2918`])); fail path calls bsearchFactor5TableByU16Key.
- H-exit4 REFUTED. H-exit1/2 deferred (case 5 never reached on leave). H-exit5 NEW.
- Item -338 3rd occ (0x8000afa0 / beginFrameDLChunk+46800) — do not chase yet.

## This iteration's work unit

**Item -7 — why case 3 Start does not advance to case 5?**

One instrumented leave run. Batch into fixup (or one-shot if sentinel blocks) +
one cmake + one leave run (HOLD_S=20).

### Hypotheses
- H-exit5a: bay-flag bit test fails on leave Start (`(-0x2928 & bit)==0`) → error
  path, state stays 3.
- H-exit5b: bit test passes, state becomes 5, but next frame reverts to 3/4 before
  confirm poll runs.
- H-exit5c: leave Start never takes the success arm of AC0F0 for another reason
  (wrong sub-flag `-0x2934`, state!=3 at compare AC0B0, etc.).
- H-exit5d: state is already ≥5 but jump table index wrong / switch_error path
  (unlikely — AC0F0 would not run).

### Discriminating measurements (ONE build)
Always-on (or rate-limit steady; always on Start and on state change):

| counter | where | fields |
|---------|-------|--------|
| hangar-state | updateHangarBayScene entry (or just before jr table) | n, state=MEM_BU(0x800CC3E4) |
| case3-start | after 0x800AC0F0 andi when raw&0x9000 | n, bay_idx, flag_word, bit, pass |
| state-write | every `sb` to -0x3C1C | n, old→new, guest pc |
| case5-entry | L_800AC8B0 entry | n (should stay 0 if 5a) |

Positive control: hangarbay-entry still fires; leave Start still a_start=1 at AC0F0;
if 5a then pass=0 on that frame; if 5b then state-write 3→5 then 5→3 same run.

### Exact commands
```bash
# Apply probes (prefer fixup after clear+regen OR one-shot on sentinel tree)
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
cmake --build build -j8 --target RogueSquadron64Recomp

env PROBE_MODE=start_only HOLD_S=20 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s575_item7_case3_to5 5 12

grep -E 'hangar-state|case3-start|state-write|case5-entry|buttons-hangar|hangarbay-entry' \
  scratch/s73_post_a_scene/s575_item7_case3_to5/run.log | head -80
```

### Expected outcomes
- 5a: case3-start pass=0 on leave → next unit = who fills -0x2928 / unlock table.
- 5b: state-write 3→5 then revert → next unit = what clears state 5.
- 5c: a_start=1 but case3-start never logs → wrong arm details.
- 5d: switch_error / wild state → fix jump table / state init.

### Do NOT
- Chase 0x8000afa0 / -338 (3 occs filed; after hangar exit only).
- Blind stick HOLD_S=60.
- Reopen M5 / freelist residual.
- Hand-edit funcs_*.c without mirroring into fixup_game_funcs.py.
