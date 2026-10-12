# NEXT: RESUME M4 upstream-operand provenance reconstruction
HYPOTHESIS-ID: m4-accumulator-source

The prior attempt was a checkpoint close-out before the reconstruction ran.
No qualified result, joined ledger, or discriminator exists yet. Do not add
instrumentation or rerun a game capture.

Competing hypotheses:

- H1: the remaining M4 mismatch is caused by the port's dynamic per-object
  matrix/operand source before VMADH.
- H2: the paired vertex input is the source despite sampled DMA blocks matching
  retail.
- H3: the RSP arithmetic/store path is still wrong with matching inputs.

Discriminating measurement: run the positive-control reconstruction over the
complete s4626 accumulator capture, then join stage-10 operands to the
s4630/s4631 matrix-span rows by task, phase, and lane. H1 requires a nonzero
port-vs-retail matrix/operand difference before VMADH; H2 requires a vertex
input difference with matching matrix rows; H3 requires identical paired
inputs but a reconstructed post-VMADH mismatch. Synthetic controls must print
PASS before accepting any null.

Resume command:

`python3 scratch/agent/m4_reconstruct.py scratch/agent/s4626_m4_accumulator_boundary_fixed/port.log > scratch/agent/s4649_m4_reconstruct.log 2>&1`

Then build one joined ledger from the existing s4630/s4631 tables. If no
complete join key exists, record the missing key and choose a retail-reference
request or close M4 as unevaluable; do not add another diagnostic field.
