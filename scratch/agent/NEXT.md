# NEXT work unit (s1020)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Perform one bounded source/build-graph audit and smallest integration change
for the probe-bearing ovl20 path. Do not launch the game until the active
overlay controls pass. s1020 showed that the composite source and shared probe
helper are now linked, but CMake still compiles only base/boot/B ucode and has
no ovl20 object or executable ovl20 marker.

Competing hypotheses and discriminator:

- `H-ovl20-dispatch-generated`: the scripts intentionally generate per-overlay
  implementations and the missing link/dispatch entry is the only defect.
- `H-ovl20-unused-source`: ovl20 is diagnostic-only or superseded, so adding it
  to the link would create a duplicate or dead implementation.
- `H-runtime-unreached`: the active overlay controls are complete after the
  integration change, but a phase-gated capture still has zero M4 and
  VMADH-control rows.

The discriminating measurement is the source-to-dispatch table after the
smallest integration change: generation ownership, CMake source/object,
linked symbol, and active overlay registration. A linked ovl20 object or an
explicit source splice selects `H-ovl20-dispatch-generated`; a duplicate/dead
path selects `H-ovl20-unused-source`. If all active-overlay controls pass, run
the existing s1018 recipe with its full passive instrumentation and compare
VI-1024, VMADH-control, and M4-row counts in one capture.

Commands:

    rg -n "FACTOR5_UCODE|ovl20|factor5_ucode_recompiled" CMakeLists.txt tools build/factor5_ucode
    cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
    cmake --build build --target RogueSquadron64Recomp -j4
    nm -gU build/RogueSquadron64Recomp | rg "rs64_m4_accum_probe|factor5_ucode|ovl20"
    find build/CMakeFiles/RogueSquadron64Recomp.dir -type f | rg "factor5.*ovl20|factor5_ucode"

If the active-overlay controls pass, reuse the exact s1018 phase/input
environment, launch from `build/`, capture to a non-dot final path, and
terminate with SIGKILL. Otherwise do not launch; record the selected artifact
hypothesis.
