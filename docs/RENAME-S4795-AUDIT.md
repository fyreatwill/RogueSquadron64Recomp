# Generated-symbol sweep: mission overlay range

Session 4795 audited `0x800AE000 <= address < 0x800B9000` against the
companion `rogue_squadron64/symbol_files` and the installed generated snapshot.
The positive-control condition was that every placeholder in the range be
enumerated from `RecompiledFuncs`; all eight were present in the generated
declarations and overlay table.

| Address | Generated symbol | Companion entry | Evidence | Decision |
|---|---|---|---|---|
| `0x800AE3E4` | `fake_func_800AE3E4` | same fake symbol | Companion says the real entry starts at `initPlayerCraftTrailBuffers` (`0x800AE3F0`). | Keep fake |
| `0x800AF6A8` | `fake_func_800AF6A8` | same fake symbol | No semantic destination at this address. | Keep fake |
| `0x800B2628` | `fake_func_800B2628` | same fake symbol | No semantic destination at this address. | Keep fake |
| `0x800B42BC` | `fake_func_800B42BC` | same fake symbol | Companion identifies the following real function as `playerXwingInit`. | Keep fake |
| `0x800B47C4` | `fake_func_800B47C4` | same fake symbol | Companion identifies the following controller handler at `0x800B47D0`. | Keep fake |
| `0x800B58B4` | `fake_func_800B58B4` | same fake symbol | Companion identifies the following real function as `playerAwingInit` and documents a split artifact. | Keep fake |
| `0x800B75C4` | `fake_func_800B75C4` | same fake symbol | Companion identifies the following real function as `playerYwingInit`. | Keep fake |
| `0x800B89F4` | `fake_func_800B89F4` | same fake symbol | Companion identifies the following real function as `playerVwingInit`. | Keep fake |

The generated snapshot has no ordinary `func_` placeholder in this range and
the companion symbol files contain no competing semantic name at any of these
eight addresses. The discriminator selects H3 (no unique identity) for every
candidate. No symbol mapping or generated output was changed.
