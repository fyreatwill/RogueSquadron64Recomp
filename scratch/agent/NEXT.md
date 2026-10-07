# Next work unit: audit the A8 key-on divide/overflow idiom class

Session 4120 selected H-A9-legitimate at the qualified title/hangar scope.
Execute exactly one complete A8 census/capture next; do not remove or bypass
the traps.

HYPOTHESIS-ID: m5-step8-keyon-divide-overflow-class

Competing hypotheses and discriminator:

- H-A8-trap-live: the eight defensive divide/overflow sites are not reached
  with invalid divisors, and the normal key-on tail remains live.
- H-A8-suppresses-valid: a trap site fires on valid retail-shaped work or the
  port loses a valid key-on tail/slot transition at that site.
- H-A8-route-invalid: the paired capture misses a required control or target
  phase, so trap and tail nulls are unevaluable.

The single discriminating measurement is one complete A8 source census plus
one same-build retail/port phase-gated capture. The census must include all
eight sites (`0x80090CEC`, `0x80090D04`, `0x80090D30`, `0x80090D48`,
`0x80090D74`, `0x80090D8C`, `0x80090DB8`, `0x80090DD0`), the divisor publisher
at `0x80090768`, the normal-tail rows, and slot `0x02` then `0x00` controls.
Ask the retail oracle first with whole-RDRAM and divisor/source controls.
Retail must reach title and hangar; port must reach both phases and fire the
positive controls. Any missing phase selects H-A8-route-invalid. A trap with
retail-valid divisor evidence or a missing normal tail selects
H-A8-suppresses-valid; otherwise select H-A8-trap-live. Do not alter a trap.

Before building, enumerate every A8 site and publisher with bounded `rg`
searches in the generated tree, fixup script, and oracle watch configuration.
Use the qualified route parameters from s4120:
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_SPIN_YIELD=1
ROGUESQ_M5_C88_VALUE=0 ROGUESQ_AUDIO_UCODE=1`, with phase-gated controls.

Required build:

`cmake --build build --config Debug --target RogueSquadron64Recomp`
