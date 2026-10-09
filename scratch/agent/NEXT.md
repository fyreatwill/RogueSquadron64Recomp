# Next work unit (s4334): map the retail descriptor boundary

HYPOTHESIS-ID: m5-step9-retail-boundary-map

The s4333 retail oracle controls passed, but exact `0x8009C88C` had zero hits.
A broad `0x8009C000:0x8009D000` range hit 999,770 times in the valid 512-wide
phase; the narrowed `0x8009C800:0x8009C900` range had zero hits. The port C88C
address is not yet a usable retail descriptor boundary.

Competing hypotheses:

- H-retail-counterpart: a nearby retail execution range/caller corresponds to
  the port descriptor helper and can be field-dumped in the 512 phase.
- H-retail-layout-gap: the mapped C88C/D740 windows have no stable retail
  counterpart, so the comparison requires address/overlay translation first.
- H-oracle-invalid: a repeat loses the whole-RDRAM, title, or hangar controls.

Discriminator: run one retail oracle census with the whole-RDRAM positive
control, VI trace, and phase-gated execution ranges covering the port C88C/D740
windows plus their `exec-prev` histogram. A stable 512-phase range/caller hit
selects H-retail-counterpart and identifies the next `--pc-field-dump` target;
zero across all mapped windows selects H-retail-layout-gap; missing controls
selects H-oracle-invalid. Do not compare payloads or change runtime behavior.

Before building any new port instrument, map the remaining port descriptor/D740
windows from the generated source, then run one bounded oracle census. Suggested
command shape:

`tools/oracle/build/rs64_oracle ... --watch-write 0x0:0x800000 --watch-pc-range 0x8009C000:0x8009D000 --pc-phase-log-width 0x006AB400:512 --pc-phase-quiet --vi-trace ...`

Do not change decoder, RSP, AI, or game-path behavior. Keep all comparison
rows phase-gated on VI origin `0x006AB400` and width 512.
