# Next work unit: locate the M5 image zero-payload boundary

HYPOTHESIS-ID: m5-image-zero-payload-origin

Competing hypotheses and discriminator written before the next build:

- H-preimage-zero: the image input/DMEM payload is already zero before the
  Factor 5 transform.
- H-transform-zero: the input is live but the stage-2/3 transform emits zero.
- H-writeback-zero: stage output is nonzero but the destination writeback is
  lost or zeroed before PCM consumers see it.
- H-control-invalid: if retail whole-RDRAM/title/hangar controls or either
  image target phase fails, the corresponding downstream null is unevaluable.

The single discriminating measurement is one same-build, retail-grounded,
phase-gated source/transform matrix for declared and legacy image arms. Record
the input DMEM snapshot, stage-2 output, stage-3 output, destination writeback,
and PCM source/consumer joins in one table, retaining task, SP, service,
status/slot, and VI controls. A zero input selects H-preimage-zero; nonzero
input followed by zero stage output selects H-transform-zero; nonzero stage
output followed by zero destination/PCM selects H-writeback-zero. Retail
whole-RDRAM/title/hangar and both port image target VIs are mandatory positive
controls; a missing phase makes that arm unevaluable. Silent is retained only
as the route control.

ORIGIN: the candidate values are legitimate image input, transform, and
writeback payloads; the host staging writer already proved that `0x800` versus
`0xF80` is not the sufficient contract divergence. No skip, force-clear, or
guest behavior change is authorized.

Next iteration: first ask retail ground truth for the physical image input and
destination ranges, then build the batched declared-versus-legacy
source/transform matrix and select the first zero boundary.
