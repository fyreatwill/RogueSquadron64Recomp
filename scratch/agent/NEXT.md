# Next work unit: qualify the M3 pre-publication ownership guard

HYPOTHESIS-ID: m3-prepublication-guard-runtime

The status-03 join is complete at single-source port scope; do not repeat it.
Runtime qualification of the checked-in M3 guard requires a host with the MIPS
GCC/LD toolchain, so first perform the one allowed environment discriminator.

Competing hypotheses and discriminator:

- H-m3-toolchain-present: `mips64-elf-gcc` and `mips64-elf-ld` are available and
  the configured `PatchesLib` target can be built.
- H-m3-toolchain-absent: one or both cross tools are unavailable, so runtime
  guard qualification cannot run on this host.
- H-m3-target-missing: the tools exist but this CMake graph still has no
  `PatchesLib` target; no runtime guard conclusion is allowed.

The single discriminating measurement is command/tool discovery plus
`cmake --build build --config Debug --target PatchesLib`. Tool presence and a
successful target build select H-m3-toolchain-present; missing tools select
H-m3-toolchain-absent; `No rule to make target PatchesLib` selects
H-m3-target-missing. Do not infer runtime behavior from the ordinary target.

Exact commands: `command -v mips64-elf-gcc; command -v mips64-elf-ld`; then
the PatchesLib build above. If the tools and target are available, the next
iteration must run one valid-path and one overlap case; otherwise record the
environment blocker and pivot to the paired M5 source-producer route repair.
