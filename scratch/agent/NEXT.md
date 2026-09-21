# Next: identify payload writer and DMA ordering after selector interleave

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3666 passed whole-RDRAM, descriptor, title, and hangar controls. The
selector publication immediately preceding each task row matched its task data
pointer exactly, including both alternating hangar objects. The dominant writer
caller remained `prev_pc=0x80090DE0`, `$ra=0x80090ABC`; the minor
`$ra=0x80090BB4` variant remains non-separating.

Next unit: run one phase-gated oracle capture that joins source-byte writes or
DMA events, selector publication (`0x80091060`/`0x80091074`), task submission
(`0x80033FCC`), and the shared writer (`0x80090DE4`) for both hangar origins.
Use the existing source descriptor watches and positive controls; do not infer
payload ownership from the selector pointer alone.

Discriminator:

- H-PayloadBeforeSelector: source bytes are written before selector publication
  for each object, so the selector only exposes an already-complete payload.
- H-DmaAfterSelector: source DMA/write activity follows selector publication and
  task selection, making ordering the active divergence.
- H-SeparatePayloadWriter: source writer or DMA identity changes with the
  selected object despite the shared `0x80090DE0` caller.
- H-CaptureInvalid: any whole-RDRAM, title, or hangar control fails; discard
  the census.

The discriminator is the relative order and identity of source writes/DMA,
selector publication, and task rows. A missing whole-RDRAM, title, or hangar
control is H-CaptureInvalid and makes the run unevaluable.

Build: `bash tools/oracle/build.sh`. Run from `build/` for one finite
phase-gated capture with all controls and explicit `--watch-pc` arms. Capture
the result under `scratch/agent/` with a non-dot final path component.
