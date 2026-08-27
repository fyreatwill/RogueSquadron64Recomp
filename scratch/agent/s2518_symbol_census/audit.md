# s2518 generated-symbol census

Region: main overlay `0x8000737C–0x80007908`, represented by
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c`.

## Hypotheses and discriminator

- `H-named-match`: a placeholder has an exact companion symbol/source match
  and can be renamed without changing generated behavior.
- `H-no-match`: the complete region has no defensible human mappings.
- `H-regeneration-risk`: a mapping exists, but the active generated-symbol or
  fixup path cannot preserve it safely.

The discriminator was the complete table of every placeholder in the address
interval, joined against the companion tree's symbol files and source search.

| address | generated name | body | companion evidence | result |
|---|---|---|---|---|
| `0x8000737C` | `fake_func_8000737C` | `addu sp, fp, zero` | `main_overlay.txt` retains the fake name; no other companion hit | unchanged |
| `0x800074D8` | `fake_func_800074D8` | loads `0x800005A4` into `a0` | `main_overlay.txt` retains the fake name; no other companion hit | unchanged |
| `0x8000751C` | `fake_func_8000751C` | `lhu v1, 2(v0)` | `main_overlay.txt` retains the fake name; no other companion hit | unchanged |
| `0x80007908` | `fake_func_80007908` | returns `2`; delay slot loads `0x801A` into `at` | `main_overlay.txt` retains the fake name; no other companion hit | unchanged |

Adjacent functions in the interval have established names
(`installPeriodicCallback`, `periodicCallbackWorker`, `u64DivU64`,
`floatToInt`, and the `rs_str*` family), so the absence is not a census or
symbol-file formatting miss. The bodies are isolated fragments rather than
recoverable semantic routines. No rename or build was warranted.

Outcome: `H-no-match` for this region. This is a single-source/static result;
it does not claim the placeholders are dead or that their original labels can
never be recovered from a future disassembly comparison.
