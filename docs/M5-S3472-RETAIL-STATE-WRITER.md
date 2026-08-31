# M5 Session 3472 — qualified retail state-table writer observation

The independent Rice-oracle capture watched physical `0x1B4AA0..0x1B4B24`
with a same-run whole-RDRAM positive control. The control recorded 13,527
writes, the target span recorded 3,527 writes, and the title phase reached
634 width-1024 VI frames at origin `0x00790400`.

The title-gated writer histogram recorded `0x800078EC` (132),
`0x80064350` (217), `0x80064360` (211), `0x80064378` (211), and
`0x800646D8` (527). Post-store sampling recorded 267 samples, 64 unique
values, 115 nonzero bytes in the final watched span, and 113 samples of
zero. Per-PC post-store sampling was live for each candidate writer; the
four `0x80064350/60/78` samples were nonzero.

This validates the independent observation and refutes
`H-ObservationInvalid`: the physical span is written during the qualified
title phase and its candidate writers are observable. It does not yet select
`H-RetailStateWriter` over `H-PortPointerSelection`, because the oracle rows
do not carry the selected-entry identity needed to join each write to the
port's table-selection rows. No runtime behavior or mitigation changed.

The first capture omitted the explicit phase histogram; the corrected capture
added `--pc-hist-phase 0x00790400:1024` and `--post-value-watch 1` in the same
schema. Evidence: `scratch/agent/s3472_retail_state_writer_postvalue.log`.
