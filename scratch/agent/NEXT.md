# Next work unit (s4433): who calls reapplyAudioConfig/osAiSetFrequency (0x80091CB8 -> 0x80029E78) in the port's TITLE phase, and does retail really lack it?

HYPOTHESIS-ID: m5-title-reapply-config

s4432 closed m5-audio-loop-submit: port loop submits at 0x8008EE84 in title (shim call, so no guest PC 0x80029E80).
Hypotheses:
- H-port-extra-call: port title calls reapplyAudioConfig (state/flag differs, e.g. frequency contract or byte 0x801596F0 / config-changed flag).
- H-retail-window-miss: retail title does call it but outside the s4414 capture window/ranges.
- H-witness-artifact: port's "exact 0x80029E78" witness fires on a host/shim path for osAiSetFrequency, not a guest arrival.
Discriminator (one build, one run per arm): port witness at generated callsite 0x80091CB8 with ra/s-regs/config flag, phase-gated; retail tools/oracle execution watch on 0x80091CB8 AND 0x80029D20 over title+hangar with whole-RDRAM control. First find how s4416's 0x80029E78 witness is implemented (not in src/main/upstream_compat.cpp; check lib/ and tools/apply_*).
Port runs: scratch/agent/s4432_port/run.sh; ~2/3 die pre-title (phase-3 corruption family), retry.
