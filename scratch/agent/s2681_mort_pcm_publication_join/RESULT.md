# Session 2681 — M5 renderer-to-AI publication join

Command: see the invocation recorded in `NEXT.md` for Session 2681; the run
was captured in `run.log` using the corrected retail core and Rice video.

The whole-RDRAM positive control fired 84,777 writes. The driven retail route
reached both hangar VI origins (`0x006AB400` and `0x006AB800`) at width 512.
The named execution controls were live: `renderVoiceAudioBlock` (496),
`audioMixStereoBlock8` (1,984), `osAiSetNextBuffer` (6,153), and
`__osAiDeviceBusy` (6,153).

The candidate AI-source span `0x166450:0x169450` had 12,288 writes and 3,072
reads. Its only phase-independent writer histogram entry was the known
initialization `0x800078EC`; no renderer writer was found there. The broader
renderer/AI-adjacent span `0x1B4A00:0x1B5000` had 62,489 writes and 939,523
reads. Its hangar-phase writer histogram included `0x8009DB2C` (renderer,
9,712 total phase samples), plus the AI-side `0x8002A0B8..0x8002A0D8`
sequence (53 samples each). The post-store samples at those AI-side PCs were
all zero; renderer post-store samples were nonzero.

Result: for these candidate spans, the retail renderer writes a live nonzero
stream in the adjacent span, but the AI source is a distinct span with no
named renderer writer. This selects `H-AI-source-gap` at the measured
candidate boundary and rejects `H-MORT-PCM` for those ranges. It does not
establish the complete source/order edge and does not select `H-Host-only-gap`.
This is single-source evidence from the retail oracle; no port behavior was
changed and no writeback/remap is authorized.
