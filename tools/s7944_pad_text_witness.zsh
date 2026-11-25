#!/bin/zsh
# s7944: PIXEL witness for the F6 panel pad Clear row (L1) and Reset to defaults (R3 hold 1 s). One run of the s7941
# synthetic-pad script with ROGUESQ_PAD_NAV_HOLD stretching open_idle (defaults), close_idle (panel closed: negative
# control), clear_idle (row A cleared, "Row cleared" message) and r3_hold_idle (defaults restored, "Defaults restored").
# At each hold: window screenshot + the latest [panel-rect] line (srcA= A-row source cell, msg= message line, and the
# text the draw thread used). tools/s7944_text_check.py compares text masks of those crops across the shots.
# Needs: unlocked screen + Screen Recording permission; no other game instance. Usage: zsh tools/s7944_pad_text_witness.zsh
set -u
R=$PWD; D=$R/scratch/s7944/w_$(date +%Y%m%d-%H%M%S); mkdir -p $D
( cd $R/build && env SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_PAD_NAV_TEST=1 ROGUESQ_PAD_NAV_HOLD=${HOLD:-400} \
    ROGUESQ_PAD_NAV_HOLD_STEPS=open_idle,close_idle,clear_idle,r3_hold_idle \
    ROGUESQ_PANEL_RECTS=1 ROGUESQ_CONTROLS=$D/c.json ./RogueSquadron64Recomp rogue_squadron.z64 > $D/game.log 2>&1 ) &
sleep 2; pid=$(pgrep -f 'RogueSquadron64Recomp rogue_squadron.z64' | head -1)
n=0
for i in {1..300}; do
  sleep 0.5
  h=$(grep -c 'pad-nav-test\] hold' $D/game.log)
  if (( h > n )); then
    n=$h; sleep 1.2
    wid=$(build/winctl find $pid | awk '{print $1}'); geo=$(build/winctl find $pid)
    screencapture -x -o -l $wid $D/shot$n.png
    step=$(grep 'pad-nav-test\] hold' $D/game.log | sed -n "${n}p" | sed 's/.*step=\([a-z0-9_]*\).*/\1/')
    rect=$(grep '\[panel-rect\]' $D/game.log | tail -1)
    echo "shot=$n step=$step open=$(grep -c '\[controls-panel\] open' $D/game.log)/$(grep -c '\[controls-panel\] closed' $D/game.log) win=$geo $rect" >> $D/shots.txt
  fi
  grep -q 'pad-nav-test\] checks=' $D/game.log && break
done
pkill -9 -f 'RogueSquadron64Recomp rogue_squadron.z64'; sleep 0.5
grep 'pad-nav-test\] checks=' $D/game.log || echo "NO RESULT"
python3 $R/tools/s7944_text_check.py $D
