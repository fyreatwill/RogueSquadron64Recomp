#!/bin/zsh
# s7357 class AH runtime arms: short save file. Runs the game from its OWN working folder (config_path = cwd) with a COPY of
# the owner save, so build/saves is never touched (owner save rule); ROGUESQ_NO_SAVE_WRITE stays set.
#   ctl   : full 512-byte copy   -> boots, NO "[s7357-io] save file short"
#   short : first 100 bytes only -> boots, "[s7357-io] save file short: read 100 of 512" (pre-fix: silent, tail = stale/0)
# usage: zsh tools/s7357_arms.zsh
R=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp; S=$R/scratch/s7357
arm(){ local wd=$S/wd_$1; rm -rf $wd; mkdir -p $wd/saves
  for f in rs64.n64.us.1.0.z64 rogue_squadron.z64; do ln -s $R/build/$f $wd/$f; done
  head -c $2 $R/build/saves/rs64.n64.us.1.0.bin > $wd/saves/rs64.n64.us.1.0.bin
  ( cd $wd && env ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_NO_PKILL=1 ROGUESQ_LOG_PHASE=1 $R/build/RogueSquadron64Recomp > $S/$1.log 2>&1 & echo $! > $S/$1.pid; wait ) &
  sleep 20; local P=$(cat $S/$1.pid); ps -p $P >/dev/null && st=alive || st=exited; kill -9 $P 2>/dev/null; sleep 1
  cmp -s $wd/saves/rs64.n64.us.1.0.bin <(head -c $2 $R/build/saves/rs64.n64.us.1.0.bin) && sv=unchanged || sv=CHANGED
  echo "$1 $st short=$(grep -a -c '\[s7357-io\] save file short' $S/$1.log) io=$(grep -a -c '\[s7357-io\]' $S/$1.log) segv=$(grep -a -c 'caught signal' $S/$1.log) vi=$(grep -a -c -i '\[phase\]\|vi ' $S/$1.log) wdsave=$sv"
  grep -a '\[s7357-io\]' $S/$1.log | head -3; }
shasum $R/build/saves/rs64.n64.us.1.0.bin
arm ctl 512; arm short 100
shasum $R/build/saves/rs64.n64.us.1.0.bin
