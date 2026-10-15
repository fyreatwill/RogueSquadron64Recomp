# Next work unit

HYPOTHESIS-ID: m5-retail-aux-byte-watch-boundary

Run one phase-gated retail oracle watch-boundary experiment for physical
`0x00149702`, using an aligned range around the odd byte. Keep the existing
whole-RDRAM, `0x000A1778`, and `0x00149988:0x0014998C` controls in the same
run. Do not change the port or rewrite values.

Competing hypotheses and discriminator:

1. H-alignment-boundary: the retail write to odd physical `0x00149702` is
   real, but the exact one-byte watch/store-field path requires an aligned
   containing range.
2. H-no-retail-write: retail reaches the other synth stores but never writes
   this byte in the selected phase.
3. H-phase-route-mismatch: the prior null was caused by the target phase or
   driven route not being the writer's active phase.

The discriminating measurement is one same-run table of watch hits, writer
PCs, and phase buckets for the aligned range plus the three positive controls.
H-alignment-boundary is selected if the aligned range fires at `0x800917C4`;
H-no-retail-write if whole-RDRAM and the other target controls fire but the
aligned range remains empty in the qualified phase; H-phase-route-mismatch if
the target phase itself is absent.

Run from the repo root:

    env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 75 --vi-poll --watch-write 0x0:0x800000 --watch-write 0x000A1778:0x000A177C --watch-write 0x00149700:0x00149704 --watch-write 0x00149988:0x0014998C --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --store-field-dump-all 2 --first-watch 0

The positive-control table must show whole-RDRAM writes and target-store rows
before the byte-watch null is interpreted. No mitigation or soak is authorized.
