# Session 3029 — generated symbol audit at `0x80062B04`

## Discriminator

The exact-callable hypothesis is selected only if the companion map, generated
body boundary, callers, header, and overlay registration agree. The generated
callable token and overlay row are the positive controls for the rename.

| Evidence source | Observation | Classification |
|---|---|---|
| Companion symbol map | `main_overlay.txt` names `advancePlayerAnimationPhase = 0x80062B04`. | Exact semantic identity |
| Companion source/comments | The companion entry is in the player-slot animation family, between `startPlayerSlotAnimationChannel` and `initPlayerSlotAnimationChannelFull`. | Meaning agrees with neighboring API |
| Generated body | `RecompiledFuncs/funcs_14.c` has a standalone `RECOMP_FUNC void advancePlayerAnimationPhase(...)` beginning at `0x80062B04`; the body ends at `0x80062C7C`, matching size `0x178`. It advances a slot phase, clamps the float, and clears the active byte when complete. | Callable boundary and behavior agree |
| Generated callers | Five direct `jal 0x80062B04` sites were found: `0x80062818`, `0x800AAE14`, `0x800AEC34`, `0x800AF448`, and `0x800AF460`. | No caller identity conflict |
| Generated header | `funcs.h` declares `advancePlayerAnimationPhase` once. | Header positive control passes |
| Overlay registration | `recomp_overlays.inl` contains one main-overlay row at offset `0x626C4`, size `0x178`, for `advancePlayerAnimationPhase`. | Registration positive control passes |
| Duplicate check | No second generated callable definition or conflicting overlay row for `0x80062B04` was found. | No ambiguity |

## Result

`H-exact-callable` selected. The project symbol TOML was stale and now uses
`advancePlayerAnimationPhase`; no generated source or runtime behavior was
modified. `H-inline-fragment` and `H-ambiguous` are rejected for this address.
