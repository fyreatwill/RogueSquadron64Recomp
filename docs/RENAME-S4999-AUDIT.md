# Generated-symbol rename audit — Session 4999

The remaining generated placeholders were checked against the companion
symbol files, the generated C bodies, the generated overlay table, the local
TOML, and generated call sites.

| placeholder | companion evidence | span evidence | caller evidence | result |
|---|---|---|---|---|
| `func_8000040C` | `rogue_squadron64/tools/make_elf.py` hard-codes the entry symbol as `func_8000040C`; no companion semantic name exists | generated body and entry record are exactly `0x34` bytes | `main` calls it at `0x80001634` and `0x8000164C` | H-no-safe-map: the live-caller gate passes, but the semantic-name gate fails |
| `func_800E9AE0` | `symbol_files/mission_overlay.txt` deliberately retains the address-coded name and documents the false `0x800E9B10` split | generated body and `recomp_overlays.inl` agree on `0x114` bytes | no generated call site for `func_800E9AE0`; the only nearby `0x800E9B10` reference is the documented false split | H-no-safe-map: exact span passes, but semantic-name and live-caller gates fail |

The local `tools/rename_generated_symbols.py` entries
`clearMemory16ByteBlocks` and `func_mission_overlay_800E9AE0` are inferred or
mechanical names, not companion semantic mappings that satisfy the gates.
Neither placeholder was renamed, and no build or regeneration was run.

This closes the currently available symbol-sweep candidates without claiming
that future companion or generated snapshots cannot add a safe mapping.
