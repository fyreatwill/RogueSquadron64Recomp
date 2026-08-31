# M5 Session 3459 — qualify title source-value witness

Built the current tree and ran the prescribed LLE/spin-yield arm with
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_SPIN_YIELD=1`, and `ROGUESQ_LOG_M5_WRITER_PARITY=1`, gated on VI
width 1024. The port reached title origin `0x00790400` at 49.7 seconds and
produced 20 title-phase captures. It later changed to width 640 and crashed
in the existing MusyX path (`musyxSynthFrame+4268`, last guest PC
`0x80001B08`).

The parity positive control did fire in the earlier width-640 phase, but the
title-scoped control did not: there were zero `m5-writer-parity-control` rows
with origin `0x00790400` and zero `m5-source-writer` rows at that origin. The
source-value join is therefore unevaluable. The run qualifies title
reachability for this arm but does not qualify the title writer witness.

This does not select `H-RetailValue`, `H-SharedValue`, or `H-PortValue`, and
does not implicate audio behavior. The next unit must explain or repair the
missing title-scoped witness while preserving the current route and without
changing waits, slots, dispatch, clear behavior, or PCM writeback.

ORIGIN: the only observed crash is in the existing MusyX synth path after the
title phase; no mitigation was added. The retail post-store values remain
legitimate single-source observations, but no port-equivalent store was
observed in this run.

Evidence: `scratch/agent/s3459_m5_source_value_port/run.log`.
