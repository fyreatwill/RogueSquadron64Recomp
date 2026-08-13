# NEXT work unit (s876)

HYPOTHESIS-ID: m3-coalesce-value-legitimacy

Perform one source-only whole-idiom audit of every computation feeding
`0x801163E4`, `0x801163E8`, `0x801163F8`, and `0x8010FF18`, including all
partition inputs, alignment arithmetic, and every caller boundary. Do not
build, run, or add a guard.

Competing hypotheses:

- H-input-range-legitimate: every writer is fed by valid display/heap inputs.
- H-input-range-malformed: a bounded writer input is already invalid.
- H-unknown-downstream: source ranges remain unclassifiable.

Discriminating measurement: a complete writer/input table. One malformed
upstream operand selects H-input-range-malformed; all operands proven valid
with no bad source selects H-unknown-downstream; complete valid ranges plus a
documented state transition selects H-input-range-legitimate.

Exact commands:

```sh
rg -n -- "0x63E4|0x63E8|0x63F8|-0xE8|partitionFramebufferMemory|coalesceFreeHeapBlocks" ../N64Recomp/RecompiledFuncs
```

Inspect at most 60-line windows around every hit, enumerate callers and
stores, and write the classification into `docs/CURRENT-TRUTH.md` and
`PORTING-STATE.md`. This is a systematic idiom audit; no runtime evidence is
required for this unit.
