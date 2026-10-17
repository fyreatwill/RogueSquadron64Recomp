# Generated-symbol audit — `__osTimerInterrupt`

## Candidate

- Symbol: `__osTimerInterrupt`
- Address: `0x8003485C`
- Companion range: `0x8003485C` through `0x800349D4`
- Hypothesis: `generated-symbol-renaming-sweep`

## Discriminator

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree inspection found no
generated body, placeholder, overlay record, or direct call site at
`0x8003485C`. The companion symbol map places the next entry,
`__osSetTimerIntr`, at `0x800349D4`, giving this candidate a nominal `0x178`
span with no generated body to validate.

## Result

This is the H-host-wrapper outcome, specifically an unmaterialized
libultra/ABI entry. Preserve the existing semantic ABI name
`__osTimerInterrupt`; no generated-symbol rename or build/soak was warranted.
The result rules out a generated body and span mismatch for this candidate,
but says nothing about runtime behavior of the wrapper.
