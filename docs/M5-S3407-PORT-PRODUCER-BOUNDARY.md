# M5-S3407 port producer-boundary qualification

The fresh build was first run with both arms concurrent; both hit the known
scheduler crash at guest PC `0x8000834c` before a phase gate, so that attempt
was invalid. The fixed same-build qualification ran silent and image arms
sequentially with phase gates and the existing M5 controls.

Both arms passed title 1024 and hangar 512, with no crash or abort markers.
The image arm produced 51 hangar-phase source rows for the target image spans,
including stage 3 DMEM `0xCB0..0xE48` to `0x1798B0` with `fnv=762B22A5`,
`nz=0`, and stage 2 DMEM `0x6F0..0x7F0` to `0x1797B0` with
`fnv=E6A1D1C5`, `nz=0`.

The phase-qualified port static-call witness produced 512 silent and 1024
image rows. In the image hangar bucket, 508 rows were callsite `0x800052C4`;
one each were `0x8008F2CC`, `0x800B33BC`, `0x800B3490`, and `0x800B3500`.
There were zero rows whose callsite was `0x8002BEEC` or `0x800078EC`.

This selects `H-PortBoundaryAbsent` at the measured port witness and refutes
`H-PortBoundaryPresent` for that witness. `H-PortBoundaryDifferent` remains
open because the host witness does not expose an instruction-level indirect
predecessor field. The zero target payload remains unresolved; no waits,
dispatch, slots, or PCM writeback were changed.

Evidence: `scratch/agent/s3407_m5_port_producer_boundary/driver.log` and the
two arm logs.
