# Session 2553 symbol census

Target: `0x800D2C98`, hypothesis `generated-symbol-renaming-sweep`.

| Source | Observation | Result |
|---|---|---|
| Companion `mission_overlay.txt` | Retains `fake_func_800D2C98 = 0x800D2C98` and explicitly deletes `func_800D2CA0` in favor of `npcInitWithMotionParams`. | Boundary classification |
| Generated `funcs_37.c` | The complete 8-byte span is `j 0x800D2CA0` followed by `nop`; it has no prologue, return sequence, or independent body. | Tail-call trampoline |
| Active symbol TOML | `{ name = "fake_func_800D2C98", vram = 0x800D2C98, size = 0x8 }`, followed at `0x800D2CA0` by `npcInitWithMotionParams` of size `0x240`. | Span agrees |
| Overlay table | `fake_func_800D2C98` occupies offset `0x2DB68` for `0x8` bytes; `npcInitWithMotionParams` begins at `0x2DB70`. | Boundary agrees |
| Repository caller search | No call site names the fragment independently; the generated body dispatches directly to `npcInitWithMotionParams`. | No rename candidate |

Outcome: `H-data-boundary` / `H-no-match` selected. The placeholder remains
unchanged; renaming it to `npcInitWithMotionParams` would collapse a real
generated span and is unsupported by the companion classification.

This is a static, single-source census. No build or runtime run was required.
