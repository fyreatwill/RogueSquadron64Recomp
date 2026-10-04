# Next work unit: measure the qualified M5 `0x800052C4` source-writer class

HYPOTHESIS-ID: m5-source-writer-052c4

The M3 runtime qualification remains externally blocked: this host has no MIPS
GCC/LD and Clang has no MIPS backend. Do not repeat that target build. Session
4054 qualified only the isolated declared-real arm; declared-silent and
legacy-real crashed before target phases and cannot support a writer null.

Competing hypotheses:

- H1: retail's `0x800052C4` execution class writes the nonzero source payload
  that the qualified port route lacks.
- H2: retail executes the class but its stores are zero/metadata-only, so the
  missing nonzero source is produced elsewhere.
- H3: the class is not target-phase equivalent between retail and port, so the
  comparison is invalid until a different qualified callsite is identified.

Discriminator: the retail oracle must pass whole-RDRAM, title, and hangar
controls and report phase-gated execution/store rows for `0x800052C4`,
`0x800052C8`, and `0x800052CC`; the declared-real port arm must reach both
target phases and retain its zero-payload signature. Nonzero scalar stores from
the retail class select H1; only zero/metadata stores with valid target-phase
execution select H2; a missing target-phase retail class or failed port route
leaves H3/unevaluable. The same run must include all three callsites and both
phase buckets; do not infer a null from a pre-target crash.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s4037_m5_candidate_writers.sh
grep -nE 'positive-control|post-store-scalar|052c4|origin=0x00790400|origin=0x006ab400|audtask-image-dma-join|CRASH|ABORT' \
  scratch/agent/s4037_m5_candidate_writers/driver.log | tail -240
```

The M3 toolchain dependency remains open until a MIPS host produces
`patches.elf`, `RecompiledPatches/patches.c`, and `PatchesLib`.
