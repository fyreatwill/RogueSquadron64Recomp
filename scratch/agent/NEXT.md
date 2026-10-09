# Next work unit (s4455): port-side rate of musyxMixActiveVoices vs retail

HYPOTHESIS-ID: m5-ai-event-cadence

Retail (s4454): musyxMixActiveVoices inner loops run 45,700x/20 s (2,285/s) pre-title; cmdlist-build loop 23,900x/20 s. Control passed.
Work: add (via a tools/apply_*.py fixup, not hand-edit) a per-call counter in musyxMixActiveVoices and musyxBuildVoiceCommandList, logged per second under ROGUESQ_LOG_M5_CMDLIST; run port ~20 s pre-title with ROGUESQ_AI_EVENT_DRAIN armed and unarmed (one build, concurrent arms).
Outcomes: port calls/s << retail => port under-drives the mixer (find the gate upstream); similar => voice-array base/contents differ (retail s0=0x801496a0 at 0x8009189c, a0=0x80165fc0).
