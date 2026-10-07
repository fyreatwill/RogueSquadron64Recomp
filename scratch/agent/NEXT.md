# Next work unit: M3 expansion-chain sentinel ownership guard

HYPOTHESIS-ID: m3-expansion-sentinel-ownership

The mandatory pivot makes the selector census inapplicable this iteration: it
would be oracle-only and would not land an engineering artifact. The bounded
M3 audit targets the allocator expansion path in patches/heap_guards.c.

Competing hypotheses:

- Hsentinel-alias: func_8002221C can publish an expansion node equal to the
  active allocator sentinel, so the expansion validation can mutate metadata.
- Hsentinel-disjoint: the existing post-splice sentinel check is sufficient and
  no pre-mutation ownership guard is needed.
- Hcoverage: the expansion branch or sentinel metadata is unavailable, so this
  audit cannot qualify the missing check.

Discriminating check: enumerate every expansion-chain dereference and link
store, then prove whether the sentinel is checked before the first store. A
pre-mutation sentinel-disjoint guard closes Hsentinel-alias; an audit showing
the sentinel is already checked before all expansion stores selects
Hsentinel-disjoint; missing source/build coverage selects Hcoverage.

Required validation command after the edit:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Runtime qualification remains blocked because this host lacks
mips64-elf-gcc/mips64-elf-ld; do not infer runtime behavior from the ordinary
host build.
