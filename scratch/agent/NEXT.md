# NEXT: M4 per-object matrix validity (offline) then downstream split
HYPOTHESIS-ID: m4-vge-store-boundary-ground-truth

RESUME: s4631: projection matrix 0x700000..3C equals retail (24 retail samples vs
6 port reads, 1 value, controls passed). Per-object matrices 0x700040+ animate in
retail (35-67 distinct values) and differ from port; cross-run equality invalid.

Hypotheses:
- H-matrix-compose: port per-object matrices are non-rigid/garbage.
- H-no-diff: port matrices are valid rigid transforms; divergence is downstream
  (clipping / RDP).

Discriminator (offline; data in scratch/agent/s4631_m4_matrix_span/port.log
`[m4-mat]` and oracle_arm2-4.log pk: rows): decode 16 words as interleaved
int/frac 4x4, check row norms, orthogonality, translation range. Positive control:
the projection block (0x700000) must decode sensibly. Non-rigid => oracle write
watch on 0x700040 for PC attribution; rigid => RDP triangle stream compare.
Use absolute paths and git -C (cwd drifts; relative script paths give rc=127).
