#!/bin/zsh
# s592 soak_queue retry B: identical recipe to a (independent attempt for sec4).
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
TAG="s592_sec4_thr12_b_$(date +%Y%m%d%H%M%S)"
OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
mkdir -p "$OUT"
/usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
sleep 0.3
env PROBE_MODE=start_only HOLD_S=90 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1" \
  zsh "$ROOT/scratch/s73_post_a_scene/run_mission_keys.sh" "$TAG" 5 12
RC=$?
LOG="$OUT/run.log"
if [[ -f "$LOG" ]]; then
  python3 - "$LOG" <<'PY'
import sys
log=open(sys.argv[1],"rb").read().decode("utf-8","replace")
def c(s): return log.count(s)
print(f"gate case6={c('[case6-force-start]')} hangar-sel={c('[hangar-sel]')} inject_lines={c('[fs-pipe-inject]')} sec4={c('start-match: section 4')} sec2={c('start-match: section 2')} thr495FC={c('entry=0x800495FC')} crash={'CRASH' if '[CRASH]' in log else 'ok'}", file=sys.stderr)
PY
  if grep -aq '\[CRASH\]' "$LOG"; then
    exit 1
  fi
fi
exit "$RC"
