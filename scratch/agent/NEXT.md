# NEXT: locate the M4 operand source (v0/v4) feeding stage 10
HYPOTHESIS-ID: m4-vge-store-boundary-ground-truth

RESUME: s4628 refuted the store arm on the port (488/488 rows: DMEM record
bytes == post-VGE v6 lanes 0-2,4-6). s4626: VMADH matches 4,128/4,128 lanes.
Surviving hypotheses: H-vge (VGE semantics differ on 31 lanes) and H-source
(operands v0/v4 differ upstream).

Competing hypotheses:
- H-vge: given identical v0/v4/v29 inputs retail would give different VGE out.
- H-source: inputs differ; the load that fills v0/v4 reads different RDRAM.
- H-instrument-boundary: no RDRAM-visible source address can be named.

Discriminator: from the stage-10 rows find the DMA/lqv source address that
fills v0/v4 (record base r9 + the DMEM->RDRAM origin of the vertex block),
log that RDRAM span in the port at stage 10, and read the same physical span
via the oracle at hangar VI 512 with whole-RDRAM control. Equal spans =>
H-vge (then write an RSP VGE unit test against known vectors); different =>
H-source (trace the writer).
Reuse scratch/agent/s4628_m4_dmem_store/run.sh for the port arm; retail arm:
Rice oracle with verified Start schedule (see s4627 artifacts).
