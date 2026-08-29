# NEXT work unit — fresh M3 idiom-class census

HYPOTHESIS-ID: m3-fresh-idiom-census

Session 3236 completed M5 Step 3 selection without finding an independently
proven contract edge. The target-phase port row is still unevaluable, so no
M5 behavior change is authorized and the same qualification is parked.

## Competing hypotheses

- `H-NewClass`: a complete, currently unclassified repeated unsafe-access
  idiom exists in the active generated/fixup audio paths.
- `H-ClosedClasses`: every repeated idiom above the audit threshold is already
  covered by the closed M3 publication/guard censuses.
- `H-GuardOnly`: remaining matches are one-off guards or readers whose writer
  and validity are already proven, not a coherent class.

## Discriminator

Perform one from-scratch, grep-enumerated census of the active generated and
fixup-controlled audio paths. Group every match by base pointer, offset,
operation, and caller; for each repeated group identify all writers and
classify each site as guarded, proven-in-range, or unresolved. A result with
one unresolved repeated class selects `H-NewClass` and names the complete
site list for the next guard audit; zero unresolved repeated classes selects
`H-ClosedClasses`; only isolated/proven reader matches selects `H-GuardOnly`.
The census must not add a guard or change runtime behavior.

## Exact commands

1. `rg -n "(D_8014|D_8015|voice|slot|musyx|break [67]|KSEG0|guard)" src patches tools`
2. Enumerate each repeated unsafe-access shape and inspect bounded source
   windows; do not read generated or ledger files wholesale.
3. Record the complete classification and selected class in a new
   `scratch/agent/s3237_m3_*` report. No build or soak is authorized unless a
   concrete behavior change is selected by the census.
