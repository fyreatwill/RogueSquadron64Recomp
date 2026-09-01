# NEXT work unit — audit the next M3 unchecked audio-table address

HYPOTHESIS-ID: m3-audio-table-address-audit

Session 3588 completed the `-0x271C` packed voice-handle writer census. All
three stores were classified: cleanup/reset write `-1`, and
`startNoteOnVoice` writes the composite handle after successful allocator
selection. Low-byte consumers were enumerated; no concrete invalid writer was
found. Do not repeat this class or add a guard.

Next work unit: audit the complete generated audio path that computes a table
address from voice-record fields `0x4E/0x4F` in `refreshVoicePlaybackRate` and
any same-idiom consumers. Enumerate every writer of those fields and every
record/table base edge; land a guard only if a concrete invalid writer is
identified.

Competing hypotheses and the discriminator:

- H-AudioRecordFieldsBounded: fields `0x4E/0x4F` stay within the table's
  intended dimensions at every writer.
- H-AudioRecordFieldsUnsafe: a concrete writer can publish an invalid field
  value used in the computed address.
- H-AudioRecordFieldsMisread: the apparent fields or table layout are
  misidentified.

Discriminator: enumerate every writer of `0x4E/0x4F`, every computed-address
consumer in the idiom, and the range checks or loop bounds on each edge. Select
unsafe only with a concrete writer and value; select bounded only when every
writer and base edge is covered; otherwise leave the boundary unclassified.
No guard is authorized without an ORIGIN naming the legitimate writer and
assessing the value.

Exact checks:

    rg -n '0x4E|0x4F|-0x7C30|refreshVoicePlaybackRate' ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c
    rg -n 'sw .* -0x26C[45]|sw .* -0x272[789A]' ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c
