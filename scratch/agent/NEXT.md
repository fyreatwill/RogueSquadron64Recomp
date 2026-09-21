# Next: exact-store join for the primary pre-selector writer

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3668 passed whole-RDRAM, descriptor, title, hangar, and type-2 task
controls. Smaller source-writer context joined title task data
`0x80173B20` and hangar task data `0x80173CB0`, but the join was latest-task
per VI bucket and did not cover primary `0x800078EC` or alternate objects
`0x80171CE0`/`0x80171E70`.

Next unit: add one bounded retail oracle instrument that records the GPR/field
context at each exact `0x800078EC` store into
`0x1797B0..0x179930`, then joins that store ordinal to the next selector and
task object. Keep whole-RDRAM, all four descriptor watches, selector watches,
task dump, and title/hangar phase controls in the same run. Do not use the
unbounded `--pc-field-dump 0x800078EC` arm.

Discriminator:

- H-PrimaryObjectWriter: exact stores carry context that identifies the next
  selected object or a stable object-specific payload contract.
- H-PrimaryInitialization: exact stores have invariant setup context and do
  not distinguish selected objects.
- H-PrimarySeparateObjects: exact-store context changes in step with the
  alternating `0x80171E70`/`0x80173CB0` hangar objects.
- H-CaptureInvalid: whole-RDRAM, title, or hangar control fails; discard the
  capture.

Before building the instrument, read `tools/oracle/README.md` and
`docs/F5-UCODE-REFERENCE.md`. Build once with `bash tools/oracle/build.sh`,
run the single 55-second capture from `build/`, and store the log under
`scratch/agent/` with a non-dot final path component. A mitigation or guest
state rewrite is out of scope.
