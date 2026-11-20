#!/bin/zsh
# s7694 G5c freeze gate on post-G6c binary: 900 s STANDINS=1 dd4 owner recipe, L4 and L12, SIGSTOP 400 ms positive control at t~700.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
for L in 4 12; do
  S=$PWD/scratch/s7694/L$L; rm -rf $S; mkdir -p $S
  ( /bin/sleep 700; p=$(pgrep -x RogueSquadron64Recomp | head -1); [ -n "$p" ] && { python3 -c 'import time;print(f"{time.time():.3f}")' > $S/ctl_wall; kill -STOP $p; /bin/sleep 0.4; kill -CONT $p; } ) & cp=$!
  env R=$S HOLD=900 ALLOW_SLOW=1 ARMS="4:rL$L:ROGUESQ_STANDINS=1+ROGUESQ_STANDINS_LOG=1+ROGUESQ_FORCE_SAVE_MISSION=$L" zsh tools/g1e_owner_quiet_arms.zsh > $S/out.txt 2>&1
  echo "L$L rc=$?" >> $PWD/scratch/s7694/rc.txt; wait $cp 2>/dev/null
done
