# Next: join pre-selector payload writers to selected objects

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3666 passed whole-RDRAM, descriptor, title, and hangar controls. The
selector publication immediately preceding each task row matched its task data
pointer exactly, including both alternating hangar objects. The dominant writer
caller remained `prev_pc=0x80090DE0`, `$ra=0x80090ABC`; the minor
`$ra=0x80090BB4` variant remains non-separating.

Next unit: use one phase-gated oracle capture to join each pre-selector source
writer (`0x8001E2C0`, `0x80007670`, `0x800078EC`, and the smaller sites) to the
selected object/task fields. Keep the source-span watch, selector publication
(`0x80091060`/`0x80091074`), task submission (`0x80033FCC`), shared writer
(`0x80090DE4`), and all four descriptor watches in one run. Add the writer
GPR/field context needed to distinguish initialization from object payload
formation; do not infer object ownership from PC identity alone.

Discriminator:

- H-PreSelectorObjectWriter: a pre-selector source writer's arguments/fields
  identify the selected object or its stable payload contract.
- H-PreSelectorInitialization: all source writes are shared setup with no
  object-specific context; payload ownership remains downstream/unobserved.
- H-SeparatePayloadWriter: source writer context changes with the selected
  object despite the shared `0x80090DE0` caller.
- H-CaptureInvalid: any whole-RDRAM, title, or hangar control fails; discard
  the census.

The discriminator is the writer's pre-selector arguments/pointed fields joined
to the next selector/task object. Object-specific context selects
H-PreSelectorObjectWriter or H-SeparatePayloadWriter; identical setup context
selects H-PreSelectorInitialization. A missing whole-RDRAM, title, or hangar
control is H-CaptureInvalid and makes the run unevaluable.

Build: `bash tools/oracle/build.sh`. Run from `build/` for one 55-second
phase-gated capture with all controls and explicit watches for the four source
writer PCs plus their field/context dumps. Capture under `scratch/agent/` with
a non-dot final path component.
