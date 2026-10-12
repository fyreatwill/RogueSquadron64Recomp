# Next work unit

HYPOTHESIS-ID: external-retail-entry-handoff

Run one new attributable handoff capture for the parked odd-PI/count-32 voice
record chain. Do not repeat the all-phase name-copy null or the M4 internal
accumulator probe.

Competing hypotheses:

- H-retail-entry-writer: retail reaches the voice-record handoff and a named
  guest writer publishes the legitimate B0xxxxxx pointer before the
  `0x800903F0` consumer.
- H-port-bridge-corruption: retail publishes the legitimate pointer, but the
  port's FE98/PI bridge changes the corresponding record into ASCII `lcre`.
- H-route-absent: the whole-RDRAM control fires but neither retail nor port
  reaches the count-32 handoff in the requested phase, so the current route
  cannot discriminate ownership.

Discriminating measurement: in one phase-gated capture, retain the whole-RDRAM
oracle control, exact target-range write watches, writer-PC histograms, and
`0x800903F0` execution rows; pair them with the port's existing FE98/voice+34
writer and consumer rows. A retail target write plus named writer before the
consumer selects H-retail-entry-writer; retail pointer bytes versus port `lcre`
at the same handoff selects H-port-bridge-corruption; firing controls with no
target/consumer rows selects H-route-absent.

Exact preparation and run requirements:

1. Inspect the existing census and recipes:
   `rg -n '0x800903F0|FE98|lcre|count-32|voice.*34' docs scratch/agent tools`
   and `sed -n '1,180p' docs/M5-S4596-VOICE34-CENSUS.md`.
2. Add all oracle watches and all port fields in one build; require positive
   whole-RDRAM, title `0x00790400`, and hangar `0x006AB400` controls.
3. Run from `build/`, phase-gated by VI transitions, and terminate every arm
   with SIGKILL. If the target phase is absent with the controls positive,
   record H-route-absent rather than adding another field.
