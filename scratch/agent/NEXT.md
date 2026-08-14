# NEXT work unit (s1019)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Perform one bounded build-and-artifact validation, then (only if the controls
pass) one corrected 1024-gated M4 capture. The s1019 audit selected
`H-stale-build-link`: `factor5_ucode_ovl20_recompiled.c` contains the probe, but
it was newer than the executable; CMake compiles only base/boot/B ucode and
`build/RogueSquadron64Recomp` contains neither the probe symbol nor ovl20.

Competing hypotheses and discriminator:

- `H-fixup-splice`: reconfiguration reruns the fixup and inserts the current
  ovl20 probe calls into the main generated ucode, after which the executable
  contains the probe string.
- `H-fixup-not-rerun`: the build remains stale or fixup does not splice the
  current ovl20 source; the main source and executable remain probe-free.
- `H-runtime-unreached`: source, main composite, and executable controls all
  pass, but a phase-gated capture still has zero M4 and VMADH-control rows.

The discriminating measurement is the complete artifact table before running:
ovl20 source probe calls, main generated-source probe calls, executable probe
string, and build timestamps. Missing main/executable controls selects
`H-fixup-not-rerun`; all controls positive followed by zero runtime rows
selects `H-runtime-unreached`. If controls pass, run the existing s1018 recipe
with its full passive instrumentation and compare VI-1024, VMADH-control, and
M4-row counts in one capture.

Commands:

    cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
    cmake --build build --target RogueSquadron64Recomp -j4
    rg -n "rs64_m4_accum_probe|ROGUESQ_LOG_M4_ACCUM" build/factor5_ucode/factor5_ucode_recompiled.c build/factor5_ucode/factor5_ucode_ovl20_recompiled.c
    strings build/RogueSquadron64Recomp | rg "rs64_m4_accum_probe|M4_ACCUM|factor5_ucode_ovl20"

Do not launch the game if either generated-source or executable controls are
missing. If all controls pass, reuse the exact s1018 phase/input environment
and launch from `build/`, capture to a non-dot final path, and terminate with
SIGKILL.
