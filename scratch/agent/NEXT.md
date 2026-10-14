# Resume next work unit

HYPOTHESIS-ID: m3-conditional-move-census

WORK UNIT: perform one complete static census of the next unclosed generated
conditional-move class (`movz`, `movn`) in
`../N64Recomp/RecompiledFuncs/funcs_*.c`. Do not chase a single wild address
and do not add a guard before the whole class is enumerated.

Competing hypotheses:

* H-conditional-move-faithful: every site has the expected conditional
  assignment or preserved destination.
* H-conditional-move-mismatch: at least one site assigns on the wrong
  predicate or writes an incorrect source/destination.
* H-conditional-move-intervening-write: a source, destination, or predicate
  register is clobbered before the generated conditional operation.
* H-conditional-move-route-gap: the class is faithful, but suspicious sites
  (if any) lack qualified-route reachability evidence.

DISCRIMINATING MEASUREMENT: enumerate every `movz`/`movn` site twice, mapping
guest PC, function, operands, generated branch/assignment shape, and the next
three guest instructions. The expected form preserves the destination for a
false predicate and assigns the source only for the true zero/nonzero
predicate. H-conditional-move-faithful is selected if both passes agree and
every site matches; mismatch or intervening write is selected by a concrete
exception; route-gap remains only if static evidence is clean but reachability
is absent.
The qualified title/hangar phase/SP/PCM route is the positive control, but no
site-level reachability claim may be made from it alone.

Exact commands:

    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n '\b(movz|movn)\b' ../N64Recomp/RecompiledFuncs/funcs_*.c

Write the bounded census to a new `docs/M3-S4839-*.md` only if the
class is found and classified. If a real runtime defect is proven, land the
smallest durable fix through the appropriate fixup script; otherwise the
census itself is the work result. Do not build or run until the hypotheses and
the discriminator above are still sufficient for every possible outcome.
