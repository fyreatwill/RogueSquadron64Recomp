# NEXT: G3c(b) knife spikes - reference RSP check of the F5 clip path
HYPOTHESIS-ID: g3c-owner-visual-b
G3c(a) height-fade closed s6365 (f live, jump_med unchanged). Remaining (a) leads (haze scaling) low value after s6311-s6359 nulls.
Hypotheses: H-rsp-emu (our LLE RSP differs from hardware on VRCP/VRCPH/VRCPL, VMULF/VMACF, VCH/VCL/VCR), H-retail (retail emits the wedges too).
Work unit: take a logged wedge's RSP input (use existing ROGUESQ spike log from G3b), replay the vertex/clip microcode ops in an independent reference (ares/cen64/parallel-rsp if installed, else a small python model of the vector ops) and compare output vertices. Positive control: a known-good vertex must match.
