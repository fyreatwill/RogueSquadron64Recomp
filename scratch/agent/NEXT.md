# NEXT work unit — census the port source/target callback edge

HYPOTHESIS-ID: m5-callback-table-writer

Session 3363 selected `H-RetailLiteralArgument`: the independent retail
oracle passed all controls and observed `0x800919EC -> 0x80007910` with
`$a0=0x8009123C` in both target phases. The next unit is one bounded,
regeneration-surviving port census of the same source/target table; no
behavior change or mitigation.

Session 3362 found the only generated `0x800919D4`/`0x800919EC` site in
`initN64RspMixer`: `$a0` is set to literal `0x8009123C` immediately before
the `jalr`, and the target is loaded from the slot initialized at
`0x80091900`. Session 3361 paired the port callback-table store: `0x80007928`
wrote `0x8009123C`, `0x80007968` cleared, and `0x80017D08` wrote only
`0x400/0x800` halfwords.

Competing hypotheses:

- `H-PortMatchesRetail`: the port callback-table writer and indirect call
  produce the retail target/value pair.
- `H-PortWriterMismatch`: the port writes a different source value, writer,
  or target than retail.
- `H-PortProbeGap`: the port chain is present but the census misses its edge.

Discriminating measurement: one build/run with an aggregate, phase-gated
probe joining every write to `0x8011A8A4:0x8011A8B8` to its guest writer PC and
the subsequent `0x800919EC`/`0x80007910` target and `$a0`, while retaining
host/task/PCM, title, and hangar controls. A paired port row matching retail
(`0x80007928 -> 0x8009123C` and `0x800919EC -> 0x80007910`, `$a0=0x8009123C`)
selects `H-PortMatchesRetail`; a controlled different writer/value/target
selects `H-PortWriterMismatch`; table writes plus no chain rows with controls
selects `H-PortProbeGap`.

Exact bounded preparation before any build:

```sh
rg -n -C 8 '800919D4|800919EC' ../N64Recomp/RecompiledFuncs/funcs_*.c
```

Then inspect the existing aggregate probe/fixup path, add only the missing
joined fields, build once, and run the qualified port recipe. The positive
controls must visibly fire before any null is interpreted.
