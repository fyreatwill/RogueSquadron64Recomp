# Generated-symbol audit — `__osSetTimerIntr`

## Candidate

- Symbol: `__osSetTimerIntr`
- Address: `0x800349D4`
- Companion range: `0x800349D4` through `0x80034B4C`
- Hypothesis: `generated-symbol-renaming-sweep`

## Discriminator

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree inspection found no
generated body, placeholder, overlay record, or direct call site at
`0x800349D4`. The companion symbol map places the next entry,
`__osInsertTimer`, at `0x80034A48`, giving this candidate a nominal `0x178`
span with no generated body to validate.

## Result

This is the H-host-wrapper outcome, specifically an unmaterialized
libultra/ABI entry. Preserve the existing semantic ABI name
`__osSetTimerIntr`; no generated-symbol rename or build/soak was warranted.
The result rules out a generated body and span mismatch for this candidate,
but says nothing about runtime behavior of the wrapper.
