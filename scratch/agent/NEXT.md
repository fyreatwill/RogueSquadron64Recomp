# Next work unit: restore the M3 patch target and qualify the sentinel guard

HYPOTHESIS-ID: m3-active-queue-sentinel-predecessor

The maintenance pass compacted CURRENT-TRUTH; the next iteration returns to
the highest applicable engineering item. Do not run an M5 route permutation or
writer census in that unit.

Competing hypotheses:

- H1: the configured build graph can be repaired or is already repairable, and
  the sentinel predecessor guard can reach a MIPS/runtime qualification path.
- H2: the sentinel may legitimately carry a predecessor during a non-empty
  queue, so source inspection will require redesign before qualification.
- H3: the host still lacks the patch target/toolchain, leaving runtime
  qualification blocked despite a valid source guard.

Discriminator: inspect the active-queue append contract and build the patch
target in the same iteration. H1 requires a valid target plus a qualified
patch build; H2 requires a concrete legitimate predecessor path; H3 is the
exact build-graph/toolchain failure after the repair attempt.

Commands:

```sh
rg -n "PatchesLib|heap_guards|active_queue|heap_tail_loc" CMakeLists.txt patches build
cmake --build build --config Debug --target RogueSquadron64Recomp
cmake --build build --config Debug --target PatchesLib
```

If the target is absent, record the exact build-graph blocker and do not infer
runtime behavior from the ordinary host build.
