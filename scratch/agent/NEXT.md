# NEXT work unit — select the next highest-information-value M3 audio idiom

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: select and execute one new complete grep-enumerate/classify
M3 audio idiom audit from the unresolved runtime-legitimacy boundaries. Start
by enumerating candidate unchecked fields/consumers and choose the class with
the strongest concrete writer-to-consumer discriminator; do not re-audit the
closed MORT publication, mix-table, pan-input, or hangar-Y classes. Do not
change runtime code unless a concrete invalid writer/value is identified. Any
mitigation needs an ORIGIN line naming the writer and assessing legitimacy.

Competing hypotheses and discriminator for this selection:

- H-NextClassGap: the selected unresolved class contains a concrete invalid
  writer/value or unchecked edge.
- H-NextClassComplete: the selected class is structurally complete and only
  runtime legitimacy remains.
- H-NextClassUnevaluable: generated code does not expose a complete edge set.

Discriminator: one ranked candidate table followed by one complete audit of
the selected class, with every writer, consumer, base, and bound classified.
Select H-NextClassGap only with a concrete invalid edge; select
H-NextClassComplete only when every edge is covered; otherwise leave it
unclassified.

Exact checks before any build:

    rg -n 'MEM_[BHW].*(0X[0-9A-F]+|-[0-9A-F]+)|LOOKUP_FUNC|jalr' ../N64Recomp/RecompiledFuncs/funcs_{22,23,24,25,26,27}.c
    rg -n 'RECOMP_FUNC|<candidate-symbol>|<candidate-offset>' ../N64Recomp/RecompiledFuncs/funcs_*.c
