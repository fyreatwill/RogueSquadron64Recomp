# s4649 M4 reconstruction/join

The positive-control reconstruction in `s4649_m4_reconstruct.log` passes both
synthetic cases. After grouping the s4626 accumulator rows by `(task, phase,
r9)`, it forms 515 complete stage-10/11/12 triplets and 4,120 lanes. The
reconstructed post-VMADH value matches stage 11 in every lane; no lane
saturates.

The requested join to the s4630/s4631 operand tables is not available. The
s4626 capture has stage-10 tasks in the 65–658 range, while the separate s4631
matrix capture has task IDs 1155–1165. There is no shared frame/object/lane
key, and the matrix span is animated between runs. The s4631 compare controls
pass (200 whole-RDRAM control hits per arm); it reports one stable 0x700000
block and dynamic 0x700040+ blocks, but those rows cannot be attributed to
the s4626 triplets.

Therefore H3 (arithmetic mismatch with identical captured inputs) is refuted
for the port by the reconstruction. H2 remains disfavoured by the independent
s4630 vertex comparison, but H1 (dynamic matrix/operand source) is
unevaluable from these captures. No runtime mitigation is justified.
