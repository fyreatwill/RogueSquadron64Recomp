# Generated-symbol audit — `__osInsertTimer`

## Candidate

- Symbol: `__osInsertTimer`
- Address: `0x80034A48`
- Companion range: `0x80034A48` through `0x80034BD0`
- Hypothesis: `generated-symbol-renaming-sweep`

## Discriminator

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree inspection found no
generated body, placeholder, overlay record, or direct call site at
`0x80034A48`. The companion symbol map places the next entry,
`__osSetCompare`, at `0x80034BD0`, giving this candidate a nominal `0x188`
span with no generated body to validate.

## Result

This is the H-host-wrapper outcome, specifically an unmaterialized
libultra/ABI entry. Preserve the existing semantic ABI name
`__osInsertTimer`; no generated-symbol rename or build/soak was warranted.
The result rules out a generated body and span mismatch for this candidate,
but says nothing about runtime behavior of the wrapper.
