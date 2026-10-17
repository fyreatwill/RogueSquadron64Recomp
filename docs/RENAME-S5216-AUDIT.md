# Generated-symbol audit — `__osSetCompare`

## Candidate

- Symbol: `__osSetCompare`
- Address: `0x80034BD0`
- Companion range: `0x80034BD0` through `0x80034BE0`
- Hypothesis: `generated-symbol-renaming-sweep`

## Discriminator

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree inspection found no
generated body, placeholder, overlay record, or direct call site at
`0x80034BD0`. The companion symbol map places `osViBlack` at `0x80034BE0`,
giving this candidate a nominal `0x10` span with no generated body to
validate.

## Result

This is the H-host-wrapper outcome, specifically an unmaterialized
libultra/ABI entry. Preserve the existing semantic ABI name
`__osSetCompare`; no generated-symbol rename or build/soak was warranted.
The result rules out a generated body and span mismatch for this candidate,
but says nothing about runtime behavior of the wrapper.
