#!/bin/zsh
# s6816 (copy of s6814 seeds.sh, bolt rows): seed spread of lvl14 passive-player death time, 30 Hz (dt 1/30) vs FPS60 (dt 1/60). One-shot rngSeed poke on
# the first mission tick; per-tick player object dump. Sequential (one game at a time).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
M=800FA730:0:8010C9E0:18,800FA730:0:80137DB0:64
AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,50:start
for s in 1 2 3; do for arm in a30 b60; do
  O=scratch/s6816/${arm}_s$s
  if [ $arm = a30 ]; then F=""; PIN=800FA730:29:30:3d088889; else F="ROGUESQ_FPS60=1"; PIN=800FA730:29:30:3c888889; fi
  env SAVE_FROM=scratch/s6767/lvl14.eep SECS=${SECS:-215} CAP0=9999 AP=$AP \
    XE="$F ROGUESQ_STORE_DIAG=1 ROGUESQ_DEBUG_WRITE=80003470:1:512:55 ROGUESQ_RAND_TRACE=$PWD/$O.rand.txt ROGUESQ_XTRACE_MEM=$M ROGUESQ_XTRACE_POKE=$PIN,800FA730:0:80003470:$((1000+s*7919)):1" \
    zsh tools/g3_port_capture.sh $O
  echo "$arm s$s rc=$? crash=$(grep -c -i 'crash\|abort\|SIGSEGV' $O/run.log)"
done; done
