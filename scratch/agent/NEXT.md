# NEXT: RDP triangle stream compare at hangar entry
HYPOTHESIS-ID: m4-vge-store-boundary-ground-truth

RESUME: s4632: port M4 operands (projection, vertices s4630, per-object matrices) are
valid and the first matrix equals retail. Divergence is downstream.

Hypotheses:
- H-clip: clipping/vertex-output stage differs (screen coords or clip flags).
- H-rdp: RDP triangle commands reaching the RDP differ in count/shape from retail.
- H-render: commands equal; difference is in the renderer (Rice/GLideN64/Metal).

Discriminator: dump the first N RDP triangle commands (0x08-0x0F) of the first hangar
frame, port vs oracle (gliden64/rice plugin log), decode screen-space vertices and
compare counts. Positive control: the title phase must show triangle commands in both.
Use absolute paths and git -C. tools/m4_matrix_decode.py exists for the matrix side.
