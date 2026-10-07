# Next work unit: qualify the pre-publication free/active ownership guard

HYPOTHESIS-ID: m3-free-active-prepublication

The next M5 status-03 behavior edge is not safe to land here: the generated
worker/store implementation is external to this checkout and the current
truth explicitly forbids a force-clear or wait replacement without that
contract. This iteration instead audits one complete M3 ownership idiom in
`patches/heap_guards.c`: reject a free-list/active-queue overlap before
publishing the advanced free-list head.

Competing hypotheses and discriminator:

- H-overlap-prevented: the new pre-publication check is compiled into the
  regeneration-safe patch and rejects only the non-legitimate overlap class.
- H-guard-not-integrated: the patch source changes but the configured build
  omits or cannot compile `PatchesLib`, so runtime behavior is not qualified.
- H-guard-too-broad: a valid allocator path is rejected; this requires a
  runtime qualification on a host with the MIPS toolchain.

The single discriminating measurement is the build/link artifact check:
`PatchesLib` must compile and the full Debug target must link the override.
Successful integration selects H-overlap-prevented pending runtime
qualification; omission or missing cross-compiler selects H-guard-not-
integrated; only a qualified runtime rejection can select H-guard-too-broad.

Commands:

1. Build the patch and full target once:
   `cmake --build build --config Debug --target PatchesLib`
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Inspect the generated patch/build dependency and link result. A runtime
   soak is not authorized if the cross-toolchain is absent.

Expected outcomes: `PatchesLib` is rebuilt and the ordinary Debug target links,
or the build reports the known missing MIPS GCC/LD dependency; in either case
do not infer runtime guard firing from a build-only result.
