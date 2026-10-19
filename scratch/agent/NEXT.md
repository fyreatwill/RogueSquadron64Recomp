Single next unit: audit the non-standard return idiom class where `$ra` is
written after the function's last call or before `jr $ra` in generated MIPS.
Competing hypotheses and discriminator:

1. H1: every reachable `jr $ra` uses an intact return address restored from
   the frame or preserved by the ABI; no bad return-site write exists.
2. H2: a reachable function clobbers `ctx->r31` after its last call and then
   returns through that value; the census identifies the function and address.
3. H3: apparent late `$ra` writes are delay-slot duplication, invalid/data-gap
   material, or tail-call/control-flow artifacts rather than bad returns.

Discriminating measurement: one whole-tree census of every `jr $ra` comment,
`ctx->r31` assignment, call site, and return block, with positive controls for
an ordinary saved-`ra` epilogue and a known tail call. Classify every candidate
by reachability and delay-slot normalization; land a fix only for a concrete
reachable clobber. No runtime build is planned.

HYPOTHESIS-ID: m3-idiom-class-audit
