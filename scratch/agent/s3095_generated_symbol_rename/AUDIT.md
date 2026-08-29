# Session 3095 audit — `0x80041EEC`

## Hypotheses

- H-ExactIdentity: the record has an exact callable companion identity.
- H-Fragment: the record is a non-callable fragment or defined data gap.
- H-Ambiguous: the available surfaces conflict or do not establish callability.

## Discriminating evidence

| Surface | Observation | Result |
| --- | --- | --- |
| Companion map | `data_gap_80041EEC` is documented as a 4-byte record before `allocAndInitDoublyLinkedNodePool12`, not a callable function. | H-Fragment |
| Generated body | `funcs_9.c` contains only `lw $t2, 0x12C($sp)` at `0x80041EEC`; no prologue or return sequence. | H-Fragment |
| Callers | No independent caller was found for the record. | H-Fragment |
| Header | The generated declaration was already `data_gap_80041EEC`. | H-Fragment |
| Overlay registration | `recomp_overlays.inl` already registers the 4-byte record as `data_gap_80041EEC`. | H-Fragment |
| Project TOML | The only stale surface was `fake_func_80041EEC`; it is now synchronized to `data_gap_80041EEC`. | H-Fragment |
| Local duplicate references | The rename tool already mapped `fake_func_80041EEC` to `data_gap_80041EEC`; no conflicting destination was found. | H-Fragment |

## Selection

H-Fragment. This is a naming-only synchronization; no build or game run is
needed because generated output already carries the selected name.
