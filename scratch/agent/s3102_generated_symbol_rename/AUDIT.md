# Session 3102 — `fake_func_800B42BC`

## Discriminator

The competing hypotheses were:

- `H-ExactIdentity`: the companion project names a callable routine here.
- `H-Fragment`: the entry is a non-callable fragment or data gap.
- `H-Ambiguous`: extent or callable evidence conflicts.

The discriminator was the six-surface comparison: companion map, generated
body, callers, header, overlay registration, project TOML, plus local
duplicates and the adjacent positive-control body.

## Results

| Surface | Finding |
|---|---|
| Companion map | `mission_overlay.txt` retains `fake_func_800B42BC` and separately names `playerXwingInit` at `0x800B42C0`; its comment says the fake entry is not the real function. |
| Generated body | `RecompiledFuncs/funcs_31.c` contains one instruction, `lw $v0, 0x2C($fp)`, with no prologue, return, or standalone callable body. |
| Callers | No generated caller, `jal`, `j`, `LOOKUP_FUNC`, or absolute pointer targets the address. The positive control `playerXwingInit` has direct callers. |
| Header | The 4-byte entry is independently declared as `fake_func_800B42BC`. |
| Overlay registration | The mission entry is a 4-byte span immediately before the separately registered `playerXwingInit` span. |
| Project TOML | The 4-byte entry was synchronized to `data_gap_800B42BC` at the same VRAM and extent. |
| Local duplicates | Menu overlay occupancy at the same VRAM is a different overlay function, not a second mission symbol or callable identity. |

## Conclusion

`H-Fragment` selected. The orphan load is bounded between a complete preceding
epilogue and the following stack-frame prologue, with no caller or return
sequence. It is now named mechanically as `data_gap_800B42BC` in the project
map and both regeneration rename paths. The generated tree remains governed
by the rename tooling rather than a hand-edited generated source file.

ORIGIN: naming-only classification and regeneration-safe symbol metadata. No
runtime, route, audio, mitigation, or generated instruction behavior changed.
