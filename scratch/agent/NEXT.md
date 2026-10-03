# Next work unit: qualify one named M5 image task/output contract edge

HYPOTHESIS-ID: m5-image-task-output-contract-edge

The alternate-family ownership thread is closed at the measured scope by
s3835: retail reached both target phases and the S/L family PCs, but had zero
reads/writes in physical `0x165000..0x16C000`; the port emitted 1,280
target-phase alternate-family stores. Do not repeat that watch.

Competing hypotheses and discriminator:

- H1: the image task contract is complete and the remaining gap is downstream
  guest service/PCM. Retail and port task-field, image completion, service,
  and PCM rows align at title 1024 and hangar 512, but the port still lacks
  the retail downstream result.
- H2: a specific image task/output edge is missing in the port. One named
  task-field/DMEM-DMA/output/completion row differs between retail and port,
  and the mismatch precedes the first downstream divergence.
- H3: the apparent edge is a measurement boundary. Retail and port rows are
  not phase- or task-joined, or a positive control is absent; no contract
  change is authorized.

The discriminator is one phase-gated paired capture containing the existing
whole-RDRAM oracle control, both target VIs, retail task-field dumps, and the
port dispatch/task-field/DMEM-DMA/SP-completion/service/PCM rows in the same
task-generation table. H1 requires complete task-field parity plus a
downstream-only divergence; H2 requires one concrete pre-divergence mismatch;
H3 is selected by any missing positive control or missing task join.

Before building, run:

    sed -n '1,220p' docs/M5-AUDIO-PLAN.md
    rg -n 'pc-task-dump|audtask-abi|audtask-dma|task-generation|PCM' src tools scratch/agent docs | head -120

Then use the smallest existing validated paired capture recipe, adding only
the task-field join required by the chosen edge. Build one Debug image with
all arms, run from `build/`, phase-gate on title `0x00790400`/1024 and hangar
`0x006AB400`/512, and kill all processes with SIGKILL. Reject nulls unless
the whole-RDRAM control and both phase controls are positive.
