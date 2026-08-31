# NEXT work unit — census M5 consumer indirect dispatch

HYPOTHESIS-ID: m5-consumer-indirect-dispatch

Session 3366 selected `H-PortConsumerIndirectGap`: the valid qualified route
reached title and hangar, the callback edge and PCM source/consumer controls
fired, but the named `0x80019B74` consumer-entry marker stayed zero. Audio task
joins used `musyx_stub` and were incomplete by design.

Competing hypotheses for the next unit:

- `H-GeneratedConsumerEdgePresent`: an existing generated indirect call feeds
  one or more named consumer PCs, but the current marker misses that edge.
- `H-GeneratedConsumerEdgeAbsent`: no generated caller reaches the named
  consumers; the unresolved dispatch is outside the generated static map.
- `H-ConsumerNameOrPCMismatch`: the runtime marker names or keys the wrong
  consumer PCs despite the callback edge being valid.

Discriminating measurement: a bounded static census, not a new runtime field.
Enumerate every generated `jalr`/`LOOKUP_FUNC` site whose target can reach the
four named consumer PCs, classify its source register/constant and overlay,
and compare it with the existing consumer-entry marker definitions. A concrete
generated edge selects `H-GeneratedConsumerEdgePresent`; no edge after a
complete census selects `H-GeneratedConsumerEdgeAbsent`; a mismatch between
the four named PCs and their marker wiring selects `H-ConsumerNameOrPCMismatch`.
An incomplete symbol/overlay map is unresolved, not a null result.

Exact commands:

```sh
rg -n -C 8 'serviceVoicePoolFrame|0x80019B74|consumer_entry|pcm-boundary' src tools ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'jalr|LOOKUP_FUNC' ../N64Recomp/RecompiledFuncs/funcs_*.c | rg '8009B5A8|8009BD7C|80019B74|consumer|voice|slot'
```

Inspect only the existing regeneration-safe marker definitions and generated
call sites; no build or runtime experiment is needed unless the census finds
missing marker wiring that can be corrected without changing behavior. No
behavior change or mitigation.
