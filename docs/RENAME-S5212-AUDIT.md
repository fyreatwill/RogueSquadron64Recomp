# Generated-symbol audit — `__osTimerServicesInit`

## Candidate

- Symbol: `__osTimerServicesInit`
- Address: `0x800347D0`
- Companion range: `0x800347D0` through `0x8003485C`
- Hypothesis: `generated-symbol-renaming-sweep`

## Discriminator

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree inspection found no
generated body, placeholder, overlay record, or direct call site at
`0x800347D0`. The companion symbol map places the next entry,
`__osTimerInterrupt`, at `0x8003485C`, giving this candidate a nominal `0x8C`
span with no generated body to validate.

## Result

This is the H-host-wrapper outcome, specifically an unmaterialized
libultra/ABI entry. Preserve the existing semantic ABI name
`__osTimerServicesInit`; no generated-symbol rename or build/soak was
warranted. The result rules out a generated body and span mismatch for this
candidate, but says nothing about runtime behavior of the wrapper.
