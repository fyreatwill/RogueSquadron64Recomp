#!/bin/zsh
# Catch a failing ROGUESQ_AUDIO_UCODE=1 cinematic (vec3Cross NAN_CHECK
# SIGABRT, SIGBUS, copyToRAM SIGSEGV, or 640-stall) with s2181 f2 plus
# later NAN_CHECK operand IEEE word bits. Exit 0 only if title+hangar.
# Self-contained: launches the game, SIGKILLs itself, exits nonzero on
# a cinematic miss.
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TAG=s2181_image_vec3_f2
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

# Past s2181_on title (49.1s) and hangar (78.3s); s2176 abort at t=24.1.
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

echo "=== vec3-word-ctl 640 0x00696100 ==="
grep -ac '\[vec3-word-ctl\].*width=640 origin=0x00696100' "$LOG" || true
echo "=== ctl by site ==="
for s in extract cross f2 f4 f8 f0 f6 f12 f14 f16 f18; do
  echo -n "  $s "
  grep -ac "\[vec3-word-ctl\].*site=$s " "$LOG" || true
done
echo "=== nan/inf rows ==="
grep -aE '\[vec3-word.*nan_mem=1|\[vec3-word.*nan_fpr=1|\[vec3-word.*inf_mem=1|\[vec3-word.*inf_fpr=1' "$LOG" | tail -20 || true
echo "=== last f2 ==="
grep -a '\[vec3-word\] .*site=f2 ' "$LOG" | tail -1 || true
echo "=== last extract ==="
grep -a '\[vec3-word\] .*site=extract ' "$LOG" | tail -1 || true
echo "=== last first-cross ==="
grep -a '\[vec3-word\] .*first=1 ' "$LOG" | tail -1 || true
echo "=== phase ==="
grep -a '\[phase\] vi_width=' "$LOG" | grep -E '1024|512|00696100' || true
echo "=== crash ==="
grep -aE '\[CRASH\]|\[ABORT\]|SIGBUS|SIGSEGV|SIGABRT|Assertion failed|si_addr=|pc-symbol=|last-guest-pc' "$LOG" | tail -20 || true

fail=0
if ! grep -aq '\[phase\] vi_width=1024' "$LOG"; then
  echo "FAIL: no VI 1024 (640-stall or cinematic crash)"
  fail=1
fi
if ! grep -aq '\[phase\] vi_width=512' "$LOG"; then
  echo "FAIL: no VI 512 hangar"
  fail=1
fi
if ! grep -aq '\[vec3-word-ctl\].*width=640 origin=0x00696100' "$LOG"; then
  echo "FAIL: missing vec3-word-ctl positive control"
  fail=1
fi
if ! grep -aq '\[vec3-word-ctl\].*site=f2 ' "$LOG"; then
  echo "FAIL: missing cinematic site=f2 ctl"
  fail=1
fi
exit $fail
