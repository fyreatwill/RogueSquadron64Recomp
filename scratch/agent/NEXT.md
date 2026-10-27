# NEXT: audit the DC0 target input path
HYPOTHESIS-ID: g1c-dd8-limit

Run exactly one bounded experiment. Extend the existing keyed DC0 probe so the
live `0x80042DC0` store records the base pointer, index/offset arithmetic, and
source value that produce `ctx->r21`. Retain the keyed post-table diff, DC0
target/value classification, and dd1 nonempty/dd4 EMPTY controls. Do not add a
guard or change game behavior.

Competing hypotheses and discriminator:

- H-coherent-stream: base plus index intentionally walks a larger stream
  buffer; this proves the OUT target is a legitimate-but-misjoined boundary.
- H-corrupt-input: base or index is outside the stream allocation or does not
  match the target arithmetic; this names the corrupt input writer.
- H-uninstrumented: the OUT target cannot be reconstructed from the logged
  source path; this reopens a host/uninstrumented writer.

The discriminator is exact target reconstruction from the logged base/index
path, with the active span-bound decision retained. Positive controls are
keyed rows, dd1 nonempty rows, dd4 EMPTY rows, and zero crash/VI-stall markers.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s6492_forface.sh
