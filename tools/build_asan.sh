#!/bin/zsh
# Build an AddressSanitizer + UndefinedBehaviorSanitizer arm of the recomp in build_asan/ (separate from build/).
# Usage: tools/build_asan.sh   (run from anywhere; needs Xcode for Metal)
# Run the result from build_asan/ with the ROM beside it, same as build/.
# s7467 class DW: like build_tsan.sh, only C++ is instrumented (host runtime, RT64, RSP bridge, main); the generated C
# (RecompiledFuncs) and the RSP ucode TUs (CMakeLists, ROGUESQ_ASAN_UCODE=ON to instrument) are not: guest memory is one
# host map, so ASan cannot see guest-side overruns there. Recoverable (-fsanitize-recover): run with
# s7468 class DY: UCODE=1 (DEFAULT since s7468: flight reached, 0 ucode reports) sets ROGUESQ_ASAN_UCODE=ON (plant ROGUESQ_S7468_UCODE_PLANT=1),
# UCODE=0 restores the s7467 exemption. B=<dir> overrides the build dir (default build_asan). Only the 6 ucode TUs rebuild.
# ASAN_OPTIONS=halt_on_error=0 so every report is logged and the arm keeps flying. Planted control: ROGUESQ_S7467_ASAN_PLANT=1.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
FLAGS="-O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -fsanitize-recover=address,undefined"
LF="-fsanitize=address,undefined"
B=${B:-build_asan}; UC=OFF; [[ ${UCODE:-1} == 1 ]] && UC=ON
cmake -S . -B $B -DCMAKE_BUILD_TYPE=Debug -DROGUESQ_ASAN_UCODE=$UC \
  -DCMAKE_C_FLAGS_DEBUG="-O1 -g -fno-omit-frame-pointer" -DCMAKE_CXX_FLAGS_DEBUG="$FLAGS" \
  -DCMAKE_EXE_LINKER_FLAGS="$LF"
cmake --build $B -j"${JOBS:-10}"
ln -sf "$PWD/rogue_squadron.z64" $B/rogue_squadron.z64 2>/dev/null || true
# Configuring a second build dir drops build/'s spirv-cross subproject rules (s5598, s7354); regenerate them so build/ stays green.
cmake -S . -B build > /dev/null
