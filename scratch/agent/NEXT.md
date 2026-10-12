# NEXT: locate the M4 operand source (v0/v4, pre-VMADH accumulator)
HYPOTHESIS-ID: m4-vge-store-boundary-ground-truth

RESUME: s4626 VMADH 4,128/4,128; s4628 store clean; s4629 VGE is pure
max(x,0) (29/4112 lanes clamp negatives). Only H-source survives:
- H-source: v0/v4 (and pre-VMADH acc) differ from retail because the vertex
  block loaded into DMEM differs (RDRAM content or DMA source).
- H-instrument-boundary: no RDRAM-visible address can be named for the rows.

Discriminator: in the port at stage 10 log the DMA/lqv RDRAM source address
(and 64 bytes of it) that fills v0/v4 for the record at base r9; read the same
physical span via the Rice oracle at hangar VI 512 (whole-RDRAM control must
fire ~10k). Equal => operands equal, divergence is in the preceding ucode
step (trace the earlier ops, not RDRAM); different => trace the RDRAM writer.
Reuse scratch/agent/s4628_m4_dmem_store/run.sh (port arm) and the s4627
oracle artifacts (retail arm). Batch the log field in ONE build.
Must land a code change (probe field) - diagnostic-only churn trips the gate.
NOTE: run git from the repo root (cwd drifts into lib/ after cd; use absolute paths).
