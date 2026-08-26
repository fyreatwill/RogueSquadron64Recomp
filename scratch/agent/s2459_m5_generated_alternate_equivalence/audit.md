# s2459 M5 generated-alternate equivalence capture

The first paired attempt used an oracle command missing Rice video and
`--hold-ms`; it stayed on the wrong route and is setup-only. The corrected
oracle passed whole-RDRAM (12,661), exact ranges (1,536 and 1,125), 627
hangar-phase `0x8002BEEC` -> `0x800078EC` predecessor rows, and six
`0x8008F2CC` executions.

The paired port image arm crashed before the target phase in
`matchKeywordWithPriority` (`last-guest-pc=0x8000834C`). A fixed image-only
attempt with the known `ROGUESQ_DRAIN_INLOOP_TICK=1` route aid also crashed
before target capture in `slotDispatcherIter` (`last-guest-pc=0x80007904`).
The passed controls make this a qualified non-result, not evidence for
equivalence or bootstrap-only behavior.

ORIGIN: independent retail controls plus observation-only port attempts; no
output remap, task-data change, gate change, guard, or other mitigation.
