#!/bin/zsh
# Launch the LLE build from the build dir (the ROM must sit next to the
# executable), screenshot only the game window after a delay, then stop it.
# Extra ROGUESQ_* env vars are inherited.
# Usage: shot.sh <seconds-before-shot> <png> <logfile>
DELAY=${1:-25}
PNG=${2:-/tmp/shot.png}
LOG=${3:-/tmp/shot.log}
BUILD=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
cd "$BUILD" || exit 2

# A leftover "quit unexpectedly" dialog from a previous run sits on top of the
# game window and ruins the capture. Dismissing it just closes that panel.
/usr/bin/pkill -x UserNotificationCenter >/dev/null 2>&1
ROGUESQ_LLE_FORCE=1 ./RogueSquadron64Recomp > "$LOG" 2>&1 &
PID=$!
sleep "$DELAY"

# Raise the game window first; otherwise it sits behind other windows and the
# capture shows whatever is on top of it.
/usr/bin/osascript -e '
tell application "System Events"
  set frontmost of (first process whose name contains "RogueSquadron") to true
end tell' >/dev/null 2>&1
sleep 2

# Window rect via System Events. No full-screen fallback: capturing the whole
# desktop would pull in unrelated windows.
RECT=""
for attempt in 1 2 3 4 5; do
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
    /usr/sbin/screencapture -x -o -R"$RECT" "$PNG"
    print "captured window rect $RECT"
else
    print -u2 "no window rect available; not capturing"
fi

# SIGKILL, not TERM: the TERM path runs SDL_QUIT cleanup, which aborts (known
# cosmetic bug) and pops a crash dialog that blocks the next run's capture.
kill -9 "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
print "log=$LOG png=$PNG"
