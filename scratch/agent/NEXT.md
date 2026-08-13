# NEXT work unit (classify the residual E9 condition)

HYPOTHESIS-ID: m3-rdp-parser-condition

Instrument the RT64 extended-opcode branch for raw E9 candidates with a
behavior-neutral breadcrumb, build one Debug binary, and run one phase-gated
capture. Do not change parser advancement, RDP handlers, or mitigation.

Competing hypotheses and discriminator:

- H-extended-residual: raw E9 entered the extended-opcode branch, which has no
  condition callback and can advance outside the normal command table.
- H-residual-range: the one slot is a non-deferred synthetic range or stale
  submit-label case.
- H-pending-residual: the slot is completed through a split-command pending
  lifecycle that the aggregate condition join missed.
- H-instrumentation-gap: the row is a normal direct/span path but was missed by
  the join's task/serial/range association.

Discriminator: an extended-branch marker on the residual address selects
H-extended-residual; a synthetic marker with the same address selects
H-residual-range; a pending completion selects H-pending-residual; none of
these with the positive direct/span controls firing selects
H-instrumentation-gap. All arms are measured in this one run.

Exact commands:

1. Add the branch-only breadcrumb in `lib/rt64/src/hle/rt64_interpreter.cpp`
   carrying the existing task/serial/range fields; keep the existing E9
   provenance controls enabled.
2. Build with the normal Debug target and run the existing phase-gated recipe
   with `ROGUESQ_LOG_RDP_CONDITION=1` plus the new branch flag.
3. Require the four E9 positive controls and compare the residual address
   against branch, synthetic, and pending rows. Kill with SIGKILL; no A/B or
   second run.
