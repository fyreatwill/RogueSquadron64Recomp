# M5 s4825 — qualified-route startup boundary audit

The existing same-build A/B logs were audited without a rebuild or rerun. Both
arms reached the same first SP task: queue `0x8011A420`, message
`0x80128C70`, scheduler type `0x01` then `0x81`, LLE task data
`0x80720108`, and one SP completion. The default arm then completed ten SP
tasks and stopped at VI 320; request-only crashed after its first completion.

The request-only crash had no `[sp-yielded-ab]` row. Its last scheduler rows
were `19CDC`, `19DFC`, `19E7C`, and `19E80T`; the crash followed before the
next observable `osSpTaskYielded` row. Therefore the request-only
`exchange(false)` branch did not execute in this capture and cannot explain
the fault. The request-only lifecycle hypothesis is not selected.

The crash reported host PC `0x1056dc634`, fault address `0x400128d47`, and
register evidence containing the guest message pointer `0x80128c70` and the
derived bad address `0x80128d47`. The guest breadcrumb `0x8000834c` resolves
to the delay-slot `nop` after `drainMeshReleaseQueue` returns, so it is stale
breadcrumb state, not a faulting instruction attribution.

Selected result: `H-common-precontrol-boundary` (single A/B source). The arms
share the scheduler/task boundary, but the exact host operation or writer of
the malformed pointer remains unresolved. No mitigation or behavior change
was made.

ORIGIN: diagnostic-only source/log audit; the malformed host pointer has not
been suppressed, rewritten, or guarded.
