#!/bin/zsh
# s7962 class PS e2e: owner folder names with spaces, non-ASCII, apostrophe, >255-char total path.
# One game at a time, 8 s each, SIGKILL; owner save copied, never written (NO_SAVE_WRITE=1).
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7962; P=${1:-new}
LONG="Rogue Squadron ü/William's Games/$(printf 'sub folder with a fairly long descriptive name %02d/' 1 2 3 4)"
mk(){ d=$1; rm -rf "$d"; mkdir -p "$d/saves"; for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt; do ln -sfn $R/build/$f "$d/$f"; done
  cp $R/build/saves/rs64.n64.us.1.0.bin "$d/saves/"; print -r -- 'ROGUESQ_S7962_PLANT=1' > "$d/settings.txt"; print -r -- '{}' > /dev/null; }
run(){ tag=$1; dir=$2; exe=$3; shift 3; L=$S/${P}_$tag.log
  ( cd "$dir" && exec env -u ROGUESQ_SETTINGS ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_NO_PKILL=1 RS64_EEP_TRACE=1 "$@" "$exe" ) > $L 2>&1 & p=$!; sleep 8; kill -9 $p 2>/dev/null; wait $p 2>/dev/null
  sym=$(grep -m1 -oE 'symtab\] (loaded [0-9]+|[^ ]+ failed)' $L); root=$(grep -m1 -oE '\[s7960-root\] data=.* \((cwd-data|exe-dir|cwd-forced|cwd-noexe)\)' $L | grep -oE '\([a-z-]+\)$')
  plant=$(grep -m1 -c 'S7962_PLANT=1(file)' $L); rom=$(grep -c 'Place' $L); eep=$(grep -m1 -oE 'b0..7=[0-9a-f ]{23}' $L); swaps=$(grep -c '^\[osViSwapBuffer' $L)
  echo "$P $tag: len=${#dir} sym=[$sym] root=$root plant=$plant rom_missing=$rom eep=[$eep] swaps=$swaps"; }
mk "$S/plain/pg"; run plain_ctl "$S/plain/pg" ./RogueSquadron64Recomp
mk "$S/$LONG"; run weird_cwd "$S/$LONG" ./RogueSquadron64Recomp
rm -rf $S/away; mkdir -p $S/away; run weird_exedir $S/away "$S/$LONG/RogueSquadron64Recomp"
rm -f "$S/$LONG/RogueSquadron64Recomp"; cp $R/build/RogueSquadron64Recomp "$S/$LONG/"; run weird_copy "$S/$LONG" ./RogueSquadron64Recomp; run weird_copy_exedir $S/away "$S/$LONG/RogueSquadron64Recomp"
# $S/away "$S/$LONG/RogueSquadron64Recomp"
rm -rf $S/away "$S/Rogue Squadron ü" $S/plain
