# Resume next work unit

HYPOTHESIS-ID: m3-next-idiom-census

WORK UNIT: choose the next unclosed generated M3 translation idiom after the
completed branch-likely and HI16/LO16 censuses, then perform one complete
static census of that whole class. Do not chase a single wild address and do
not add a guard before the whole class is enumerated.

Competing hypotheses:

* H-next-faithful: the next idiom is lowered consistently across the generated
  tree and is not the current defect.
* H-next-mismatch: at least one site has a semantically wrong generated
  lowering.
* H-next-intervening-write: at least one site is clobbered before its merge or
  use.
* H-next-route-gap: suspicious candidates exist but lack qualified-route
  reachability evidence.

DISCRIMINATING MEASUREMENT: enumerate every site in the selected idiom,
mapping guest PC, function, operands, intervening instructions, and derived
use. H-next-faithful is selected if every site has the expected lowering;
H-next-mismatch if a site demonstrably differs; H-next-intervening-write if a
site is clobbered before its merge/use; and H-next-route-gap if only suspicious
sites without route evidence remain.
The qualified title/hangar phase/SP/PCM route is the positive control, but no
site-level reachability claim may be made from it alone.

Exact commands:

    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n '<selected idiom>' ../N64Recomp/RecompiledFuncs/funcs_*.c tools docs

Write the bounded census to a new `docs/M3-S4838-HILO-CENSUS.md` only if the
class is found and classified. If a real runtime defect is proven, land the
smallest durable fix through the appropriate fixup script; otherwise the
census itself is the work result. Do not build or run until the hypotheses and
the discriminator above are still sufficient for every possible outcome.
