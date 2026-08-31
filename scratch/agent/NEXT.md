# NEXT work unit — qualify M5 Step 1 downstream contract

HYPOTHESIS-ID: m5-downstream-contract

Session 3364 selected `H-PortMatchesRetail`: the qualified port run passed
host/task/PCM, title, and hangar controls and observed the retail-matching
`0x800919EC -> 0x80007910` edge with `$a0=0x8009123C`, plus the known
`0x80007928 -> 0x8009123C` writer. The callback source/target gap is closed;
the remaining M5 Step 1 question is whether the matching edge closes the
downstream service/slot/voice/PCM contract.

Competing hypotheses for the next unit:

- `H-DownstreamContractComplete`: matching callback edges lead to the retail
  service, slot/status, voice, and PCM outcomes.
- `H-PortConsumerIndirectGap`: the matching edge exists, but the port does not
  dispatch the callback-table consumer path.
- `H-PortAudioContractGap`: consumer dispatch exists, but task/slot/voice/PCM
  completion still diverges after the callback edge.

Discriminating measurement: one build/run using the existing phase-gated
consumer-entry, slot/status, voice, PCM source/consumer, task/SP-completion,
title, and hangar markers, while retaining the callback edge as a control. A
complete service-to-PCM row selects `H-DownstreamContractComplete`; matching
callback rows with zero consumer entries selects `H-PortConsumerIndirectGap`;
consumer entries with missing slot/voice/PCM joins selects
`H-PortAudioContractGap`. Any null before title/hangar is unevaluable.

Exact bounded preparation before any build:

```sh
rg -n -C 8 'serviceVoicePoolFrame|0x80019B74|consumer_entry|pcm-boundary' src tools ../N64Recomp/RecompiledFuncs/funcs_*.c
```

Then inspect the existing regeneration-safe consumer markers, add only a
missing join if the complete table cannot be read, build once, and run the
qualified port recipe directly from `build/` for 90 seconds with no injected
input. The prior 45-second attempts stayed in 640 attract; the known valid
s3364 route reached title at 13.7 seconds and hangar at 25.0 seconds. Require
title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` before reading
consumer/PCM nulls. The callback edge and route controls must visibly fire
before any downstream null is interpreted. No behavior change or mitigation.
