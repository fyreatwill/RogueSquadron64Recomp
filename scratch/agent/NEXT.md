# NEXT work unit (reach the residual E9 condition)

HYPOTHESIS-ID: m3-rdp-parser-condition

Run one phase-gated capture with the existing `kind=extended` instrument and
the full provenance controls, requiring the capture to reach task 650 or
later. Do not change parser advancement, RDP handlers, or mitigation.

Competing hypotheses and discriminator:

- H-extended-residual: raw E9 entered the extended-opcode branch, which has no
  normal command-table condition path and can advance outside the normal
  command table.
- H-residual-range: the one slot is a non-deferred synthetic range or stale
  submit-label case.
- H-pending-residual: the slot is completed through a split-command pending
  lifecycle that the aggregate condition join missed.
- H-instrumentation-gap: the row is a normal direct/span path but was missed by
  the join's task/serial/range association.

Discriminator: after task 650, an extended marker on the residual address
selects H-extended-residual; a synthetic marker with the same address selects
H-residual-range; a pending completion selects H-pending-residual; none of
these with the positive direct/span controls firing selects
H-instrumentation-gap. A run ending before task 650 is unevaluable and cannot
update the hypothesis ledger.

Exact commands:

1. Use the already-built Debug target and run
   `env ROGUESQ_LOG_RDP_CONDITION=1 zsh scratch/agent/s790_postsec2_reachability.sh`.
2. Require VI 1024, all four E9 positive controls, and a late task >=650;
   compare the residual address against `kind=extended`, synthetic, and
   pending rows. Kill with SIGKILL; no A/B or second run.
