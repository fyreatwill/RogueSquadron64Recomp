# NEXT: close the M4 upstream-operand boundary with a provenance reconstruction
HYPOTHESIS-ID: m4-accumulator-source

Use the already qualified hangar capture, not a new mitigation. Competing
hypotheses:

- H1: the remaining M4 mismatch is caused by the port's dynamic per-object
  matrix/operand source before VMADH.
- H2: the paired vertex input is the source despite the sampled DMA blocks
  matching retail.
- H3: the RSP arithmetic/store path is still wrong even with matching inputs.

Discriminating measurement: run the positive-control reconstruction in
`scratch/agent/m4_reconstruct.py` over the complete s4626/s4628 accumulator
capture, then join its stage-10 operand rows to the s4630/s4631 matrix-span
rows by task, phase, and lane. H1 predicts a nonzero port-vs-retail matrix or
operand difference before VMADH; H2 predicts a vertex-input difference with
matching matrix rows; H3 predicts identical paired inputs but a reconstructed
post-VMADH mismatch. The synthetic controls must print PASS before any null is
accepted.

Exact commands:

1. `python3 scratch/agent/m4_reconstruct.py <qualified-s4626-capture>` and
   retain stdout in `scratch/agent/s4649_m4_reconstruct.log`.
2. Use the existing s4630/s4631 capture tables to produce one joined ledger;
   do not compare animated rows across separate runs.
3. If no complete join exists, stop and record the missing key rather than
   adding another diagnostic field; the next choice is a retail-reference
   request or closing M4 as unevaluable.
