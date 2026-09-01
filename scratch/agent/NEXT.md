# NEXT work unit — trace `voice_record+0x64` writers

HYPOTHESIS-ID: m3-stop-voices-handle-provenance

M5 exact DMA ordering remains unresolved and unavailable to the current
retail oracle. Do not repeat the source-buffer watch or add another DMA
counter. Session 3585 completed the `stopVoicesByHandle` consumer audit:
the node/layout interpretation is consistent, but `node+0xC` comes from
`voice_record+0x64` and is used as a voice-table index without a local bound
check.

Next work unit: complete the static writer/lifecycle audit for
`voice_record+0x64`, covering every generated read/write site and every
producer of the voice-record base. No game build or runtime instrument is
authorized unless the static audit identifies a concrete, ground-truthable
writer boundary.

Competing hypotheses and the discriminator:

- H-VoiceIndexBounded: all writers establish `-1 <= voice_record+0x64 < 32`
  before a live handle node copies it.
- H-VoiceIndexUnsafe: a concrete writer can publish a value outside the
  32-record range while the node remains reachable by a consumer.
- H-VoiceRecordMisread: `+0x64` is not the slot index or the table is not the
  32-record `0x17C` array identified by the companion map.

Discriminator: enumerate every `+0x64` writer and every base-producing call
edge, classify each value range and invalidation path, and reconcile the
result with `allocVoiceHandleNode`, `freeSynthVoiceFromActiveList`, and the
four `stopVoicesByHandle` edges. Select unsafe only with a concrete writer
and value; select bounded only when every writer is covered; otherwise leave
the boundary unclassified. No guard is authorized without an ORIGIN naming
the legitimate writer and assessing the value.

Exact checks:

    rg -n -i '0x64|0X64|allocVoiceHandleNode|freeSynthVoiceFromActiveList|stopVoicesByHandle' ../N64Recomp/RecompiledFuncs ../rogue_squadron64
    rg -n 'RECOMP_FUNC void ' ../N64Recomp/RecompiledFuncs/funcs_21.c | head -80
    sed -n '4700,4940p' ../N64Recomp/RecompiledFuncs/funcs_21.c
    sed -n '7780,8060p' ../N64Recomp/RecompiledFuncs/funcs_23.c

Record the result in a new `docs/M3-S3586-VOICE-INDEX-WRITERS.md`, update
`docs/CURRENT-TRUTH.md` and `PORTING-STATE.md`, then set the iteration outcome.
