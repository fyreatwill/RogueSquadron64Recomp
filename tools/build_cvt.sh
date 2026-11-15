#!/bin/zsh
# s7408 class BR: per-site FP->int conversion census build in build_cvt/ (separate from build/). Transforms a copy of
# ../N64Recomp/RecompiledFuncs into build_cvt/cvt_src (tools/s7408_cvt_transform.py) and points RECOMP_FUNCS_DIR at it.
# Run from build_cvt/ with the ROM beside it; env ROGUESQ_S7408_PLANT=1 arms the positive control.
# Report: tools/s7408_cvt_report.py <log>.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
D=build_cvt
python3 tools/s7408_cvt_transform.py ../N64Recomp/RecompiledFuncs $D/cvt_src
cmake -S . -B $D -DCMAKE_BUILD_TYPE=Debug -DRECOMP_FUNCS_DIR=$PWD/$D/cvt_src
cmake --build $D -j"${JOBS:-12}"
ln -sf "$PWD/rogue_squadron.z64" $D/rogue_squadron.z64 2>/dev/null || true
# Configuring a second build dir drops build/'s spirv-cross subproject rules (s5598, s7354); regenerate them.
cmake -S . -B build > /dev/null
