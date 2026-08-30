# NEXT work unit — identify the target VI route writer independently

HYPOTHESIS-ID: m5-route-boundary-target-writer

M5 Step 1 is currently route-invalid: retail reaches title/hangar, while the
port image and silent arms stop at pre-title VI 640. Run one independent retail
oracle capture that compares the target framebuffer writer with the port's
observed pre-title route. This is a ground-truth boundary unit; do not change
audio behavior or add another port counter.

## Competing hypotheses

- `H-RetailTargetWriter`: a legitimate retail writer/caller publishes the
  target framebuffer address during title or hangar, with an attributable PC
  and ordered VI transition.
- `H-RetailPreTargetOnly`: the watched writer is live only before the target
  transition, so the missing port target row is upstream of that writer.
- `H-RetailTargetWriteUnavailable`: whole-RDRAM/title/hangar controls pass but
  the selected aligned watch cannot expose the target writer, leaving the
  boundary unresolved rather than absent.

## Discriminator

The same oracle run must pass the whole-RDRAM positive control and reach title
`1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`. Watch the target physical
framebuffer span `0x00790000..0x00790C00`, the pre-title span
`0x00696000..0x00697000`, and the known route callsites
`0x8001BE24,0x8008EB7C,0x8008EC88,0x8008EBC8`. A target-phase write with a
writer PC selects `H-RetailTargetWriter`; valid phases with only pre-target
writes select `H-RetailPreTargetOnly`; missing aligned target rows despite all
controls select `H-RetailTargetWriteUnavailable`.

## Exact command

From the repository root, use the existing bounded target-writer driver:

```sh
zsh scratch/agent/run_s2297_m5_target_only_writer_sequence.sh s3273_m5_route_boundary
```

It arms the whole-RDRAM control, target/pre-target physical spans, phase-gated
PC histograms, and post-value rows in one retail run, then SIGKILLs the oracle
watchdog. Record the positive controls and target-only writer table. Do not
interpret a missing target row unless the controls are present.

## Follow-up selection

If `H-RetailTargetWriter` is selected, compare that writer/order against the
port's `640 @ 0x0066A500` route before authorizing any M5 Step 3 edge. If
`H-RetailPreTargetOnly` or `H-RetailTargetWriteUnavailable` is selected, keep
Step 1 unevaluable and choose the next route-boundary discriminator; do not
infer an audio, gate, slot, or PCM cause.
