#!/bin/zsh
# s7963 class AN e2e: foreground / hidden 60 s (System Events visible=false) / shown / SIGSTOP 5 s + CONT. Private game dir, owner save copied, never written.
# usage: zsh tools/s7963_an_e2e.zsh [tag]  -> scratch/s7963/<tag>{.log,_pring.txt,_events.txt}; score: python3 tools/s7963_an_gate.py scratch/s7963/<tag>
R=$(cd "$(dirname $0)/.." && pwd); S=$R/scratch/s7963; G=$S/game; T=${1:-an}
rm -rf $G; mkdir -p $G/saves; for f in RogueSquadron64Recomp rs64.n64.us.1.0.z64 audio_device.txt; do ln -sfn $R/build/$f $G/$f; done
cp $R/build/saves/rs64.n64.us.1.0.bin $G/saves/
L=$S/${T}.log; PR=$S/${T}_pring.txt; EV=$S/${T}_events.txt; : > $EV
ev(){ print -r -- "$(python3 -c 'import time;print("%.6f"%time.monotonic())') $*" >> $EV; }
( cd $G && exec env -u ROGUESQ_SETTINGS ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_NO_PKILL=1 ROGUESQ_PRESENT_RING=$PR ./RogueSquadron64Recomp ) 2>&1 | perl -MTime::HiRes=clock_gettime -ne '$|=1; printf "%.6f %s", clock_gettime(Time::HiRes::CLOCK_UPTIME_RAW()), $_' > $L &
sleep 2; P=$(pgrep -nf "$G/RogueSquadron64Recomp|^./RogueSquadron64Recomp" ); ev pid $P
snap(){ ev "snap $1 cpu=$(ps -o %cpu= -p $P) $(lsappinfo info -only ApplicationType -app "$(lsappinfo find pid=$P)" 2>/dev/null | tr -d '\n') napassert=$(pmset -g assertions | grep -c "pid $P(")"; }
front(){ osascript -e "tell application \"System Events\" to set frontmost of (first process whose unix id is $P) to true" 2>>$EV; }
vis(){ osascript -e "tell application \"System Events\" to set visible of (first process whose unix id is $P) to $1" 2>>$EV; }
sleep 30; front; ev phase fg0; sleep 5; snap fg; sleep 25
ev phase hidden; vis false; sleep 10; snap hidden; sleep 50
ev phase shown; vis true; front; sleep 10; snap shown; sleep 20
ev phase stop; kill -STOP $P; sleep 5; kill -CONT $P; ev phase cont; sleep 20
snap end; kill -9 $P; wait 2>/dev/null; ev done
