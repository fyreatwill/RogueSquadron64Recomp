#!/bin/zsh
# s7961 e2e: which settings.txt does a launch read? one game at a time, 6 s each, SIGKILL; owner save never written.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7961; mkdir -p $S; P=${1:-new}
rm -rf $S/pg; mkdir -p $S/pg/saves; cd $S/pg
for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt controls.json; do [ -e $R/build/$f ] && ln -sfn $R/build/$f $f; done
cp $R/build/saves/rs64.n64.us.1.0.bin saves/; echo 'ROGUESQ_S7961_PLANT=1' > settings.txt
run(){ tag=$1; dir=$2; exe=$3; shift 3; ( cd $dir && exec env -u ROGUESQ_SETTINGS ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_NO_PKILL=1 "$@" $exe ) > $S/${P}_$tag.log 2>&1 & p=$!; sleep 6; kill -9 $p 2>/dev/null; wait $p 2>/dev/null
  echo "$P $tag: $(grep -m1 '\[s7663\] settings file=' $S/${P}_$tag.log | sed 's|'$R'/||g') | $(grep -m1 -o 'S7961_PLANT=1(file)' $S/${P}_$tag.log || echo noplant)"; }
run symlink_pg $S/pg ./RogueSquadron64Recomp
run owner_build $R/build ./RogueSquadron64Recomp
run repo_root $R build/RogueSquadron64Recomp
rm -rf $S/away; mkdir -p $S/away
run away_empty $S/away $R/build/RogueSquadron64Recomp
run forced_cwd $S/away $R/build/RogueSquadron64Recomp ROGUESQ_DATA_ROOT=cwd
rm -rf $S/away
