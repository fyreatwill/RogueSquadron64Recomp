# NEXT work unit — audit the next M3 unchecked voice-table consumer

HYPOTHESIS-ID: m3-voice-table-consumer-audit

Session 3586 completed the `voice_record+0x64` writer audit. The field is a
packed handle, not a standalone slot index: `startNoteOnVoice` writes the
allocator-returned slot in the low byte and cleanup/reset paths write `-1`.
No concrete invalid low-byte writer was found. Do not repeat this class or add
a guard.

Next work unit: select the next M3 idiom class from the generated audio path
with an unchecked voice-table index or record-derived address, enumerate the
whole class statically, and land a guard only if a concrete invalid writer is
identified.

Competing hypotheses and the discriminator:

- H-NextConsumerBounded: the next unchecked consumer's index is bounded by its
  producer contract.
- H-NextConsumerUnsafe: a concrete writer can publish an invalid index to the
  next consumer.
- H-NextConsumerMisread: the apparent index or table layout is misidentified.

Discriminator: choose one complete unchecked-index idiom, enumerate every
writer and base-producing edge in that class, and classify the value range at
the consumer. Select unsafe only with a concrete writer and value; select
bounded only when every writer is covered; otherwise leave the boundary
unclassified. No guard is authorized without an ORIGIN naming the legitimate
writer and assessing the value.

Exact checks:

    rg -n 'andi.*0xFF|sll.*17C|D_8013D880|0x17C' ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c
    rg -n 'RECOMP_FUNC void ' ../N64Recomp/RecompiledFuncs/funcs_21.c | head -100
    rg -n 'lw +\$[^,]+, -0x27|sw +\$[^,]+, -0x27' ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c
