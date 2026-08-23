#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TAG=s2184_image_dma_cinematic
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

echo "=== image joins by phase/width/origin ==="
grep -a '\[audtask-image-join\]' "$LOG" | awk '
  { phase="?"; width="?"; origin="?";
    for (i=1; i<=NF; ++i) {
      if ($i ~ /^phase=/) { split($i,a,"="); phase=a[2] }
      if ($i ~ /^width=/) { split($i,a,"="); width=a[2] }
      if ($i ~ /^origin=/) { split($i,a,"="); origin=a[2] }
    }
    key=phase "/" width "/" origin; count[key]++
  }
  END { for (key in count) print count[key], key }
' | sort -k2
echo "=== image join positive control ==="
grep -ac '\[audtask-image-join\]' "$LOG" || true
echo "=== named-word overlaps ==="
grep -a '\[audtask-image-join\]' "$LOG" | perl -ne '
  my ($dest) = /\bdest=(0x[0-9A-Fa-f]+)/; my ($len) = /\blen=(0x[0-9A-Fa-f]+)/;
  next unless defined $dest && defined $len;
  my $d=hex($dest); my $l=hex($len);
  for my $pair (["heap0",0x25A580],["slot_word0",0x0CA748],["slot_plus50",0x0C7B0C],["vec3_dest",0x165E40],["match_v0",0x0CDB58],["match_a0",0x2231EC]) {
    print "overlap=$pair->[0] $dest len=$len\n" if $d <= $pair->[1] && $pair->[1] < $d+$l;
  }
' | head -20 || true
echo "=== phase ==="
grep -a '\[phase\] vi_width=' "$LOG" | grep -E '1024|512|00696100|00696600' | tail -20 || true
echo "=== crash ==="
grep -aE '\[CRASH\]|\[ABORT\]|SIGBUS|SIGSEGV|SIGABRT|Assertion failed|si_addr=|pc-symbol=|last-guest-pc' "$LOG" | tail -20 || true

if ! grep -aq '\[audtask-image-join\]' "$LOG"; then
  echo "FAIL: missing image-DMA positive control"
  exit 1
fi
exit 0
