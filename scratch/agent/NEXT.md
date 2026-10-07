# Next work unit: qualify the M5 image contract after route closure

HYPOTHESIS-ID: m5-image-contract-qualification

Competing hypotheses and discriminator written before the next build:

- H-declared-contract: declared and legacy image arms reach the same task/SP,
  service, status/slot, and PCM joins; staging size is not the missing edge.
- H-legacy-contract: only the legacy image arm closes a downstream join or
  avoids a phase-scoped task/service failure.
- H-image-output-gap: both image arms complete the task chain but neither
  produces the expected downstream PCM/slot transition.
- H-control-invalid: if retail whole-RDRAM/title/hangar controls or either
  image target phase fails, the corresponding downstream null is unevaluable.

The single discriminating measurement is one same-build, retail-grounded,
phase-gated declared-versus-legacy image matrix. Record task exit/SP
completion, service return, status `01/02/00` and `03`, slot/reap activity,
PCM source/consumer joins, and target VIs for both image arms. The retail
whole-RDRAM/title/hangar controls must pass; a missing target phase makes that
arm unevaluable. Silent is retained only as the route control established in
this iteration.

ORIGIN: the staging writer is the host audio-task DMA setup, which copies the
OSTask `ucode_data_size`; `0x800` is the declared task field and `0xF80` is
the legacy compatibility span. Neither value is treated as a guest payload
writer or as permission to add a skip/guard.

Next iteration: build the batched declared-versus-legacy image contract
matrix and select the first downstream divergence, if any.
