#!/bin/zsh
# s7941: F6 Controls panel driven from a pad alone. Two arms, run one after the other (one game at a time):
#   on  : ROGUESQ_PAD_NAV_TEST=1 -> expect checks=23 fail=0 and controls.json with B=pad:y
#   off : same + ROGUESQ_PANEL_PAD=0 (negative control) -> expect fail=21 (only the two pass-through checks pass)
# SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 is required: without it SDL drops virtual-pad input when the window is not focused
# (s7941 first run: every press read 0). Usage: zsh tools/s7941_pad_nav_test.zsh   (from the repo root)
set -u
R=$PWD; D=$R/scratch/s7941/e2e_$(date +%Y%m%d-%H%M%S); mkdir -p $D
arm() {  # tag extra-env...
  local tag=$1; shift
  ( cd $R/build && env SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_PAD_NAV_TEST=1 \
      ROGUESQ_CONTROLS=$D/$tag.json "$@" ./RogueSquadron64Recomp rogue_squadron.z64 > $D/$tag.log 2>&1 ) &
  local p=$!
  for i in {1..120}; do sleep 1; grep -q 'pad-nav-test\] checks=' $D/$tag.log && break; done
  pkill -9 -f 'RogueSquadron64Recomp rogue_squadron.z64'; wait $p 2>/dev/null
  grep 'pad-nav-test\] checks=' $D/$tag.log | sed "s/^/$tag: /" || echo "$tag: NO RESULT"
}
arm on
arm off ROGUESQ_PANEL_PAD=0
on=$(grep -c 'checks=23 fail=0' $D/on.log); off=$(grep -c 'checks=23 fail=21' $D/off.log)
b=$(python3 -c "import json,sys;print(json.load(open('$D/on.json'))['buttons'].get('B'))" 2>/dev/null)
echo "tag=s7941_pad_nav on_pass=$on off_control=$off saved_B=$b"
[[ $on == 1 && $off == 1 && $b == "['pad:y']" ]] && { echo VERDICT PASS; exit 0; } || { echo VERDICT FAIL; exit 1; }
