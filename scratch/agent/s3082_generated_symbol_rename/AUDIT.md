# Session 3082 generated-symbol audit: `0x80019808`

## Discriminating table

| Hypothesis | Evidence | Result |
| --- | --- | --- |
| H-ExactIdentity | No semantic callable identity is present. | Rejected. |
| H-Fragment | Companion map and redefs call it `data_gap_80019808`; the generated body is exactly two instructions between `projectPointToScreen` and `awaitFrameSyncMesgBlock`. | Selected. |
| H-Conflict | Address, extent, neighboring symbols, and overlay registration agree. | Rejected. |
| H-Unresolved | The available surfaces are sufficient to classify the record mechanically. | Rejected. |

## Six-surface evidence

- Companion `main_overlay.txt`: `data_gap_80019808 = 0x80019808`, defined, immediately before the frame-sync routines.
- Companion `build/redefs.txt`: `func_80019808`, `D_80019808`, and `fake_func_80019808` all resolve to `data_gap_80019808`.
- Generated body: `funcs_4.c` contains only `lwc1 $f2, 0x1830($at)` and `mul.s $f0, $f0, $f2`; it has no callable prologue or return sequence.
- Generated header: `funcs.h` declares only `data_gap_80019808`.
- Overlay registration: `recomp_overlays.inl` registers an 8-byte record at ROM offset `0x193C8`.
- Project symbol TOML: the entry is `data_gap_80019808`, VRAM `0x80019808`, size `0x8`.

The only generated-tree references are the definition, declaration, and overlay registration; no caller was found. The regeneration-safe mapping already translates the placeholder to the mechanical gap name, so no additional code rename is warranted.

ORIGIN: naming-only classification. No runtime, audio, route, mitigation, or generated instruction behavior changed.
