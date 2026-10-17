# Session 5163 M4 retail page-writer phase attribution

The generated-symbol sweep was a REVISIT after the last 15 ledger entries were
all sweep classifications. The independent retail oracle was run once with a
whole-RDRAM write control, a physical watch on `0x1F0000:0x1F1000`, the known
lifetime writer `0x800078EC`, and phase-gated writer attribution for hangar
origin `0x006AB400`, width 512. The qualified cxd4 RSP plugin and Rice
rdplog route were used.

Controls and route:

- Whole-RDRAM control: 83,370 writes.
- Exact-PC control: `0x800078EC` executed 1,298,143 times.
- VI control: 595 frames at hangar origin `0x006AB400`, width 512; the run
  also reached title at width 1024.
- Target page lifetime writes: 73,370.

The phase-gated target-page writer table attributed 8,912 hangar-phase writes
to `0x800078EC`. It also retained the `0x800C7F08` and sequential
`0x800C7F34` through `0x800C801C` writer family (7,680 each in the same
phase-gated table). The phase-origin row retention counter itself remained
zero, so the per-write writer table, not retained row count, is the usable
phase discriminator in this run.

Outcome: `H-writer-is-hangar` is selected for the retail page-reuse question.
This identifies a legitimate retail writer during hangar; it does not prove
which value the port should produce or explain the port-side corruption. It is
single-source oracle evidence. No runtime mitigation is authorized.

Run logs: `scratch/agent/s5163_m4_page_writer/oracle.log` (route-blocked
control without cxd4 RSP) and `oracle-rsp.log` (qualified result).
