# M5 session 4682 — AI/SDL boundary qualification

The independent retail run passed the whole-RDRAM positive control at 10,000
callbacks and reached the 512-wide hangar family (`0x006AB800` in this
recipe). Its AI duty samples were nonzero in the title and hangar buckets.
This is independent route/audio evidence, but not an exact `0x006AB400`
retail-origin match.

The rebuilt port ran image and silent arms concurrently from one binary. Both
arms reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`; both
had 0 crash and 0 abort markers. The image arm's target-phase rows showed
nonzero data at `ai-output`, `pcm-boundary-source`, and
`pcm-boundary-consumer`. For the same sampled buffers, source and consumer
FNV/nonzero counts matched (for example hangar `0x80168250` had FNV
`0xF1097DB8`, `nz=741` at both boundaries). The SDL host rows showed
`pcm_bytes=768`, `samples=384`, `device=2`, and the expected queue growth.
The silent arm reached the same boundaries with the known zero-output FNV
`0xF59C39C5` and `nz=0`, while still exercising the queue path.

Counts across the complete logs were image/silent respectively: phases
139/141, `m5-ai-state` 67/67, `ai-output` 55/55,
`pcm-boundary-source` 90/91, `pcm-boundary-consumer` 305/306, and
`m5-audio-host` 1094/1096. The phase-gated source-to-consumer match and the
same-run silent control select H-AI-bridge-valid. No AI status, PCM
conversion, or SDL queue change is authorized by this result.

ORIGIN: diagnostic-only retail oracle and existing port boundary probes; no
guest or host behavior was rewritten.

Evidence: `scratch/agent/s4682_m5_ai_sdl_boundary/retail.log`,
`image-results.txt`, and `silent-results.txt`.
