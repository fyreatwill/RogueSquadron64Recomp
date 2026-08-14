# NEXT work unit (s928)

HYPOTHESIS-ID: m3-render-voice-audio-class

Audit the complete `renderVoiceAudioBlock` idiom at `0x8009DB44`, including all
generated callers, its voice-record coefficient/state ranges, indirect-call
edges, nested audio helper contracts, and termination.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-render-unclassified: a caller or nested helper uses an unchecked voice
  record, stack/output pointer, indirect target, or unbounded control path.
- H-render-classified: all callers share one fixed render contract, every
  nested helper edge is structurally bounded, and only dynamic value
  legitimacy remains open.
- H-render-shape-mismatch: one caller uses a distinct render contract; record
  the exact split and stop.

Discriminating measurement: enumerate every memory access, indirect/direct
helper edge, caller argument setup, and loop/termination condition in the
generated body and each nested edge; cross-check `main_overlay.txt` and
companion symbols. Any omitted access, unsafe bound, unbounded control, or
shape split rejects full classification.

Exact commands: inspect `funcs_27.c` around `0x8009DB44`, `rg` every
`renderVoiceAudioBlock` reference and nested helper call, then inspect the
matching `main_overlay.txt` entry and each direct nested helper body. No game
build or soak is planned.
