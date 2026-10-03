# M5 session 3824 — family route/object identity join

The Debug target rebuilt successfully. The first image-only launch used the
wrong working-directory recipe and remained at VI 640; it is coverage-invalid.
The fixed launch used the validated paired-route environment from the repository
root and reached title VI `1024 @ 0x00790400` at 13.4s and hangar VI
`512 @ 0x006AB400`, with no crash or abort.

All six family edge/store positive controls fired. The clear-witness control
identified `0x801797B0` with length `0x298`, and the route snapshot was active
in target rows (`ordinal=640`, `row=0`, `arm=factor5_ucode_b`). The qualified
source-DMA rows still read `0x1798B0 -> DMEM 0xCB0` with `FNV=0x762B22A5` and
zero nonzero bytes.

The family census produced 1,280 target-phase store rows: 768 title and 512
hangar, covering S=512, I=256, and L=512. Every row had `target=0`,
`clear_exact=0`, and `clear_span=0`. The 257 family-entry rows (129 title,
128 hangar; S=128, I=1, L=128) all had `target_arg=0`. Thus the family calls
and stores are real and phase-qualified, but they write alternate objects
instead of the clear-associated source object.

This selects H2 at the measured scope and refutes H1's aliasing explanation.
It does not identify whether the alternate objects are the intended route
state, nor why their output does not reach the cleared source object.

Evidence: `scratch/agent/s3824_m5_family_route_object_join_fixed/run.log`.
