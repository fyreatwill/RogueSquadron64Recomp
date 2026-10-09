# Next work unit (s4319): qualify the missing MORT/voice witnesses

HYPOTHESIS-ID: m5-step9-mort-boundary

State (s4318): the Rice-backed retail oracle and both port arms passed whole-
RDRAM/title/hangar/route controls. The real-image arm emitted nonzero PCM and
the silent arm did not. Task/DMA, slot, route, and PCM source/consumer rows were
present, but neither arm emitted MORT descriptor-entry/payload rows or real
filter rows. The previous invalid verdict was a driver omission of
`ROGUESQ_LOG_M5_ROUTE_TRANSITION`, fixed and rerun in the same iteration.

Competing hypotheses:

- H-MORT: the MORT descriptor/decode/output boundary is the remaining owner,
  but the current witness is not attached to the active call path.
- H-AI: MORT/guest PCM is valid and the defect is at AI/SDL or PCM consumer;
  the missing descriptor witness is instrumentation coverage, not behavior.
- H-route: the selected task/voice path never reaches the intended descriptor
  or filter callsites; current PCM rows belong to a different route.

Discriminator: one build/run with both `ROGUESQ_AUDIO_UCODE=0` and `=1` arms,
phase-gated at VI 1024 (`0x00790400`) and VI 512 (`0x006AB400`), adding the
missing MORT descriptor-entry/payload and voice/filter callsite witnesses plus
one positive control for each witness. Keep the existing oracle whole-RDRAM,
title, hangar, host, route, task/DMA, slot, and PCM controls. A same-phase
descriptor/payload witness with nonzero source but divergent output selects
H-MORT; matching descriptor/source/output with consumer or byte-count
divergence selects H-AI; absent descriptor/filter witnesses despite all route
controls selects H-route and requires tracing the actual callsite before any
decoder/AI change. No mitigation or decoder change is authorized.

Exact preparation/checks:

`rg -n "init-voice-sample|init-desc|filter-voice-audit|MORT|pcm-boundary|ROGUESQ_LOG_INIT_VOICE_SAMPLE" src lib tools scratch/agent --glob '!*.log'`

Use the fixed driver `scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh`
with `ROGUESQ_LOG_M5_ROUTE_TRANSITION=1`; batch both audio arms in one run and
store the bounded result under `scratch/agent/s4319_m5_step9_witnesses`.
