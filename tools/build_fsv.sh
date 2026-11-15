#!/bin/zsh
# s7410 class BT: callee-saved preservation probe build in build_fsv/ (separate from build/). Transforms a copy of
# ../N64Recomp/RecompiledFuncs into build_fsv/fsv_src (tools/s7410_fsv_transform.py) and points RECOMP_FUNCS_DIR at it.
# Run from build_fsv/ with the ROM beside it; env ROGUESQ_S7410_PLANT=1 arms the positive control.
# Report: tools/s7410_fsv_report.py <log>.
set -e
cd "${0:A:h}/.."
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
D=build_fsv
python3 tools/s7410_fsv_transform.py ../N64Recomp/RecompiledFuncs $D/fsv_src
cmake -S . -B $D -DCMAKE_BUILD_TYPE=Debug -DRECOMP_FUNCS_DIR=$PWD/$D/fsv_src
cmake --build $D -j"${JOBS:-12}"
ln -sf "$PWD/rogue_squadron.z64" $D/rogue_squadron.z64 2>/dev/null || true
# Configuring a second build dir drops build/'s spirv-cross subproject rules (s5598, s7354); regenerate them.
cmake -S . -B build > /dev/null
# s7409: the forced-mission route needs the owner's save beside the binary (a COPY; build/saves is never touched). Without
# it the game boots profile-less and START is ignored in the 768 phase (5/5 nomission, first s7409 attempt).
[ -f $D/saves/rs64.n64.us.1.0.bin ] || { mkdir -p $D/saves; cp build/saves/rs64.n64.us.1.0.bin $D/saves/; }
