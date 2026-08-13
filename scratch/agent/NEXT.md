# NEXT work unit (s881)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree. Pick
the highest-ranked unclassified pointer idiom at the start of the iteration,
enumerate every site with `rg`, and classify every occurrence as proven safe,
dead/phase-unreachable, or requiring a patch. Do not add a guard until the
whole class is enumerated and the writer/legitimacy question is explicit.
Do not run a game build or animating A/B for this source inventory.

Competing hypotheses:

- H-class-has-unclassified-sites: the selected idiom has at least one site
  without a proof of safety or a concrete writer/legitimacy explanation.
- H-class-fully-classified: every selected site is already proven safe, dead,
  or covered by an existing justified patch.
- H-inventory-shape-mismatch: the candidate ranking does not define one
  coherent idiom class; stop and record the shape mismatch rather than mixing
  unrelated sites.

Discriminating measurement: the complete site table for one syntactic idiom,
with a classification and writer/legitimacy basis for every hit. Any omitted
site or unproven writer rejects H-class-fully-classified; a coherent but empty
class selects H-inventory-shape-mismatch.

Exact commands: use `rg` to enumerate the selected idiom in `RecompiledFuncs/`
and the fixup/source inventories, then use bounded `sed` windows around every
site and its named-symbol/decomp counterpart. Record the site count and all
classifications in the session ledger. No game build or soak is planned.
