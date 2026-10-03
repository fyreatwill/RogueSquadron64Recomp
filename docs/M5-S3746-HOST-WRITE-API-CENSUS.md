# M5 session 3746 — central host-to-RDRAM write census

The independent retail oracle was run first with a whole-RDRAM positive
control and exact physical watches. The control fired 10,010 times and the
run reached title and hangar. Retail wrote `0x128CD0..D3` five times from
guest PC `0x8001BB14`, all before the target phase buckets; it wrote
`0x128C92` zero times.

Added one phase-gated host-write census hook at the four central host-side
RDRAM write surfaces: PI ROM reads, PI SRAM reads, zmemcpy, and RSP
DMEM-to-RDRAM DMA. The hook emits a separate same-run control for each API
that executes, and reports any overlap with `0x128C92` or `0x128CD0..D3`.
The Debug target rebuilt successfully after exporting the runtime submodule
patch.

The first paired port launch reached the qualified hangar in the real arm and
fired the hook and RSP controls, with zero host exact-field rows; its silent
arm also reached hangar with zero rows. A fixed rerun added per-API controls:
the silent arm fired PI ROM, RSP DMA, PI SRAM, and zmemcpy controls, reached
hangar, and still emitted zero host exact-field rows. The fixed real retry
crashed before target phases in the scheduler, so it is not used as evidence;
the earlier same-build qualified real arm is the real-arm evidence.

This selects `H-ExactFieldUnwritten` for the censused central host APIs and
refutes `H-HostTransient` for that class. It does not cover arbitrary direct
host pointer writes outside those APIs and does not establish that the exact
fields are the image source rather than control metadata. No value was
suppressed or rewritten.

ORIGIN: no mitigation was added. The observed retail writer is
`0x8001BB14` for the earlier `0x128CD0..D3` writes; the port census observed
no target-phase host writer to either exact field.

Evidence: `scratch/agent/s3746_oracle_exact_route/oracle.log`,
`scratch/agent/s3746_port_host_exact_route/real.log` and `silent.log`, and
`scratch/agent/s3746_port_host_exact_route_fixed/silent.log`.
