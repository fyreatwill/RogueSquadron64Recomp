# s1047 retail state-transition audit

This is a static audit only; no game run or retail watch was used.

| Path/role | Guest address | Evidence | Input/state result |
|---|---:|---|---|
| Controller edge producer | `0x80079CE0` / `0x80079D08-0x80079D2C` | `setNewAndPreviousButtonsPressed` calls `readControllerInputs` for each port, then stores current and `current & ~previous` | The game produces the edge value. |
| Edge consumer helper | `0x80079F50` | `getControllerNewButtonsPressed` returns `D_8013A960[idx]` | A valid Start edge is available as `0x1000`. |
| First audited hangar frame | `0x800AAD9C` | `0x800AADCC` polls, `0x800AADD0` refreshes edges, `0x800AB0EC` reads new buttons, and `0x800AB0F4` masks `0x4000` | This loop's immediate action is B-only, not Start-only. It is a hangar-loop predicate, not proof of the attract handoff. |
| Hangar overlay handoff | `0x800C6854` | `0x800C5A8C` calls it from the state-table case selected by `lhu [state-0xB0] == 0`; it loops on `runHangarSelectionFrame` | Entry is state-table driven; no Start read is on this handoff edge. |
| Adjacent menu navigation | `0x800C6170-0x800C61D4` | Edge reads update a bounded selection; the third read masks `0x5000` | This path recognizes Start+B, not bare Start. |
| Adjacent menu action families | `0x800BFB40`, `0x800C34B8`, `0x800AC0E8` and related callers | Generated code masks `0x9000` or `0xD000` after `getControllerNewButtonsPressed` | Several menu actions require composite Start+A or Start+A+Z masks; the exact attract caller is not among these bounded hits. |
| State writer after handoff | `0x800C5A94-0x800C5AC8` | Return from `runHangarMenuFromOverlay` stores state `1` or `6`, otherwise stores `1` at `state-0xB0` | This is post-entry and cannot explain why retail remains in width-320 attract. |

## Discriminator result

The table does not select `H-retail-start-gate` versus `H-retail-timing-state`
for width-320 attract: the attract dispatcher and its state write are not in
this bounded handoff. It identifies `H-retail-other-input` as the highest-value
lead in the next menu layer, but that is **single-source/static**, not a retail
phase conclusion. The next audit must trace the width-320 state's caller into
the state table at `0x800C5A5C` and its writer.

The independent oracle controls still establish that Start pad words and the
documented eleven-event schedule reach the retail game; they do not identify
which guest predicate consumes the edge.
