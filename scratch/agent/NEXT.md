# NEXT: audit the full span-grid writer and initialization
HYPOTHESIS-ID: g1c-span-grid-writer

Run exactly one bounded experiment. Extend the existing keyed DC0/postring
probe to capture the full span-grid dimensions and initialization/writer
activity over `0x80130DB0..0x80132DAF`, retaining the dd1 nonempty and dd4
EMPTY keyed controls. Do not add a guard or change game behavior.

Competing hypotheses and discriminator:

- H-full-grid: initialization and writers cover the full 0x2000-byte grid;
  dd4 empty returns are a legitimate rasterizer/input result.
- H-short-init: only the first 24 bytes are initialized; later DC0 reads are
  stale or uninitialized.
- H-late-unexpected-writer: a post-rasterization writer changes sampled rows
  from an unexpected source.

The discriminating measurement is a positive initialization control plus
keyed per-writer source attribution for the same rows read by the DC0 return.
The result must report grid dimensions, writer PCs/values, and the keyed table
snapshot for dd1 nonempty and dd4 EMPTY rows. A null is invalid unless the
full-grid initialization control visibly fires in the same run.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s6511_span_grid.sh
