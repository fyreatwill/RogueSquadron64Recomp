# Next: audit lwl/lwr (and ldl/ldr) pairs split by a branch target (M3 idiom class)

Delay-slot classes (operand hazard s5345, branch-in-slot s5346) are closed.
Hypotheses: H1 every lwl/lwr pair is adjacent or in straight-line code (class empty);
H2 some pair has a branch target between halves, so recomp's merged/ordered handling
could read a stale partial register; H3 sites only in runtime-replaced libultra.
Discriminator: extend tools/ with a census of lwl/lwr/swl/swr/ldl/ldr whose partner
is not within the same basic block (a branch target or branch lies between). Positive
control: synthetic split pair must be flagged. Report count; for hits read generated C.
Do not touch lib/.

HYPOTHESIS-ID: lwl-lwr-split-pair-audit
