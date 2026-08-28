# Session s2888 generated-symbol sweep: `0x800E0000..0x800F0000`

The interval contains nine unresolved placeholder records in the generated
snapshot. Every row was classified before any rename.

| Address | Size | Generated body / boundary evidence | Companion evidence | Class | Action |
|---|---:|---|---|---|---|
| `0x800E406C` | `0x4` | One `sw $a0,0x20($sp)` between the epilogue at `0x800E4068` and `handleRayShieldedNpcDestroy` at `0x800E4070`; no prologue or return | No semantic symbol at the exact boundary | H-DataGap | `data_gap_800E406C` |
| `0x800E447C` | `0x4` | One `lw $v1,0x14($v1)` between `handleRayShieldedNpcDestroy` and `resetCraftInstanceMotionState`; no prologue or return | No semantic symbol at the exact boundary | H-DataGap | `data_gap_800E447C` |
| `0x800E71C8` | `0x8` | Two instructions (`lhu` and `lw`) immediately before `transformCraftAnchorsApplySubFx3`; no callable prologue/epilogue | Exact boundary is fake; only the next callable is named | H-DataGap | `data_gap_800E71C8` |
| `0x800E8A34` | `0xC` | Three-instruction fragment immediately before the `runDestructionPhaseSequence` prologue; not an independent callable body | Existing `build_redefs.py` mapping and deleted-duplicate note identify the duplicate-symbol prefix | H-DataGap | `duplicateSymbolPrefixForRunDestructionPhaseSequence` |
| `0x800E9AD8` | `0x8` | Two instructions (`lw` and `addiu`) immediately before `func_mission_overlay_800E9AE0`; no prologue/return | Exact boundary is fake; only the next callable is named | H-DataGap | `data_gap_800E9AD8` |
| `0x800EC10C` | `0x4` | One invalid COP2 word decoded to `do_break`, immediately before `allocObjectPoolNode`; not callable game code | Exact boundary is fake; only the next callable is named | H-DataGap | `data_gap_800EC10C` |
| `0x800ED148` | `0x8` | Two instructions (`lui`/`addu` building `$at`) immediately before `claimSongSlotForCurrentHandle`; no prologue/return | Exact boundary is fake; only the next callable is named | H-DataGap | `data_gap_800ED148` |
| `0x800EFD74` | `0xC` | Three instructions immediately before `dispatchSlotAction5IfActive`; no independent prologue/return | Exact boundary is fake; only the next callable is named | H-DataGap | `data_gap_800EFD74` |
| `0x800EFDDC` | `0x4` | One `lw $v1,0xCC($fp)` immediately before `updateNpcEventTimer`; no prologue/return | Exact boundary is fake; only the next callable is named | H-DataGap | `data_gap_800EFDDC` |

No row has unique callable companion evidence. All nine are bounded
non-callable records; the next sweep begins after `0x800F0000`.
