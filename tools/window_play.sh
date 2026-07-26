#!/bin/zsh
# Launch the game, press Start (Return) a few times to skip the intro, then
# capture the window at several times.
# Usage: play.sh <prefix> <log> <t1> [t2 ...]
PREFIX=$1; LOG=$2; shift 2
BUILD=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
cd "$BUILD" || exit 2
/usr/bin/pkill -x UserNotificationCenter >/dev/null 2>&1
ROGUESQ_LLE_FORCE=1 ./RogueSquadron64Recomp > "$LOG" 2>&1 &
PID=$!

raise() {
    /usr/bin/osascript -e '
tell application "System Events"
  set frontmost of (first process whose name contains "RogueSquadron") to true
end tell' >/dev/null 2>&1
}

rect() {
    /usr/bin/osascript -e '
tell application "System Events"
  repeat with p in (every process whose name contains "RogueSquadron")
    repeat with w in (every window of p)
      set pos to position of w
      set sz to size of w
      return ((item 1 of pos) as text) & "," & ((item 2 of pos) as text) & "," & ((item 1 of sz) as text) & "," & ((item 2 of sz) as text)
    end repeat
  end repeat
end tell' 2>/dev/null
}

press_start() {
    raise
    /usr/bin/osascript -e '
tell application "System Events" to key code 36' >/dev/null 2>&1
}

sleep 8
raise
# Start button (Return) a handful of times, spaced out, to get through the
# intro cinematic and any "press start" prompts.
for i in 1 2 3 4 5 6 7 8; do
    press_start
    sleep 2
done

prev=24
for t in "$@"; do
    if (( t > prev )); then sleep $((t - prev)); fi
    prev=$t
    press_start
    R=$(rect)
    if [[ -n "$R" ]]; then
        /usr/sbin/screencapture -x -o -R"$R" "${PREFIX}_${t}s.png"
        print "captured ${t}s"
    else
        print "no window at ${t}s"
    fi
done

kill -9 "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
print "play done"
