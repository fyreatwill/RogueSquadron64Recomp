#!/bin/zsh
# s7391: guest stack low-water arm in build_spwm/ (separate from build/). Same flags as build/ plus
# -DROGUESQ_SP_WATCH=ON (include/spwm/recomp.h checks every generated $sp adjust). Run from build_spwm/ with the ROM beside it,
# env ROGUESQ_S7391_SPWM=1. Report: tools/s7391_spwm_report.py <log>.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
D=build_spwm
cmake -S . -B $D -DCMAKE_BUILD_TYPE=Debug -DROGUESQ_SP_WATCH=ON
cmake --build $D -j"${JOBS:-12}"
ln -sf "$PWD/rogue_squadron.z64" $D/rogue_squadron.z64 2>/dev/null || true
# Configuring a second build dir drops build/'s spirv-cross subproject rules (s5598, s7354); regenerate them.
cmake -S . -B build > /dev/null
