#!/bin/zsh
# s7967 class CS e2e: the save folder lives in iCloud Drive and its save is evicted to a dataless placeholder.
# Private game folder under scratch/s7967 (owner save COPIED, build/saves untouched); saves/ is a symlink into
# ~/Library/Mobile Documents/com~apple~CloudDocs/rs64_s7967_cs_probe (removed at the end). Arms, ${SECS:-25} s each, SIGKILL:
#   online   evicted, saving ON: must log "downloaded" and keep saving (no "will NOT save")
#   offline  evicted + ROGUESQ_S7967_SIM_OFFLINE=1, saving ON: must log "will NOT save (saving_was=1)" and leave the cloud save
#            byte-identical
#   mutant   as offline + ROGUESQ_S7967_CS=0 (guard off): logs "guard OFF"; reports whether the game rewrote the save
#            (rewritten = the hazard the guard prevents)
#   nosave   evicted + SIM_OFFLINE, ROGUESQ_NO_SAVE_WRITE=1: "saving_was=0"
#   local    materialised save (not a placeholder): no [s7967-cs] line at all
# Exit 0 = every arm matches. Output scratch/s7967/${P}_summary.txt.
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7967; P=${1:-new}; SECS=${SECS:-25}; mkdir -p $S; : > $S/${P}_summary.txt; bad=0
CD="$HOME/Library/Mobile Documents/com~apple~CloudDocs"; [ -d "$CD" ] || { print "no iCloud Drive: class CS moot here"; exit 3; }
T="$CD/rs64_s7967_cs_probe"; G=$S/game; SV=rs64.n64.us.1.0.bin
rm -rf $G; mkdir -p $G; for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt controls.json; do [ -e $R/build/$f ] && cp $R/build/$f $G/$f; done
rm -rf "$T"; mkdir -p "$T"; ln -s "$T" $G/saves
seed(){ cp $R/build/saves/$SV "$T/$SV"; cp $R/build/saves/$SV "$T/$SV.bak"; }
evict(){ local i; for i in $(seq 1 60); do brctl evict "$T/$SV" >/dev/null 2>&1; brctl evict "$T/$SV.bak" >/dev/null 2>&1
  [[ "$(stat -f %Sf "$T/$SV")$(stat -f %Sf "$T/$SV.bak")" == *dataless*dataless* ]] && return 0; sleep 2; done; return 1; }
h(){ [ -e "$T/$SV" ] && { brctl download "$T/$SV" >/dev/null 2>&1; shasum "$T/$SV" | cut -c1-12; } || print none; }
arm(){ local name=$1 ev=$2 want=$3 nowant=$4; shift 4; seed; local hs0=$(shasum "$T/$SV" | cut -c1-12) e=-
  [[ $ev = 1 ]] && { evict || { print "$P $name FAIL: could not evict" | tee -a $S/${P}_summary.txt; bad=1; return; }; e=$(stat -f %Sf "$T/$SV"); }
  local L=$S/${P}_$name.log; ( cd $G && exec env -u ROGUESQ_SETTINGS "$@" ROGUESQ_NO_PKILL=1 ./RogueSquadron64Recomp ) > $L 2>&1 & local p=$!
  sleep $SECS; local k=dead; kill -0 $p 2>/dev/null && k=alive; kill -9 $p 2>/dev/null; wait $p 2>/dev/null
  local cs=$(grep -m1 -o '\[s7967-cs\].*' $L | cut -c1-140); local us=$(grep -o 'update_screen #[0-9]*' $L | tail -1 | tr -dc 0-9)
  local cr=$(grep -cE 'CRASH|SIGSEGV|SIGBUS|SIGABRT|terminate called' $L); local hs1=$(h); local rw=same; [[ $hs1 != $hs0 ]] && rw=REWRITTEN
  local tl=$(ls -a "$T" | grep -c 'temp'); local ok=PASS
  [[ -n $want && "$cs" != *"$want"* ]] && ok=FAIL; [[ -n $nowant && "$cs" == *"$nowant"* ]] && ok=FAIL; [[ $name = local && -n $cs ]] && ok=FAIL
  [[ $k = alive && $cr = 0 ]] || ok=FAIL; [[ $name = offline && $rw != same ]] && ok=FAIL; [[ $ok = FAIL ]] && bad=1
  print "$P $name $ok: evict=$e $k us=${us:-0} crash=$cr save=$rw temps_left=$tl cs=[$cs]" | tee -a $S/${P}_summary.txt; }
N="ROGUESQ_NO_SAVE_WRITE=1"; Y="-u ROGUESQ_NO_SAVE_WRITE"
arm online 1 "downloaded" "will NOT save" ${=Y}
arm offline 1 "will NOT save (saving_was=1)" "" ${=Y} ROGUESQ_S7967_SIM_OFFLINE=1
arm mutant 1 "guard OFF" "" ${=Y} ROGUESQ_S7967_SIM_OFFLINE=1 ROGUESQ_S7967_CS=0
arm nosave 1 "saving_was=0" "" ${=N} ROGUESQ_S7967_SIM_OFFLINE=1
arm local 0 "" "" ${=Y}
rm -rf "$T" $G; print "$P VERDICT $([[ $bad = 0 ]] && print PASS || print FAIL)" | tee -a $S/${P}_summary.txt; exit $bad
