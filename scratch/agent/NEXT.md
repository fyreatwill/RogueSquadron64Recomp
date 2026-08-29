# NEXT work unit — port/retail target framebuffer parity

HYPOTHESIS-ID: m5-port-retail-framebuffer-parity

Session 3234 established the retail target context at route origin
`0x00790A00`: valid frame base `0x00790000`, candidates
`0x00790400/0x00790800`. The route `$a0=0x8014090E` is not a framebuffer.

## Competing hypotheses

- `H-PortMatchesRetail`: the port selects the retail target candidate
  `0x00790400`; the remaining defect is downstream of origin selection.
- `H-PortOriginSelection`: the port selects a different target framebuffer.
- `H-PortAudioBoundary`: the port reaches a different target boundary because
  audio/task progress diverges before the VI commit.

## Discriminator

Run the existing same-build silent/image phase-gated pair in one iteration,
with the image and silent arms built together. Require both arms' dispatch,
DMEM, DMA, `Broke`/SP completion, service, slot, PCM, and VI-commit rows.
An image-arm port commit of `0x00790400` at the matching target phase selects
`H-PortMatchesRetail`; a valid different commit selects
`H-PortOriginSelection`; missing target progress or missing audio joins with
the established dispatch control selects `H-PortAudioBoundary` only if its
phase gate and controls pass. A failed phase join is unevaluable, not a null.

## Exact command

Use the existing qualified pair driver:

`bash scratch/agent/s2972_m5_step1_qualified_route/run_pair.sh`

Before running, add one phase-gated port VI-commit field for target candidate
`0x00790400` to that driver's existing batch instrumentation; do not add a
route-`$a0` framebuffer interpretation. Capture results under a new
`scratch/agent/s3235_m5_port_retail_framebuffer_parity/` directory and retain
the silent arm as the no-write control.
