# NEXT work unit — compare port producer loop-entry arguments

HYPOTHESIS-ID: m5-producer-entry-argument-qualification

The retail ground-truth route is now qualified: the whole-RDRAM control fires,
hangar `512 @ 0x006AB400` is present, and `0x800078EC` writes the target span
with nonzero values. The next unit is one regeneration-safe port witness and
one fresh-build batch containing silent and Factor 5 image arms.

Competing hypotheses and the single discriminating measurement:

- `H-PortEntryArgsMatch`: the port reaches `0x800078EC` with the same effective
  destination/length/value contract as retail, so nonzero target-span stores
  should appear in the phase-qualified first-loop rows.
- `H-PortEntryArgsZero`: the port reaches the loop with a zero or malformed
  `a0/a1/a2`/value contract, explaining its zero target span upstream of the
  RSP transform.
- `H-PortRouteMismatch`: the port's observed `0x800078EC` stores come through a
  different caller/route than retail, so entry fields differ even if the loop
  itself is correct.

The discriminator is the complete phase-qualified entry table: first
`0x800078E0`/`0x800078EC` iteration per invocation, `a0/a1/a2`, computed `v0`,
stored value, caller/return edge, and target-span classification, with bounded
rows for both port arms. A matching nonzero tuple selects
`H-PortEntryArgsMatch`; a zero/malformed tuple selects `H-PortEntryArgsZero`;
different caller/route with otherwise valid fields selects `H-PortRouteMismatch`.
Missing positive controls or missing hangar rows are unevaluable.

Before building, add the witness through the regeneration path and verify its
hook is in the fixup input:

`rg -n 'func_800078EC|L_800078EC|rs64_m5_writer_parity' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/N64Recomp/tools`

Build and run the existing two-arm contract driver after the hook is added:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3411_m5_downstream_join.sh`

Keep whole-RDRAM, title, hangar, audio ABI/DMA, image-stage, and PCM controls
armed. Do not change waits, slots, dispatch, clear behavior, or PCM writeback.
Capture the new witness under `scratch/agent/s3421_m5_entry_arguments/` and
report both arms together.
