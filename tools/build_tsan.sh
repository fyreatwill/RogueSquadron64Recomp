#!/bin/zsh
# s7354: ThreadSanitizer arm of the recomp in build_tsan/ (separate from build/).
# Only C++ (host runtime, RT64, RSP bridge, main) is instrumented; the generated C (RecompiledFuncs) and the RSP ucode TUs
# (compiled as CXX, exempted in CMakeLists.txt since s7369, ROGUESQ_TSAN_UCODE=ON to instrument) are not,
# so guest-memory traffic is not traced (guest threads are serialized by ultramodern; RDRAM sharing with the RSP is by design).
# Usage: tools/build_tsan.sh   Run the result from build_tsan/ with the ROM beside it, same as build/.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
FLAGS="-O1 -g -fno-omit-frame-pointer -fsanitize=thread"
cmake -S . -B build_tsan -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_FLAGS_DEBUG="-O1 -g -fno-omit-frame-pointer" -DCMAKE_CXX_FLAGS_DEBUG="$FLAGS" \
  -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=thread"
cmake --build build_tsan -j"${JOBS:-10}"
ln -sf "$PWD/rogue_squadron.z64" build_tsan/rogue_squadron.z64 2>/dev/null || true
# Configuring a second build dir drops build/'s spirv-cross subproject rules (s5598, s7354); regenerate them so build/ stays green.
cmake -S . -B build > /dev/null
