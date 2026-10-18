# Next work unit: one generated-symbol renaming candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Bound the sweep to `fake_func_800B47C4`, outside the already-audited
`func_800E9AE0`. The candidate census found three non-data mismatches; this
one is the only one with a named 0xC-byte preamble mapping and a companion
comment identifying the following real `menuControllerInput` body. Before
the rename, the competing hypotheses are:

* H1: `fake_func_800B47C4` is a real generated 0xC-byte preamble and the
  existing `menuControllerInputPreamble` mapping is exact; rename all generated
  references.
* H2: the 0xC-byte record is data or an invalid split; leave it address-coded
  despite the nearby menu name.
* H3: the generated snapshot and mapping are already synchronized or the
  address is reused; no rename is safe.

Discriminator: generated prologue span (`0x800B47C4` through `0x800B47CC`),
the syms size (`0xC`), and the companion note that `menuControllerInput` starts
at `0x800B47D0`; only H1 authorizes the bounded mapping rename.

The broader census command was:

`rg -n 'func_0x|func_[0-9A-Fa-f]{8}' RecompiledFuncs docs tools | head -200`
