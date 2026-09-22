# M5 s3694 — DMEM producer join instrument

The independent retail control was run before the port build. A whole-RDRAM
watch fired 11,058 writes, the `0x1797B0..0x179930` source span fired 1,058,
the title subspan fired 48, and the retail run reached 444 VI samples at
hangar origin `0x006AB400`. Its phase-gated source writer histogram included
`0x800078EC` (768), `0x80007670` (172), and the `0x8001F...` family.

The port change adds a thread-local predecessor record to the existing
phase-scoped DMEM-store hook. Each source-range DMA row can now carry the
preceding DMEM writer sequence, address, length, scalar/vector kind, value,
payload hash, nonzero count, route ordinal, and overlap with the DMA source
window. The build completed successfully.

The first paired run was invalid: both arms stopped at VI width 640 because
the validated `ROGUESQ_LLE_UNGATED=1` route flag was omitted. The corrected
paired run qualified the silent arm at title and hangar, while real audio hit
`[audio-wait-pump-stall]` before the target source callbacks. A real-arm retry
with the corrected route reached title and hangar but again emitted only the
RSP source-hook control; it emitted no target DMEM-source or source-range rows.
The retry therefore has no valid producer table. The source-row cap was also
fixed so the optional transition logger can no longer bypass the target-phase
gate and consume the table with pre-target rows.

This session selects no producer hypothesis. `H-ZeroDMEMProducer`,
`H-DMEMJoinMismatch`, and `H-RetailSourceIsDifferent` remain open. The
absence of target source rows is unevaluable because the DMEM/source branch's
positive control did not fire in the qualified real-audio retry; the recurring
audio-pump stall is the immediate route blocker, not evidence about DMEM.

Evidence: `/tmp/rs64_oracle_s3694_groundtruth.log`,
`/tmp/rs64_s3694_real_fixed.log`, `/tmp/rs64_s3694_silent_fixed.log`, and
`/tmp/rs64_s3694_real_final.log`.
