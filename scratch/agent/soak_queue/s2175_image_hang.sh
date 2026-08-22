#!/bin/zsh
# Catch a failing ROGUESQ_AUDIO_UCODE=1 cinematic (SIGBUS or 640-stall)
# with s2175 hang-after-87A0 always-log (87A8 / dispatch / xform).
# Exit 0 only if title+hangar. Self-contained: launches the game,
# SIGKILLs itself, exits nonzero on a cinematic miss.
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TAG=s2175_image_hang
OUTDIR=$ROOT/scratch/s73_post_a_scene/$TAG
mkdir -p "$OUTDIR"
cd "$ROOT" || exit 2
/usr/bin/pkill -9 -x RogueSquadron64Recomp >/dev/null 2>&1 || true

export GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1'
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

# Past s2175_on title (48.5s) and hangar (77.7s); s2171 SIGBUS at t=28.2.
sleep 180
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

echo "=== heap0-ctl 640 0x00696100 ==="
grep -ac '\[heap0-ctl\].*width=640 origin=0x00696100' "$LOG" || true
echo "=== dispatchEntry ctl 640 0x00696100 ==="
grep -ac '\[heap0-ctl\].*site=dispatchEntry.*width=640 origin=0x00696100' "$LOG" || true
echo "=== store dest 0x8025A580 ==="
grep -a '\[heap0\] .*site=store57100 .*dest=0x8025A580' "$LOG" | tail -3 || true
echo "=== last heap0 per site ==="
for s in store57100 load87a0 lwc87a8 dispatchEntry dispatchRet xformEntry xformRet; do
  last=$(grep -a "\[heap0\] n=.* site=$s " "$LOG" | tail -1)
  echo "  $s: $last"
done
echo "=== last first-slot load87a0 ==="
grep -a '\[heap0\] .*site=load87a0 .*dest=0x8025A580' "$LOG" | tail -1 || true
echo "=== lwc87a8 zero=1 ==="
grep -a '\[heap0\] .*site=lwc87a8 .*zero=1' "$LOG" | tail -5 || true
echo "=== phase ==="
grep -a '\[phase\] vi_width=' "$LOG" | grep -E '1024|512|00696100' || true
echo "=== crash ==="
grep -aE '\[CRASH\]|SIGBUS|SIGSEGV|si_addr=|pc-symbol=|last-guest-pc' "$LOG" | tail -12 || true

fail=0
if ! grep -aq '\[phase\] vi_width=1024' "$LOG"; then
  echo "FAIL: no VI 1024 (640-stall or cinematic crash)"
  fail=1
fi
if ! grep -aq '\[phase\] vi_width=512' "$LOG"; then
  echo "FAIL: no VI 512 hangar"
  fail=1
fi
if ! grep -aq '\[heap0-ctl\].*width=640 origin=0x00696100' "$LOG"; then
  echo "FAIL: missing heap0-ctl positive control"
  fail=1
fi
if ! grep -aq '\[heap0-ctl\].*site=dispatchEntry.*width=640 origin=0x00696100' "$LOG"; then
  echo "FAIL: missing dispatchEntry ctl positive control"
  fail=1
fi
exit $fail
