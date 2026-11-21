#!/bin/zsh
# s7738: link the live build/ objects against a RecompiledFuncs library compiled from a
# different tree (default: the s7736 regen replay, built by
#   cmake -S . -B build_replay -DRECOMP_FUNCS_DIR=$PWD/scratch/s7736/gate/replay
#   cmake --build build_replay --target RecompiledFuncs -j2)
# Output: build_replay/RogueSquadron64Recomp. Never writes into build/.
# Usage: zsh tools/s7738_link_replay.sh [lib.a] [out]
set -e
R=${0:A:h}/..
R=${R:A}
LIB=${1:-$R/build_replay/libRecompiledFuncs.a}
OUT=${2:-$R/build_replay/RogueSquadron64Recomp}
[[ -s $LIB ]] || { echo "no lib $LIB"; exit 3; }
cmd=$(sed -e "s| -o RogueSquadron64Recomp | -o $OUT |" -e "s| libRecompiledFuncs.a | $LIB |" \
      $R/build/CMakeFiles/RogueSquadron64Recomp.dir/link.txt)
[[ $cmd == *" -o $OUT "* && $cmd == *" $LIB "* ]] || { echo "link.txt substitution failed"; exit 4; }
cd $R/build
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
eval "$cmd"
echo "linked $OUT"
