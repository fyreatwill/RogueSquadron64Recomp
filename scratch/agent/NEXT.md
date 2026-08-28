# NEXT work unit — bounded VI-commit-to-route ordering audit

HYPOTHESIS-ID: m5-route-vi-commit-order

Perform one bounded static audit of the different handoff edge between the
host VI commit writer and the first audio route prepare. Do not add a probe or
build unless the audit identifies a concrete non-mitigation change.

Competing hypotheses and the discriminator:

- H-VICommitMissing: the port never records the target VI commit because the
  host writer is not reached or does not observe the guest VI state.
- H-VICommitMisordered: the commit is recorded, but route preparation reads a
  stale/foreign commit due to caller or thread ordering.
- H-PrepareConsumerWrong: the commit is valid and ordered, but the first
  route-prepare consumer selects the wrong task/arm or clears the identity at
  the wrong edge.
- H-StaticInsufficient: the sources do not expose a defensible missing or
  misordered edge, so no behavior change is justified.

The single discriminator is a complete writer-to-consumer table: every host
VI commit writer and caller, commit fields and sequence publication, every
route-prepare consumer, thread-local/atomic handoff, and the corresponding
retail-grounded target transition. A missing writer selects a concrete host
edge for later ground-truth-backed work; misordering selects the precise
publication/consumer edge; a wrong consumer selects its arm/clear boundary;
otherwise preserve the route-failure boundary and pivot to the generated
symbol sweep. Do not infer audio behavior from VI-640 `accepted=0`.

Exact commands from the repo root:

    rg -n -C 35 'g_m5_vi_commit|rs64_m5_vi|VI_WIDTH_REG|VI_ORIGIN_REG|vi-commit|route_prepare|route-prepare|audio_current_route_snapshot|identity_edge' src/main/main.cpp src/main/upstream_compat.cpp tools docs
    rg -n -C 20 'osViSetMode|osViSwapBuffer|rs64_m5_route_prepare_handoff' /Users/williambuckley/Documents/Tools/rogue_squadron64
    git diff -- src lib syms tools

Record the complete table and decision in
`scratch/agent/s3043_m5_vi_commit_order_audit/`.
