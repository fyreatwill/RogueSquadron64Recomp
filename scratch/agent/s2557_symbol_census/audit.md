# Session 2557 — generated-symbol census at `0x800E447C`

## Discriminator

The complete region table was required to distinguish an exact/semantic rename
from an unresolved symbol or a boundary fragment. Evidence was checked in the
active generated files, the companion mission symbol input, repository-wide
source/caller search, and the ROM path as a positive boundary check.

| placeholder | complete span | body | candidate | evidence | result |
|---|---|---|---|---|---|
| `fake_func_800E447C` | `0x800E447C–0x800E447F` (4 bytes) | `lw v1, 0x14(v1)` | none; not `resetCraftInstanceMotionState` | `funcs_39.c`, `funcs.h`, and `recomp_overlays.inl` agree; companion `mission_overlay.txt` retains the fake symbol and starts `resetCraftInstanceMotionState` at `0x800E4480`; exact-address/source/caller search found no independent human definition or call site | `H-data-boundary / H-no-match`; unchanged |

The one instruction is between the preceding function's epilogue at
`0x800E4478` and the next function's prologue at `0x800E4480`. The companion
input explicitly deletes `func_800E4480` as a duplicate-symbol collision, so
borrowing the next function's name would absorb a real boundary. The ROM check
was attempted at overlay ROM offset `0x3F34C`, but the expected local ROM file
was absent (`build/Debug/rogue_squadron.z64`); this is a limitation, not a
positive ROM result.

No generated code, symbol input, runtime, or behavior changed. The next
unresolved mission-overlay placeholder is `0x800E71C8`.
