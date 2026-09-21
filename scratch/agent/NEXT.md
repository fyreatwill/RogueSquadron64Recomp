# Next: identify the selector that interleaves hangar task objects

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3665's corrected execution-watch capture passed whole-RDRAM, all four
descriptor, title, and hangar controls. Title reproduced s3664's origin split,
but each hangar origin interleaved `0x80171E70` and `0x80173CB0` task objects.
The dominant writer caller remained `prev_pc=0x80090DE0`, `$ra=0x80090ABC`,
with a minor `$ra=0x80090BB4` variant on hangar rows.

Next unit: use one new phase-gated oracle capture to join the task object's
selector/source field before `0x80033FCC` to each hangar task row. Keep the
same positive controls and explicit `--watch-pc 0x80033FCC,0x80090DE4`; add the
smallest existing selector watch that distinguishes `0x80171E70` from
`0x80173CB0` (the prior selector table is `0x80149758/0x8014975C`). Capture
both 512 origins and retain `$ra` in the join. Do not infer ownership from
the shared caller alone.

Discriminator:

- H-SelectorInterleave: selector/source field changes before alternating
  `0x80171E70`/`0x80173CB0` rows while caller identity stays stable.
- H-SeparateProducer: selector/source field and writer caller change together.
- H-SharedProducerWithTwoObjects: selector remains stable while the object
  pointer alternates, indicating downstream double-buffer/object selection.
- H-CaptureInvalid: any whole-RDRAM, title, or hangar control fails; discard
  the census.

Build: `bash tools/oracle/build.sh`. Run from `build/` for 55 seconds with the
s3665 fixed route, controls, phase buckets, task join, and selector watch.
Capture to `scratch/agent/s3666_m5_hangar_selector_join/`; use the built-in
finite lifetime so the shutdown summary is retained.
