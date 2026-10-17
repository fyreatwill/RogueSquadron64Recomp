# Generated-symbol audit — `__osDequeueThread`

## Candidate

- Symbol: `__osDequeueThread`
- Address: `0x80034790`
- Companion range: `0x80034790` through `0x800347D0`
- Hypothesis: `generated-symbol-renaming-sweep`

## Discriminator

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree inspection found no
generated body, placeholder, overlay record, or direct call site at
`0x80034790`. The preceding generated function ends at `0x8003478C`, and the
next companion symbol is `__osTimerServicesInit` at `0x800347D0`.

## Result

This is the H-host-wrapper outcome, specifically an unmaterialized
libultra/ABI entry. Preserve the existing semantic ABI name
`__osDequeueThread`; no generated-symbol rename or build/soak was warranted.
The result rules out a generated body and span mismatch for this candidate,
but says nothing about runtime behavior of the wrapper.
