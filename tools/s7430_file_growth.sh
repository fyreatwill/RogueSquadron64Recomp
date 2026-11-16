#!/bin/zsh
# s7430 class CM runtime half: which files does an owner-recipe run (no logging env) create or grow, run after run?
# Copied game folder per arm (owner save copied, never touched; ROGUESQ_NO_SAVE_WRITE=1 as runner.sh sets it).
#   O   OLD binary (S7430_OLD=<path>, pre-fix) owner recipe   -> before arm (expect ucode_024A10.bin created)
#   R1  new binary owner recipe, R2 same folder again          -> H-bounded iff R1 and R2 create/grow nothing
#   G   new + ROGUESQ_DUMP_UCODE_BIN=1                         -> positive control: the gated writer fires, detector sees it
#   K   planted 300 KiB rs64_s6892.log, new binary             -> rotated to rs64_s6892.log.1 at start
#   KN  same + ROGUESQ_S7430_NO_ROTATE=1                       -> stays (old behaviour), control for K
# Exit 0 = H-bounded + fixes verified, 1 = growth/drift, 3 = control failed.
ROOT=${0:A:h:h}; B=/tmp/rs64_s7430; T=${S7430_SECS:-40}; rc=0
mk() { rm -rf $B/$1; mkdir -p $B/$1/saves; cp ${2:-$ROOT/build/RogueSquadron64Recomp} $B/$1/RogueSquadron64Recomp
  cp $ROOT/build/rogue_squadron.z64 $ROOT/build/rs64.n64.us.1.0.z64 $B/$1/ 2>/dev/null; cp $ROOT/build/saves/rs64.n64.us.1.0.bin $B/$1/saves/; }
snap() { (cd $B/$1 && find . -type f ! -name '*.runlog' ! -name 'snap_*' ! -name RogueSquadron64Recomp -exec stat -f '%N %z' {} + | sort) > $B/$1/snap_$2.txt; }
run() { local d=$1 n=$2; shift 2
  (cd $B/$d && env ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 "$@" ./RogueSquadron64Recomp > $B/$d/$n.runlog 2>&1) &
  local pid=$!; sleep $T; pkill -9 -f "^./RogueSquadron64Recomp"; wait $pid 2>/dev/null; snap $d $n; }
delta() { comm -13 $B/$1/snap_$2.txt $B/$1/snap_$3.txt | tr '\n' ' '; }
mkdir -p $B; [[ -n $S7430_OLD ]] && { mk O $S7430_OLD; snap O 0; run O 1; print -r -- "O  (old) new/changed: $(delta O 0 1)"; }
mk R; snap R 0; run R 1; run R 2
r1=$(delta R 0 1); r2=$(delta R 1 2); print -r -- "R1 new/changed: [$r1]"; print -r -- "R2 new/changed: [$r2]"
[[ -z $r1 && -z $r2 ]] || rc=1
mk G; snap G 0; run G 1 ROGUESQ_DUMP_UCODE_BIN=1; g=$(delta G 0 1); print -r -- "G  new/changed: [$g]"
[[ $g == *ucode_024A10.bin* ]] || { print "CONTROL FAIL (G: gated writer not seen)"; exit 3; }
for a in K KN; do mk $a; head -c 307200 /dev/zero | tr '\0' 'x' > $B/$a/rs64_s6892.log; snap $a 0
  if [[ $a = K ]]; then run $a 1; else run $a 1 ROGUESQ_S7430_NO_ROTATE=1; fi
  print -r -- "$a files: $(cat $B/$a/snap_1.txt | grep s6892 | tr '\n' ' ') | $(grep -a -m1 '\[s7430\]' $B/$a/1.runlog)"; done
grep -q 'rs64_s6892.log.1 307200' $B/K/snap_1.txt && ! grep -q '^./rs64_s6892.log ' $B/K/snap_1.txt || rc=1
grep -q '^./rs64_s6892.log 307200' $B/KN/snap_1.txt && ! grep -q 'log.1' $B/KN/snap_1.txt || { print "CONTROL FAIL (KN)"; exit 3; }
print "VERDICT $([[ $rc = 0 ]] && print H-bounded || print H-growth/drift)"; exit $rc
