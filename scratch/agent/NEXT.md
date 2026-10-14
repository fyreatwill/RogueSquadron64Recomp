# Resume next work unit

HYPOTHESIS-ID: m3-conditional-move-reachability

WORK UNIT: classify every one of the 149 file/guest-PC `movz`/`movn` sites in
`docs/M3-S4840-MOVZ-MOVN-CENSUS.md` as (a) post-return/unreachable, (b)
data-like/unreachable by generated control flow, or (c) reachable from a
generated entry/control-flow edge. Do not implement a fix yet.

Competing hypotheses:

* H-movz-movn-reachable: at least one nonzero-destination site is reachable;
  the `do_break` lowering is a live translation defect and needs a fixup-level
  implementation audit.
* H-movz-movn-latent: all sites are post-return or data-like/unreachable;
  the defect is latent on the generated control-flow graph and is not the
  current runtime explanation.
* H-movz-movn-route-gap: static CFG classification cannot prove reachability
  for the qualified route; no runtime conclusion is authorised.

DISCRIMINATING MEASUREMENT: for all 149 file/PC sites, independently inspect
the containing generated function's entry, labels, unconditional returns,
indirect-return blocks, and incoming generated gotos. Record one classification
and the exact predecessor evidence per site. H-movz-movn-reachable is selected
by any nonzero-destination site with a reachable predecessor; H-movz-movn-latent
by an all-unreachable table; H-movz-movn-route-gap only if the generated CFG
cannot decide a site. A runtime soak is not needed for this static discriminator.

Exact commands:

    python3 tools/census_movz_movn.py --output docs/M3-S4840-MOVZ-MOVN-CENSUS.md
    rg -n 'RECOMP_FUNC|return;|LOOKUP_FUNC|goto |L_[0-9A-F]+' ../N64Recomp/RecompiledFuncs/funcs_27.c ../N64Recomp/RecompiledFuncs/funcs_37.c ../N64Recomp/RecompiledFuncs/funcs_49.c

The s4840 table and parser are the fixed input. If a live site is proven,
inspect the fixup/regeneration path before changing generated output; if all
sites are latent, park this class and choose the next complete M3 census.
