# M5 Session 3430 — setDisplayMode caller arguments

The independent retail oracle ran first with a whole-RDRAM positive control,
Rice video, the validated Start schedule, and execution watches at the two
actual `setDisplayMode` callsites. The control reached 10,000 writes and the
route reached title 1024 and hangar 512. Retail exposed `0x8008EBC0` twice,
once in each target phase, with `a0=0x80165ED0`, `a1=0x12`, `a2=0x0E`, and
`a3=0`; `0x8008EA78` did not fire on this route. The missing init-callsite
row is therefore not interpreted as a phase failure.

The regeneration-safe port witnesses were inserted immediately before both
generated calls and the Debug build succeeded. Concurrent silent and Factor 5
image arms both reached title 1024 and hangar 512 with the host-positive init
control and audio ABI/DMA controls live, and neither emitted crash or abort
markers. Each arm exposed one `set-reapply` row at title with
`a0=0x80165ED0`, `a1=0x12`, `a2=0`, `a3=0`; neither exposed a `set-init` row.
The image-stage control fired only in the image arm.

This selects `H-DirectSetupCallerParity`: the observed port reapply caller
passes the same setup arguments as retail, while the divergent `0x5622` value
is not an argument to either observed audio setup call at this boundary. It
refutes `H-PortCountAtReapplyCaller` and `H-PortCountAtInitCaller` as proposed
explanations for the `0x5622` divergence, and closes the direct callsite
question at this scope. The earlier producer of the init-to-allocate count
remains unresolved; no runtime behavior changed.

Evidence: `scratch/agent/s3430_m5_setdisplay_groundtruth/oracle.log`,
`scratch/agent/s3430_m5_setdisplay_pair/{silent,image}.log`, and the build
output.
