# NEXT work unit (s2437) — phase-locate the retail caller

HYPOTHESIS-ID: m5-retail-caller-reachability

## Work unit

Use one bounded retail-oracle run with the same positive control and exact
writer watches, but phase-gate the actual `jal` callsite `0x8008F2CC` across
the observed 640-width intro origins (`0x0066A500`, `0x005D4500`,
`0x00696600`, `0x00696100`, `0x0062C200`, `0x0062BD00`) as well as title and
hangar. Keep `--pc-field-dump 0x8008F2CC` and
`--store-field-dump 2:0x800078EC`; observation-only, no port change.

## Competing hypotheses and discriminator

- H-RetailIntroCaller: the six lifetime calls land in an observed 640 intro
  origin and expose a field context related to the exact writer.
- H-RetailCallerUnrelated: the calls land in a 640 origin but their field
  context does not join the exact writer's phase/arguments.
- H-RetailCallerUnreached: all controls pass but no phase bucket retains a
  caller row, so the callsite is not on the exercised route.

The discriminator is the same-run table joining any retained callsite rows
(`pc=0x8008F2CC`, `$s0/$s1`, pointed source fields, `$a0/$a1/$a2`) to exact
writer rows by phase and return address. Intro-origin rows with a matching
writer context select H-RetailIntroCaller; nonmatching rows select
H-RetailCallerUnrelated; zero rows with valid controls select
H-RetailCallerUnreached.

## Exact validation

Require the whole-RDRAM positive control to reach 10,000 callbacks, title
`0x00790400:1024`, hangar `0x006AB400:512`, and exact-range totals before
interpreting any row. Use `--watch-pc 0x8008F2CC,0x800078EC`, repeated
`--pc-phase-log` for the six 640 origins plus the explicit title/hangar width
buckets, `--pc-field-dump 0x8008F2CC`, and
`--store-field-dump 2:0x800078EC` with the existing eleven-Start schedule.
