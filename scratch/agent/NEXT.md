# Next work unit

HYPOTHESIS-ID: m5-retail-writer-ownership

Use one bounded static ownership lookup for the three retail destinations
identified in s4936: 0x80149702, 0x80149988/8A, and 0x800A1778. Search the
companion decomp symbols/m2c output and the port's generated symbols for the
owning structure and fields, then compare the retail store cadence with the
port's 0x80149470 route state. Do not change runtime behavior.

Competing hypotheses and discriminator:

1. H-route-state: the destinations are fields in the audio route/slot state
   represented by 0x80149470 or a directly referenced child structure.
2. H-render-or-input: the destinations belong to an unrelated render, input,
   or timing table, and the writer's audio-looking context is incidental.
3. H-unknown: the available symbol/decomp material cannot establish ownership
   without a new runtime watch.

The discriminating measurement is a complete address-to-symbol/field table for
all three destinations, including every static reference and the closest named
structure member. H-route-state is selected if the table identifies the
route/slot object and its port counterpart; H-render-or-input if it identifies
another subsystem; H-unknown if no named owner can be proven. If static
ownership is unresolved, stop and design a new phase-gated oracle/port join
before building anything.

Suggested commands: rg -n "80149702|80149988|8014998A|800A1778|80149470"
../rogue_squadron64 ../N64Recomp RecompiledFuncs syms docs; then read bounded
windows around each hit. No build or soak is authorized until the table and
the competing outcomes are written here.
