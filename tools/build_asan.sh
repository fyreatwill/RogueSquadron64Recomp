#!/bin/zsh
# Build an AddressSanitizer arm of the recomp in build_asan/ (separate from build/).
# Usage: tools/build_asan.sh   (run from anywhere; needs Xcode for Metal)
# Run the result from build_asan/ with the ROM beside it, same as build/.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
FLAGS="-O1 -g -fno-omit-frame-pointer -fsanitize=address"
cmake -S . -B build_asan -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_FLAGS_DEBUG="$FLAGS" -DCMAKE_CXX_FLAGS_DEBUG="$FLAGS" \
  -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=address"
cmake --build build_asan -j"$(sysctl -n hw.ncpu)"
ln -sf "$PWD/rogue_squadron.z64" build_asan/rogue_squadron.z64 2>/dev/null || true
