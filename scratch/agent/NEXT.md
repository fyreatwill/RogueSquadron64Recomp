# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4865 result: port data_size is 1 in 99.9% of stores, identical with ROGUESQ_S4562_PAUSE 0 and 4; per store ~2 counter resets (0x8009106C) but only 1 increment (0x800911DC). Retail ~90% size 2.
Hypotheses: (H1) port's musyxBuildVoiceCommandList takes an early-out path on every other call (guest state differs, e.g. empty voice list/gate); (H2) retail also resets twice but increments twice (cadence ratio differs); (H3) the second synth entry is a separate caller (not the frame-batch build).
Discriminator: oracle exec watches at 0x8009106C and 0x800911DC (physical 0x0009106C/0x000911DC) plus 0x80091784, whole-RDRAM control first; compare reset:incr:store ratios to port 2:1:1. In the port, log the branch taken between 0x8009106C and 0x800911DC in the same helper (rs64_s4864_ev) with the early-out PC.
