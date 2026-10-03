# M5 session 3750 — route-state hook was not an exact-field read

The paired qualified port run enabled the existing generated `osRecvMesg`
caller census, route-preparation hook, and source-DMA census in real-audio and
silent arms. Both arms passed source-hook controls and reached title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. The real arm emitted the
expected target source-DMA family; the silent arm emitted no matching
`0x1798B0 -> DMEM 0xCB0` rows.

The proposed read/use measurement was not valid. Static disassembly shows
`0x80019CD8` is `lw a0,0x10(sp)` after the queue receive, not a load from the
route fields. The runtime census agrees: target-phase route rows had
`a0=0x80128C70/0x80128C80`, but sampled `s0` was zero and the logged
`source_word/source_byte` were therefore not reads of `0x128CD0/0x128C92`.
The 256-row per-arm frequency-caller cap fired, so this is an instrument
mis-target, not a null result.

Static candidate enumeration found bounded exact-offset load sites that must
be filtered by runtime base pointer before the next build: `0x800A5E00`
(`lbu 0x22(a0)`), `0x800B4B08` (`lhu 0x22(a0)`), and the `0x60(a0)` loads at
`0x80065854`, `0x8007BEEC`, `0x8008F548`, `0x8008F5F0`, `0x8008F640`,
`0x800D989C`, and `0x800E8064`. This is a candidate list, not proof that any
site reads the target object.

ORIGIN: diagnostic-only hook mis-target; no value was suppressed and the
legitimate `0x800078EC` zero fill was unchanged.

Evidence: `scratch/agent/s3750_m5_route_state_source_join/{real,silent}.log`
and the generated disassembly under
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs.s3549-partial/`.
