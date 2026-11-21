#!/bin/zsh
# s7739: adopt a fresh regen replay as the LIVE RecompiledFuncs tree (hard order make_elf -> N64Recomp -> fixup chain -> cmake),
# so hand-drift in the live tree (stale hooks, duplicated blocks, orphan chunks, dropped data_gap funcs) cannot accumulate.
#   1. back up the live tree (outside git) to <work>/live_backup and build/RogueSquadron64Recomp to <work>/live_binary_backup
#   2. tools/s7719_regen_gate.py --keep <work>/gate   (regen_front + regen_replay + drift census; must print H-mirrored)
#   3. optional REF=<older replay dir>: the new replay must be byte-identical to it (H-clean) or the script stops (H-new-drift)
#   4. replace every top-level *.c/*.h/*.cpp of the live tree with the replay's (live-only *.c removed; other dirs untouched)
#   5. diff -rq live vs replay restricted to sources must be empty, then cmake --build build -j2
# Restore: rsync -a <work>/live_backup/ ../N64Recomp/RecompiledFuncs/ (and delete replay-only files), rebuild.
# Usage: zsh tools/s7739_adopt_replay.sh <work dir> [REF=dir via env]   rc 0 ok, 1 drift/mismatch, 3 chain/build fail
set -u
R=${0:A:h}/..; R=${R:A}; cd $R
W=${1:?usage: s7739_adopt_replay.sh <work dir>}; W=${W:A}
L=${LIVE:-$R/../N64Recomp/RecompiledFuncs}; L=${L:A}
mkdir -p $W
[[ -d $W/live_backup ]] && { echo "refusing: $W/live_backup exists (pick a new work dir)"; exit 3; }
rsync -a $L/ $W/live_backup/ || exit 3
[[ -f build/RogueSquadron64Recomp ]] && cp -p build/RogueSquadron64Recomp $W/live_binary_backup
python3 tools/s7719_regen_gate.py --keep $W/gate > $W/gate.out 2>&1; grc=$?
tail -1 $W/gate.out
(( grc == 0 )) || { echo "gate rc $grc: not adopting"; exit $(( grc == 1 ? 1 : 3 )); }
N=$W/gate/replay
if [[ -n ${REF:-} ]]; then
  n=$(diff -r $REF $N | wc -l | tr -d ' ')
  (( n == 0 )) || { echo "H-new-drift: replay differs from REF by $n lines"; exit 1; }
  echo "H-clean: replay byte-identical to $REF"
fi
setopt null_glob
for f in $L/*.(c|h|cpp); do [[ -e $N/${f:t} ]] || { echo "remove live-only ${f:t}"; rm -f $f; }; done
for f in $N/*.(c|h|cpp); do cp -p $f $L/; done
d=$(diff -rq $L $N | grep -v '^Only in '$L': ' | wc -l | tr -d ' ')
extra=$(for f in $L/*.(c|h|cpp); do [[ -e $N/${f:t} ]] || echo x; done | wc -l | tr -d ' ')
(( d == 0 && extra == 0 )) || { echo "copy mismatch d=$d extra=$extra"; exit 3; }
echo "live tree == replay (sources)"
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j2 > $W/build.out 2>&1 || { echo "build failed, see $W/build.out"; exit 3; }
echo "built: $(tail -1 $W/build.out)"
