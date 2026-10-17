# Next: new-angle external retail-entry boundary revisit.

The s5250 baseline arm self-skipped at host load1=5.20, so do not retry it
until a future loop supplies load1<2. M5 has no uncompleted de-stub step and
the recent M3 idiom classes are closed. The `vi` candidate was confirmed as
typed `OSViContext` data with no callable placeholder in s5277; do not continue
the sweep until the retail-entry revisit is attempted.

Competing hypotheses and discriminator:

- H1: the remaining retail/port entry difference is an unmeasured argument or
  return-value contract at the retained caller, not the previously censused
  byte field.
- H2: the difference is introduced before the retained caller by a distinct
  caller path or phase-specific dispatch.
- H3: the difference is measurement-only and disappears when the same
  caller/phase/argument tuple is joined on both sides.

Discriminating measurement: use one phase-gated run of the existing entry-join
instrumentation, retaining a complete tuple for every `0x8008FAAC` hit:
caller PC, `a0`, DRAM `a1`, `a2`, `a3`, and return-side scalar state. H1
predicts a tuple/return mismatch with the same caller; H2 predicts an
unmatched caller/phase population; H3 predicts matching tuples and return
state. A whole-RDRAM positive control must fire in the same run before a null
is interpreted.

Exact preparation command (before any build):

`rg -n "s5223_entry_join|whole-RDRAM|phase-origin-watch|8008FAAC" tools src/main ../N64Recomp/RecompiledFuncs/funcs_24.c`

HYPOTHESIS-ID: external-retail-entry-boundary-revisit
