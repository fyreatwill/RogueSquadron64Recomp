#!/bin/zsh
# Dense capture burst. Sparse one-shot captures land on transitions and lie;
# always sample the window densely before concluding "the screen is black".
# Usage: burst.sh <prefix> <log> <start-delay-sec> <count> <interval-sec>
PREFIX=$1; LOG=$2; DELAY=${3:-2}; COUNT=${4:-28}; IVAL=${5:-0.15}
BUILD=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
cd "$BUILD" || exit 2
/usr/bin/pkill -x UserNotificationCenter >/dev/null 2>&1
ROGUESQ_LLE_FORCE=1 ./RogueSquadron64Recomp > "$LOG" 2>&1 &
PID=$!
sleep 0.8
/usr/bin/osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron") to true' >/dev/null 2>&1
R=""
for a in 1 2 3 4 5 6; do
    R=$(/usr/bin/osascript -e '
tell application "System Events"
  repeat with p in (every process whose name contains "RogueSquadron")
    repeat with w in (every window of p)
      set pos to position of w
      set sz to size of w
      return ((item 1 of pos) as text) & "," & ((item 2 of pos) as text) & "," & ((item 1 of sz) as text) & "," & ((item 2 of sz) as text)
    end repeat
  end repeat
end tell' 2>/dev/null)
    [[ -n "$R" ]] && break
    sleep 0.2
done
[[ -z "$R" ]] && { print -u2 "no window"; kill -9 $PID; exit 1; }
sleep "$DELAY"
for i in $(seq -w 1 "$COUNT"); do
    # The game can die mid-burst; without this check screencapture happily
    # grabs whatever window is underneath and every frame looks like "content".
    if ! kill -0 "$PID" 2>/dev/null; then
        print "process gone before frame $i"
        break
    fi
    /usr/sbin/screencapture -x -o -R"$R" "${PREFIX}_$i.png"
    sleep "$IVAL"
done
kill -9 "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
print "burst done"
