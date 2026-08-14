# NEXT work unit (s1075)

HYPOTHESIS-ID: selector-nongenerated-ownership

Perform one bounded generated-source audit of callers and raw-dispatch entries
for `func_800B47C4` (`0x800B47C4`). Trace only the argument provenance needed
to classify `temp_s1 = arg0 & 0xFF` before its computed-base XOR write at the
companion source line 1007. Include direct generated calls and indirect
raw-address references; do not build or run.

Competing hypotheses and discriminator:

* `H-B47C4-index-2`: a generated caller or dispatch path proves `arg0 & 0xFF`
  can be 2, selecting the selector-byte alias as a concrete path.
* `H-B47C4-other-index`: all callers prove another index or an unrelated call
  contract, ruling out this generated path to `+0x14`.
* `H-B47C4-open`: at least one caller/dispatch path leaves `arg0` provenance
  unresolved; preserve the pointer-mediated possibility without claiming
  runtime corruption.

Discriminating measurement: one table containing every generated caller or
raw-dispatch entry, its passed `arg0` expression, the resulting masked-index
proof, and whether the call can reach the XOR branch. A proven index of 2
selects `H-B47C4-index-2`; all proven non-2 paths select
`H-B47C4-other-index`; any unresolved provenance selects `H-B47C4-open`.

Exact commands:

```sh
rg -n -B 8 -A 12 '800B47C4|func_800B47C4|0x800B47C4' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --glob 'funcs_*.c' 2>/dev/null
rg -n -S '800B47C4|func_800B47C4|0x800B47C4' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  --glob '*.{c,h,md}' 2>/dev/null
```

No build or runtime run is needed for a source-classification result.
