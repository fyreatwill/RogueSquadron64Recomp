# Session 2926 bounded symbol reconciliation

| VRAM | Generated body | Boundary / instruction evidence | Companion/source evidence | Generated callers/lookups | Action |
|---|---|---|---|---|---|
| `0x80069AEC..0x80069AF0` | `collideSegmentAgainstObjectNodesPreamble`; one instruction: `sll $v1,$a0,1` | Four-byte record immediately precedes the complete `collideSegmentAgainstObjectNodes` prologue at `0x80069AF0`; no standalone return or independent body | Companion map names the adjacent body `collideSegmentAgainstObjectNodes`; no separate semantic source symbol exists for the fragment | No placeholder references, callers, or address lookups beyond the definition/overlay registration | Rename `fake_func_80069AEC` to `collideSegmentAgainstObjectNodesPreamble` in project and companion maps; generated snapshot and regeneration helper were already synchronized |

## Discriminator result

The exact boundary and generated instruction identify an entry fragment for the
adjacent callable body. This selects `H-CallableSemantic`; it is not a proven
data gap and remains callable-adjacent rather than being renamed mechanically.

## Verification

- `python3 tools/rename_generated_symbols.py --help` completed successfully.
- The bounded generated snapshot already contained `collideSegmentAgainstObjectNodesPreamble` and had no `fake_func_80069AEC` definition.
- Project and companion maps were stale and were reconciled.
