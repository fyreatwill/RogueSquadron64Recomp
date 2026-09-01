# M5 Session 3486 — selector pointer writer join

The independent Rice oracle passed the whole-RDRAM control and reached the
title phase. A read/write capture of physical `0x00149750` recorded 3,228
retail writes and 78,106 reads; the writer-PC histogram identified
`0x80091074` for all writes, including 629 title-phase writes. The selector
block was live with 2,249 title executions at `0x800916F0` and 2,246 at
`0x80091710` in the paired capture.

The matching port run initially hit the known startup crash at guest PC
`0x8000834C` before title. The fixed retry used the validated
LLE/spin-yield/ungated route, passed the task-writer and pointer controls, and
reached title origin `0x00790400`. Its bounded pointer-store rows were all
from `0x80091074`. Normal selector and pointer-store values were
`0x80171CE0` and `0x80173B20`, with one title-phase `0x8018DD30` value in both
the selector and pointer-store rows. No `0x8018FB70` row appeared in this
retry.

This matches the retail and port writer route at the measured pointer word
and rules out a writer-route-only explanation for the extra port operand. It
does not establish that writer inputs or stored values are identical across
runtimes, nor does it rule out a post-store selection transform. The oracle
and port controls both fired, so the null for `0x8018FB70` is qualified only
for this retry's title capture.

Evidence: `scratch/agent/s3486_m5_ground_truth/pointer-hist.log`,
`scratch/agent/s3486_m5_ground_truth/oracle-read.log`, and
`scratch/agent/s3486_m5_port/port-retry2.log`.

ORIGIN: the witness observes the pointer word, selector registers, and writer
PC/value; it does not rewrite, skip, or validate task fields.
