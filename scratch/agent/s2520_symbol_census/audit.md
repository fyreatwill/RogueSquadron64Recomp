# s2520 generated-symbol census

Region: main overlay `0x80005570–0x8000595C`, spanning the PI/DMA worker
cluster in `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/`.

## Hypotheses and discriminator

- `H-named-match`: a placeholder has an exact companion symbol/source match
  and can be renamed without changing generated behavior.
- `H-no-match`: the complete region has no defensible human mapping, so the
  placeholder stays.
- `H-regeneration-risk`: an apparent name exists, but the active generation or
  fixup path cannot preserve it safely.

The discriminator is the complete placeholder table joined against the
companion symbol file, companion source search, and generated body/boundary.
An exact match would select `H-named-match`; no exact match selects
`H-no-match`; a tooling-preservation failure would select
`H-regeneration-risk`.

| address | generated name | generated body/boundary | companion evidence | result |
|---|---|---|---|---|
| `0x8000595C` | `fake_func_8000595C` | one instruction, `addu v0, zero, zero`, immediately after `setDmaSlotMaxTxStepSize` at `0x80005938` and immediately before `initMemoryPack` at `0x80005960` | `main_overlay.txt` retains `fake_func_8000595C`; source-wide search found no human symbol or m2c definition at this address | unchanged |

The named functions in the same interval are independently supported by the
companion symbol file: `piDmaWorker`, `submitDmaRequestBatch`,
`initPiDmaWorker`, `dispatchPendingPiDmaToWorker`, `getAssetRamAddress`, and
`setDmaSlotMaxTxStepSize`. The complete interval therefore selects
`H-no-match`. This is a single-source/static result; it does not prove the
one-instruction fragment is dead or permanently unnameable. No generated
code, runtime, or mitigation changed, so no build was warranted.
