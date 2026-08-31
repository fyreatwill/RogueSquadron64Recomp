# M5 session 3393 — lower-noise target attribution

The independent retail oracle ran before the port with whole-RDRAM and exact
target-span write watches, plus execution watches for `0x800078E8` and
`0x800078EC`. Its positive controls fired: 11,125 whole-RDRAM writes, 1,125
writes in `[0x1798B0,0x179A48)`, 6,507 executions at `0x800078E8`, and
3,244,851 at `0x800078EC`. The phase-specific target attribution remained
`n=0` for `origin=0x006AB400`, width 512, so the retail payload edge is
partial even though the exact target watch itself fired.

The same-build port probe reached title origin `0x00790400`, width 1024, at
11.6 seconds and hangar origin `0x006AB400`, width 512, at 19.7 seconds. The
phase-gated controls and PCM source/consumer controls fired. In the hangar
phase the only target-area event was the existing zero-fill path:
`0x8008F2CC -> rs_memset`, destination `0x801797B0`, length `0x298`, value
zero. No port row for `0x800078E8` or `0x800078EC` appeared, and the PCM
boundary rows remained `FNV=0xF59C39C5`, `nz=0`.

This reinforces `H-EarlierPortContract` only at the observed port boundary and
refutes a matching port producer row in this run. It does not identify the
retail payload's producer contract and does not prove that the port zero-fill
writer is illegitimate. The exact census should not be repeated unchanged;
the next probe must repair or replace the retail phase-attribution view.

Evidence: `scratch/agent/oracle_s3393_lower_noise.log` and
`scratch/agent/port_s3393/run.log`.
