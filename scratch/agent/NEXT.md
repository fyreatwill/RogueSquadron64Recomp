# NEXT: G3c(b) knife spikes — reference-RSP check of the F5 clip path
HYPOTHESIS-ID: g3c-owner-visual

Closed: red-VTX thread (s6350). Remaining G3c items: (a) edge fade (s6311 edgefade work), (b) spikes reopened, (c) shake (s6292 alternation 0.395 retail vs 0.384 wide: no arm difference so far).

Hypotheses for (b): H-rsp-emu (our LLE differs from hardware on VRCP/VRSQ/VCH clip flags), H-retail (retail emits the wedges too).
Discriminator: take one logged wedge triangle's input vertices (spike log from s6085 / ROGUESQ_CULL_SPIKE), run the same vertex transform+clip in a reference (ares/parallel-rsp or hand-model from F5-UCODE-REFERENCE.md); positive control = a known-clipped vertex reproduces. Output differs => fix emulation; matches => ask owner about default-on cull.
