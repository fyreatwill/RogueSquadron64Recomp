# NEXT work unit (s2494) — capture the port osSpTaskLoad task boundary

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Capture the port's generated `osSpTaskLoad` entry during the qualified driven
hangar route and join its task pointer and fields to the established retail
oracle rows at `0x80033E3C`. The s2493 descriptor callback is a distinct
type-1 `gspTask` object, so do not compare it as if it were the retail type-2
load task. Use one batched port run with the descriptor control retained, the
new load-boundary fields, and all phase controls. Do not change task dispatch,
audio behavior, or guards.

## Competing hypotheses and discriminator

- H-port-load-matches-retail: the port load task pointer and selected
  type/data/yield/output fields match one of the retail target tuples.
- H-port-load-differs-retail: port load rows are populated but differ in
  pointer or selected fields, refuting equivalence at the direct load boundary.
- H-port-load-not-reached: the containing scheduler path is live but the port
  load hook has zero target-phase rows; move to the actual caller only then.

The discriminator is the joined table at port origin `0x006AB400`, width 512.
The port target-phase control, load-boundary hook, and prior retail positive
controls must be present. A complete pointer/field match selects equivalence;
a populated mismatch refutes it. Zero port load rows are valid only for the
third hypothesis when the containing scheduler path is live in the same run.

| Field | Port load hook | Retail oracle | Outcome |
|---|---|---|---|
| task pointer, type, data/yield/output fields | generated `osSpTaskLoad` rows | `0x80149470` tuples | match / mismatch |
| target route | port phase 12 / `0x006AB400` | retail 512 / `0x006AB400` | invalid without either |
| positive controls | descriptor + scheduler controls | whole-RDRAM 10,000; VI/PIF; load hits | invalid without controls |
| load hook | target-phase port rows | retail `0x80033E3C` rows established | third hypothesis if absent |

## Exact commands

First use the existing oracle artifact from s2493; do not rebuild or alter
the runtime before adding the complete port-side load-boundary table. Run the
qualified `tools/probe.sh` recipe with boot-relative Start presses, phase gate
at 1024, and the port generated load hook enabled alongside the existing
descriptor/scheduler controls. Capture the run log under
`scratch/agent/s2494_m5_port_load_join/` and SIGKILL the game through
`tools/probe.sh`.
