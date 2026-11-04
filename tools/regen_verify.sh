#!/bin/zsh
# s6864: does a regen tree still build the code the live tree builds? Compiles both trees with the live build's flags and
# compares per function (tools/regen_obj_compare.py). -mno-outline and __LINE__=0 stop a change elsewhere in a file from
# showing up in unchanged functions. Never writes to the live tree or build/.
# usage: tools/regen_verify.sh <regen dir> <out dir>   (regen dir: output of tools/regen_replay.sh)
# Then read every differing function: docs/REGEN-VERIFY.md has the s6864 baseline.
cd "$(dirname "$0")/.." || exit 2
R=${1:A}; O=${2:A}; L=$PWD/../N64Recomp/RecompiledFuncs; F=build/CMakeFiles/RecompiledFuncs.dir/flags.make
[ -d "$R" ] && [ -n "$2" ] || { echo "usage: $0 <regen dir> <out dir>"; exit 2; }
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
for t in live:$L regen:$R; do
  n=${t%%:*}; D=${t#*:}; rm -rf $O/o_$n; mkdir -p $O/o_$n
  { grep -E '^C_(FLAGS|DEFINES|INCLUDES) *=' $F | sed 's/^[^=]*= *//' | tr '\n' ' ' | sed 's#-I[^ ]*N64Recomp/RecompiledFuncs##g'
    echo " -I$D -mno-outline -Wno-builtin-macro-redefined -D__LINE__=0 -c"; } > $O/o_$n/cc.rsp
  ls $D/funcs_*.c | (cd build && xargs -P 6 -I{} zsh -c 'f={}; cc @$0/cc.rsp $f -o $0/${f:t}.o > $0/${f:t}.out 2>&1; echo "$? ${f:t}" >> $0/rc.txt' $O/o_$n)
  echo "$n: files $(wc -l < $O/o_$n/rc.txt) failed $(grep -vc '^0 ' $O/o_$n/rc.txt)"
  grep -v '^0 ' $O/o_$n/rc.txt | head; grep -v '^0 ' $O/o_$n/rc.txt > /dev/null && exit 1
done
python3 tools/regen_obj_compare.py $O/o_live $O/o_regen $O/compare.json
