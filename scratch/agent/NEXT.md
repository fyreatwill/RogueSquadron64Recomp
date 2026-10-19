Single next unit: audit one unlisted M3 idiom class: generated `$at`/`r1`
values crossing branch joins and delay-slot-normalized return paths.
Competing hypotheses and discriminator:

1. H1: every reachable branch join preserves the value expected by the
   following generated operation.
2. H2: a reachable join loses or overwrites `$at`/`r1`, changing a later branch,
   address calculation, or delay-slot operand.
3. H3: apparent hazards are dead conditional material, duplicated delay-slot
   code, or invalid/data-gap fragments.

Discriminating measurement: one whole-tree census of every `ctx->r1` write,
branch/jump join, and delay-slot use, with positive controls for an ordinary
branch join and a known dead/data-gap fragment. Classify every candidate by
reachability and delay-slot normalization; land a fix only for a concrete
reachable value change. No runtime build is planned. Run:
`python3 tools/audit_at_branch_join.py` after adding that census script.

HYPOTHESIS-ID: m3-idiom-class-audit
