# M3 session 3587 — allocator stride-scan audit

## Work unit

Audit the complete `allocateSynthVoice` voice-table indexing idiom in
`RecompiledFuncs/funcs_21.c`. The table records use a 0x17C stride derived as
`(((index * 95) - index) << 2)`.

## Competing hypotheses and discriminator

- H-AllocatorBounded: every table index is a slot-count-bounded scan counter.
- H-AllocatorUnsafe: a writer or candidate path can publish an invalid index.
- H-AllocatorMisread: the 0x17C-stride object is not the voice table.

The discriminator is complete enumeration of every stride calculation and
candidate selection in `allocateSynthVoice`, followed through its loop bounds,
sentinel tests, and per-slot limit checks.

## Evidence

The function reads the slot count from `0x80141AD0`, initializes scan counters
to zero, advances the table base by 0x17C, and repeats only while the counter is
less than that count. The two preferred-candidate scans select `t2`/`t3` only
from those bounded counters and reject `-1` before dereferencing the selected
record. The fallback scan repeats the same slot-count bound and rejects `-1`.
The returned candidate is additionally checked against the candidate record's
`-0x2752` limit before return. The source contains no other 0x17C table-index
path in this function.

## Result

H-AllocatorBounded is selected for this idiom. H-AllocatorUnsafe has no
concrete writer/value in the audited class, and H-AllocatorMisread is not
supported: the same stride, slot-count loop, per-slot fields, and candidate
return path form one coherent table implementation. This is static evidence;
runtime allocator/lifetime legitimacy remains open. No mitigation or guard was
added.
