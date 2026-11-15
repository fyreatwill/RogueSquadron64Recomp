#!/bin/zsh
# s7389: framebuffer-load-watch arm in build_fbld/ (separate from build/). Same flags as build/ plus
# -DROGUESQ_FB_LDWATCH=ON (include/fbld/recomp.h wraps guest MEM_* accesses). Run from build_fbld/ with the ROM beside it,
# env ROGUESQ_S7389_FBLD=1 [ROGUESQ_S7389_CTL=130000:138000]. Report: tools/s7389_fbld_report.py <log>.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
D=build_fbld
cmake -S . -B $D -DCMAKE_BUILD_TYPE=Debug -DROGUESQ_FB_LDWATCH=ON
cmake --build $D -j"${JOBS:-12}"
ln -sf "$PWD/rogue_squadron.z64" $D/rogue_squadron.z64 2>/dev/null || true
# Configuring a second build dir drops build/'s spirv-cross subproject rules (s5598, s7354); regenerate them.
cmake -S . -B build > /dev/null
