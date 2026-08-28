# NEXT work unit (s2974)

HYPOTHESIS-ID: m5-route-prep-target-predicate

## Unit

Perform one bounded source audit of the existing M5 route-preparation target
predicate and its legitimate writer/ordering edge, using the s2973 evidence as
the baseline. Do not de-stub audio or add another run-lifetime diagnostic.
Identify the exact state/VI values that make the port predicate remain
`target=0` at VI 640, compare them with the retail target handoff already
captured by the oracle, and land one regeneration-safe route repair only if the
writer is demonstrably producing a stale or incomplete port value. If the
predicate is intentionally pre-target-only, record the specific missing
handoff rather than adding a guard.

## Competing hypotheses and discriminator

- H-target-predicate-stale: the port target predicate reads a stale or
  incomplete VI/route value; the writer and ordering edge can be named and a
  minimal repair makes the target predicate true.
- H-target-handoff-missing: the predicate is correct, but the port never
  receives or commits the upstream target route handoff; no local predicate
  change is justified.
- H-target-definition-mismatch: the port and retail use different legitimate
  target identity/origin definitions; the mismatch must be resolved from the
  independent oracle before changing code.

The discriminator is the source-level value-flow table: target predicate,
each input value, its writer, ordering edge, and the corresponding retail
handoff fields. A stale value with a named writer selects H-target-predicate-
stale; an absent upstream handoff selects H-target-handoff-missing; a
legitimate definition mismatch selects H-target-definition-mismatch. Do not
build or run until this table is written here or in a new artifact.

## Commands

1. Inspect the existing route-preparation call sites and handoff definitions:
   `rg -n "route_target|route_prepare|m5.*route|VI_ORIGIN_REG|VI_WIDTH_REG" src RecompiledPatches build -g '!*.log'`.
2. Read bounded windows around each predicate and writer. Check the s2973
   `RESULTS.md` and the oracle route fields; do not read large logs.
3. If and only if the table identifies a legitimate stale-value writer,
   patch the smallest regeneration-safe host route handoff, rebuild
   `RogueSquadron64Recomp`, and run both arms with the existing s2973 wrapper
   recipe and oracle positive control. Otherwise land the audit artifact and
   leave behavior unchanged.
