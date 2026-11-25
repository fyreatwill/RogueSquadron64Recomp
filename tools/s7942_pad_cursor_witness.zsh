#!/bin/zsh
# s7942: PIXEL witness for the F6 panel pad cursor. One run of the s7941 synthetic-pad script with ROGUESQ_PAD_NAV_HOLD
# stretching the idle steps on rows 0, 1 and 17 (17 = last row, needs the table to scroll). At each hold: window screenshot
# (screencapture -l <wid>) + the latest [panel-rect] line (cursor row rect prow=, table clip=, vis=). tools/s7942_band_check.py
# then finds the highlight band in each PNG and checks it sits on the logged rect and inside the clip.
# Needs: unlocked screen + Screen Recording permission for this shell; no other game instance. Usage: zsh tools/s7942_pad_cursor_witness.zsh
# s7945: optional env PANEL_ASPECT=16:9 PANEL_FS=1 = owner recipe (high-DPI drawable, fullscreen, no title bar).
set -u
R=$PWD; D=$R/scratch/s7942/w_$(date +%Y%m%d-%H%M%S); mkdir -p $D
( cd $R/build && env SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FULLSCREEN=${PANEL_FS:-0} ${PANEL_ASPECT:+ROGUESQ_ASPECT=$PANEL_ASPECT} ROGUESQ_PAD_NAV_TEST=1 ROGUESQ_PAD_NAV_HOLD=${HOLD:-400} \
    ROGUESQ_PANEL_RECTS=1 ROGUESQ_CONTROLS=$D/c.json ./RogueSquadron64Recomp rogue_squadron.z64 > $D/game.log 2>&1 ) &
sleep 2; pid=$(pgrep -f 'RogueSquadron64Recomp rogue_squadron.z64' | head -1)
n=0
for i in {1..240}; do
  sleep 0.5
  h=$(grep -c 'pad-nav-test\] hold' $D/game.log)
  if (( h > n )); then
    n=$h; sleep 1.2
    wid=$(build/winctl find $pid | awk '{print $1}'); geo=$(build/winctl find $pid)
    screencapture -x -o -l $wid $D/shot$n.png
    row=$(grep 'pad-nav-test\] hold' $D/game.log | sed -n "${n}p" | sed 's/.*row=\([0-9]*\).*/\1/')
    rect=$(grep '\[panel-rect\]' $D/game.log | tail -1)
    echo "shot=$n row=$row win=$geo $rect" >> $D/shots.txt
  fi
  grep -q 'pad-nav-test\] checks=' $D/game.log && break
done
pkill -9 -f 'RogueSquadron64Recomp rogue_squadron.z64'; sleep 0.5
grep 'pad-nav-test\] checks=' $D/game.log || echo "NO RESULT"
python3 $R/tools/s7942_band_check.py $D
