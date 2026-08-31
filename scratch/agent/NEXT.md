# NEXT work unit — obtain independent ground truth for the literal callback argument

HYPOTHESIS-ID: m5-callback-table-writer

Session 3362 found the only generated `0x800919D4`/`0x800919EC` site in
`initN64RspMixer`: `$a0` is set to literal `0x8009123C` immediately before
the `jalr`, and the target is loaded from the slot initialized at
`0x80091900`. Session 3361 paired the port callback-table store: `0x80007928`
wrote `0x8009123C`, `0x80007968` cleared, and `0x80017D08` wrote only
`0x400/0x800` halfwords.

Competing hypotheses:

- `H-RetailLiteralArgument`: retail executes the same guest chain with
  physical evidence of the literal `0x8009123C` argument.
- `H-RetailAlternateArgument`: retail reaches the chain but supplies a
  different argument, separating port state from the static port literal.
- `H-RetailChainAbsent`: the port's observed chain is not the retail path.

Discriminating measurement: use the independent retail oracle to watch the
physical callback-table slot and guest execution at the corresponding chain,
retaining `$a0`/target attribution. A whole-RDRAM write control, callback-slot
write control, title, and hangar controls must all fire. A retail row with
target `0x80007910` and argument `0x8009123C` selects the literal-argument
hypothesis; a different argument selects the alternate-argument hypothesis;
no retail chain row selects the chain-absent hypothesis.

Exact bounded preparation before any build:

```sh
rg -n -C 8 '800919D4|800919EC' ../N64Recomp/RecompiledFuncs/funcs_*.c
```

Then run the existing retail oracle recipe with its whole-RDRAM, callback-slot,
title, and hangar positive controls. Do not change behavior. No port build is
needed unless the oracle exposes an address/argument mismatch requiring a
same-build port row.
