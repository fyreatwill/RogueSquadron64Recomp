# NEXT work unit — audit the port target-VI publication boundary

HYPOTHESIS-ID: m5-target-vi-publication-boundary

Session 3275 validated the port phase-4 controls at `640 /
0x0066A500` in both same-build audio arms, but neither arm reached a target
phase or emitted `[m5-port-retail-target]`. The retail target writer remains
single-source evidence, principally guest PC `0x800078EC`. This unit audits
the local publication/commit boundary without changing runtime behavior.

## Competing hypotheses

- `H-PortTargetPublicationAbsent`: no local caller publishes a target VI
  request after the valid phase-4 commit.
- `H-PortTargetCommitMismatch`: a target request is published, but the commit
  or route-preparation consumer uses another width/origin or caller relation.
- `H-PortPublicationSourceUnavailable`: the checked-in sources/symbol data do
  not expose the complete caller-to-commit chain.

## Discriminator

Build one caller-to-commit table from the checked-in VI wrappers and every
available caller/symbol reference. A complete table with no target request
selects `H-PortTargetPublicationAbsent`; a target request with changed
commit/consumer fields selects `H-PortTargetCommitMismatch`; missing
generated/local bodies or unresolved callers selects
`H-PortPublicationSourceUnavailable`.

## Exact command

From the repository root, run:

```sh
rg -n "osViSetMode|vi-commit|route-prepare|m5-route-transition|m5-port-vi-control|applyPendingViChanges|0x80007904|0x8000834C" src lib tools syms --glob '!*.log' --glob '!*.dmp'
rg -n "VI|osViSetMode|applyPendingViChanges|0x0066A500|0x00790400|0x00790000" docs scratch/agent --glob '*.md' --glob '*.txt' | head -200
```

Write the complete table and classification to
`scratch/agent/s3276_m5_target_vi_publication_audit.md`. If source coverage is
complete, no build is needed; do not run M5 Step 3 from this result because it
still requires a like-for-like target row and the existing guard-build
prerequisite.
