# NEXT work unit (s1176)

HYPOTHESIS-ID: musyx-downstream-ground-truth-pointer-origin

Correlate the s1175 retail writer PCs with the generated MusyX initialization
body and companion symbols, then identify the first actual sample/stream-field
writer for a later ground-truth watch. No voice-array range may be inferred
from `0x001496F8`.

Competing hypotheses and discriminator:

- H1: one of the attributed routines writes a valid KSEG0 sample pointer into
  a voice slot.
- H2: the watched block is mixer bookkeeping/sentinel traffic and the actual
  sample/stream writer is elsewhere.
- H3: the generated/companion correlation cannot distinguish the writer, so a
  new oracle watch would be premature.

The discriminating measurement is a complete static mapping from each s1175
writer PC to its generated instruction and destination field; only a mapped
sample/stream destination authorizes the next oracle watch.

Exact commands:

    rg -n "8008EDB8|8008EE04|8008EE6C|8008F0CC|8008F0E4|8008F0EC|1496F8|149700|musyx" /Users/williambuckley/Documents/Tools/rogue_squadron64 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    rg -n "8008EDB8|8008EE04|8008EE6C|8008F0CC|8008F0E4|8008F0EC" /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/lib

Do not build or run an oracle watch unless the static table maps a writer to a
sample/stream field. If it does, the next unit must batch that watch with the
whole-RDRAM positive control and separate read/write totals.
