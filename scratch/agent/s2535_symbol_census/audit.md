# s2535 generated-symbol census

Date: 2026-08-26
Hypothesis: `generated-symbol-renaming-sweep`

| Region | Generated body | Companion/project evidence | Candidate | Result |
|---|---|---|---|---|
| `0x80097D58–0x80097D5F` (8 bytes) | `lw $fp, 0x88($sp)`; `addiu $sp, $sp, 0x90` | `funcs_26.c`, `funcs.h`, `recomp_overlays.inl`, `syms/rogue_squadron.syms.toml`, and `rogue_squadron64/symbol_files/main_overlay.txt` all retain `fake_func_80097D58`; next complete body is `clearStreamedVoiceFlags` at `0x80097D60` | None | Leave unchanged |

The size-8 project-symbol entry and the next symbol at `0x80097D60` establish
the complete region. The two instructions are a function-epilogue fragment,
not a complete callable body. Exact-address searches in the companion source,
m2c, symbol files, generated implementation, declarations, and overlay table
found no human name or caller attribution. Naming it after the following
function would rewrite a generated boundary without evidence.

This is a static, single-source result; no generated code or runtime behavior
changed, and no regeneration/build was warranted.
