#!/bin/zsh
# wait for the s5429 relief hold to write its summary (max ~580 s), then print status
D=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/m6/s5429_relief
for i in $(seq 1 58); do [ -s $D/summary ] && break; /bin/sleep 10; done
cat $D/summary 2>/dev/null; tail -5 $D/keys.log; ls $D/fbd | wc -l
