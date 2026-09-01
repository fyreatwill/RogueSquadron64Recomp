# M5 Session 3572 — source transition join

The new opt-in `ROGUESQ_LOG_M5_SOURCE_TRANSITION` table recorded exact
source-span CPU stores, memsets, and DMA writebacks from process start through
the first target source DMA. The build passed title `1024 @ 0x00790400`,
hangar `512 @ 0x006AB400`, the RSP/source positive control, and the existing
writer controls. It emitted 2,044 transition rows: 1,036 CPU stores and 1,008
source-range DMA writebacks.

Before the first hangar source DMA, the port recorded 1,036 CPU-store rows and
no source-range DMA or memset rows. Nonzero initialization came from
`0x80007670` and the `0x8001FAxx` texture-record family during the preceding
640/title phases. In the target phase, `0x800078EC` then wrote zero bytes
through `0x1797B0..0x179930`; the first target DMA followed with zero payload.
The target-phase transition table contained 384 CPU zero-store rows and 1,008
zero-payload DMA rows.

The independent retail oracle passed its whole-RDRAM positive control, reached
the target route, and recorded 1,166 writes in
`0x1797B0..0x179A48`. Its target-phase writer histogram independently included
`0x80007670`, the `0x8001FAxx` family, and `0x800078EC` (664 writes). This
confirms that the writer family is real game activity, not a port-only hook
artifact; the oracle run did not capture store values, so numeric parity is
not claimed.

This selects `H-PreTaskCpuInit` at the transition boundary: the port does
produce nonzero source content before the target handoff, then a CPU zero-fill
from `0x800078EC` removes it before the first source DMA. It refutes
`H-PreTaskOtherInit` and `H-PreTaskZeroContract` for the earlier transition,
but does not explain why the zero-fill is ordered or populated on this route.

ORIGIN: diagnostic-only source-transition census. No output, PCM, task, DMA,
or source state was changed.

Evidence:

- Port log: `scratch/agent/s3572_source_transition/run.log`
- Retail oracle log: `scratch/agent/oracle_transition_3572/oracle.log`
- Oracle positive-control preflight:
  `scratch/agent/oracle_preflight_3572/control.log`
