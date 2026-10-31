#!/bin/zsh
# G1f (s6688): launch the game with the inherited ROGUESQ_ASPECT / ROGUESQ_FULLSCREEN,
# capture the game window by id (cannot grab an overlapping window), optionally toggle
# fullscreen and capture again, then SIGKILL. Prints window geometry per capture.
# Harness keys never reach SDL on macOS (s5416), so the toggle uses the in-process
# synthetic F11 (ROGUESQ_FS_TEST_TOGGLE_S); its keywitness line is the delivery control.
# Usage: g1f_window_check.sh <outprefix> [delay_s=25] [toggle=0|1]
OUT=${1:?outprefix}; DELAY=${2:-25}; TOGGLE=${3:-0}
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
W=$ROOT/build/winctl
cd $ROOT/build || exit 2
[ "$TOGGLE" = 1 ] && export ROGUESQ_FS_TEST_TOGGLE_S="$((DELAY + 2)),$((DELAY + 12))"
./RogueSquadron64Recomp > "$OUT.log" 2>&1 &
PID=$!
shot() {
  local g; g=$($W find $PID) || { echo "$1: no window"; return 1; }
  /usr/sbin/screencapture -x -o -l${g%% *} "$OUT$1.png"
  echo "$1: window $g png $(sips -g pixelWidth -g pixelHeight "$OUT$1.png" | awk '/pixel/{printf "%s ",$2}')"
}
sleep "$DELAY"; shot ""
if [ "$TOGGLE" = 1 ]; then
  sleep 6; shot _fs; /usr/sbin/screencapture -x -D1 "${OUT}_fs_display.png"
  sleep 10; shot _back
elif grep -q 'fullscreen=1' "$OUT.log"; then
  /usr/sbin/screencapture -x -D1 "${OUT}_display.png"
fi
kill -9 $PID 2>/dev/null
grep -a -E '^\[g1f\]|keywitness\] type=0x300' "$OUT.log"
