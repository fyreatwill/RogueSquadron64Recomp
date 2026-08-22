#!/bin/zsh
# Catch a failing ROGUESQ_AUDIO_UCODE=1 cinematic (640-stall or SIGBUS)
# with s2170 match-kw-flow probes. Exit 0 only if title+hangar.
# Self-contained: launches the game, SIGKILLs itself, exits nonzero on fail.
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TAG=s2171_image_cinematic_flow
OUTDIR=$ROOT/scratch/s73_post_a_scene/$TAG
mkdir -p "$OUTDIR"
cd "$ROOT" || exit 2
/usr/bin/pkill -9 -x RogueSquadron64Recomp >/dev/null 2>&1 || true

export GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_MATCH_KW=1'
env GAME_EXTRA_ENV="$GAME_EXTRA_ENV" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh "$TAG" 30 12 \
  > "$OUTDIR/driver.txt" 2>&1 &
DRV=$!

G=
for i in $(seq 1 40); do
  G=$(sed -n 's/^pid \([0-9]*\).*/\1/p' "$OUTDIR/driver.txt" 2>/dev/null | head -1)
  [[ -n "$G" ]] && break
  sleep 0.5
done
if [[ -z "$G" ]]; then
  echo "EARLY-DEATH: no game pid"
  kill -9 "$DRV" 2>/dev/null || true
  exit 3
fi

# 120s is past s2170 title (48.9s) and hangar (78.5s); s2169 stall never left 640.
sleep 120
kill -9 "$G" 2>/dev/null || true
/usr/bin/pkill -9 -x RogueSquadron64Recomp >/dev/null 2>&1 || true
kill -9 "$DRV" 2>/dev/null || true
/usr/bin/pkill -9 -f "run_mission_keys.sh $TAG" >/dev/null 2>&1 || true
sleep 1

LOG="$OUTDIR/run.log"
echo "out=$OUTDIR log=$LOG"
if [[ ! -f "$LOG" ]]; then
  echo "EARLY-DEATH: no run.log"
  exit 3
fi

echo "=== flow last-n ==="
for s in effectsEntry effectsRet matchEntry matchRet330 matchRet358; do
  last=$(grep -a "\[match-kw-flow\] n=.* site=$s " "$LOG" | tail -1)
  echo "  $s: $last"
done
echo "=== ctl 640 0x00696100 ==="
grep -ac '\[match-kw-flow-ctl\].*width=640 origin=0x00696100' "$LOG" || true
echo "=== phase ==="
grep -a '\[phase\] vi_width=' "$LOG" | grep -E '1024|512|00696100' || true
echo "=== crash ==="
grep -aE '\[CRASH\]|SIGBUS|SIGSEGV|si_addr=|pc-symbol=' "$LOG" | tail -10 || true

fail=0
if grep -aqE '\[CRASH\]|SIGBUS|SIGSEGV' "$LOG"; then
  echo "FAIL: crash/SIGBUS"
  fail=1
fi
if ! grep -aq '\[phase\] vi_width=1024' "$LOG"; then
  echo "FAIL: no VI 1024 (640-stall class)"
  fail=1
fi
if ! grep -aq '\[phase\] vi_width=512' "$LOG"; then
  echo "FAIL: no VI 512 hangar"
  fail=1
fi
if ! grep -aq '\[match-kw-flow-ctl\].*width=640 origin=0x00696100' "$LOG"; then
  echo "FAIL: missing flow-ctl positive control"
  fail=1
fi
exit $fail
