# Session 2529 generated-symbol census

## Complete region table

| Address span | Placeholder | Generated body | Companion symbol | Source/m2c/caller evidence | Result |
|---|---|---|---|---|---|
| `0x8007C298–0x8007C29C` (8 bytes) | `fake_func_8007C298` | `sll a1,a2,1`; `addu a1,a1,a0` | `fake_func_8007C298 = 0x8007C298; // defined:true` | No exact-address definition, human symbol, m2c implementation, caller attribution, or semantic candidate found; next symbol is `initNpcTexturedEffectFromTemplate` at `0x8007C2A0` | Leave unchanged |

The generated overlay table independently confirms the 8-byte span
(`offset=0x0007BE58`, `rom_size=0x8`). The two instructions compute an
address-like value in `a1`, but without a call-site contract or matching
source definition that is insufficient to name the fragment. This is a
static, single-source result and does not prove whether the fragment is a
callable function or a boundary artifact.

## Hypothesis result

- `H-named-match`: not selected; no unambiguous name exists.
- `H-no-match`: selected for this bounded region.
- `H-regeneration-risk`: not reached; no rename was attempted.

No generated code, runtime, build configuration, or mitigation changed.

ORIGIN: diagnostic-only. No runtime, generated function, submodule, or
mitigation-shaped behavior changed.
