# Next work unit: qualify M3 patch integration on a MIPS-capable host

HYPOTHESIS-ID: m3-patch-integration

The active-sentinel predecessor guard is source- and ordinary-host-build
qualified, but runtime qualification is blocked on this macOS host because
`mips64-elf-gcc` and `mips64-elf-ld` are absent. This is the next applicable
strategic item after the M5 sink discriminator closed.

Competing hypotheses:

- Hguard-runtime: the rebuilt `PatchesLib` loads and the guard remains quiet
  on a qualified run, showing the ownership proof is compatible with runtime.
- Hguard-hit: the guard fires with an ORIGIN-tagged ownership violation,
  identifying a live heap corruption path.
- Htoolchain-block: the required MIPS compiler/linker remain unavailable, so
  runtime qualification is unevaluable and no M3 conclusion may be drawn.

Discriminating measurement: on a host that provides both tools, run
`cmake --build build --config Debug --target PatchesLib`, then the ordinary
Debug target and the qualified runtime recipe with the active-sentinel guard
enabled. A successful `PatchesLib` build plus a clean or ORIGIN-tagged guard
run selects Hguard-runtime or Hguard-hit; absent tools select Htoolchain-block.
Do not infer runtime behavior from the ordinary target alone.
