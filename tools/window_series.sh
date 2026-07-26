#!/bin/zsh
# Launch once, capture the game window at several times, then stop.
# Usage: series.sh <prefix> <log> <t1> [t2 ...]
PREFIX=$1; LOG=$2; shift 2
BUILD=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
cd "$BUILD" || exit 2
/usr/bin/pkill -x UserNotificationCenter >/dev/null 2>&1
ROGUESQ_LLE_FORCE=1 ./RogueSquadron64Recomp > "$LOG" 2>&1 &
PID=$!
/usr/bin/osascript -e '
tell application "System Events"
  set frontmost of (first process whose name contains "RogueSquadron") to true
end tell' >/dev/null 2>&1

prev=0
for t in "$@"; do
    sleep $((t - prev))
    prev=$t
    RECT=""
    for a in 1 2 3; do
        RECT=$(/usr/bin/osascript -e '
tell application "System Events"
  repeat with p in (every process whose name contains "RogueSquadron")
    repeat with w in (every window of p)
      set pos to position of w
      set sz to size of w
      return ((item 1 of pos) as text) & "," & ((item 2 of pos) as text) & "," & ((item 1 of sz) as text) & "," & ((item 2 of sz) as text)
    end repeat
  end repeat
end tell' 2>/dev/null)
        [[ -n "$RECT" ]] && break
        sleep 1
    done
    if [[ -n "$RECT" ]]; then
        /usr/sbin/screencapture -x -o -R"$RECT" "${PREFIX}_${t}s.png"
        print "captured ${t}s"
    else
        print "no window at ${t}s"
    fi
done

kill -9 "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
print "series done"
