#!/bin/zsh
# s595 soak_queue: REDESIGNED recipe for item -361 R2 guard live re-verify.
# 7 consecutive non-discriminating attempts (s592b, s593-manual, s593_a/b,
# s594_c/d) all died before reaching post-exit sec4>=2 -- either pre-force-exit
# background noise (case6=0) or force-exit reached (case6=1 hangar-sel=1,
# s594_c) but the FULL_SYNC recovery cell (0x76B768) never fired within the
# HOLD_S=90 window, so thr-11 never destroyed and the run drifted into
# unrelated background noise (item -347, transformLightByType region) instead
# of ever reaching sec4>=2. Per NEXT.md's iron-rule-8 redesign clause: recovery
# is intermittent (s589 fired, s591/s594 did not) -- give it more wall-clock
# exposure per run instead of blindly re-queuing the same HOLD_S=90 shape.
# HOLD_S raised 90->210 (s592a's own 267s @ HOLD90 implies ~177s non-hold
# overhead; 177+210=387s, safely under the loop's 600s hard cap).
# Self-contained from repo root. Exit nonzero on game CRASH marker.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
TAG="s595_coalesce_r2_verify_e_$(date +%Y%m%d%H%M%S)"
OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
mkdir -p "$OUT"
/usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
sleep 0.3
env PROBE_MODE=start_only HOLD_S=210 \
  GAME_EXTRA_ENV="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1" \
  zsh "$ROOT/scratch/s73_post_a_scene/run_mission_keys.sh" "$TAG" 5 12
RC=$?
LOG="$OUT/run.log"
if [[ -f "$LOG" ]]; then
  python3 - "$LOG" <<'PY'
import sys
log=open(sys.argv[1],"rb").read().decode("utf-8","replace")
def c(s): return log.count(s)
sec4=c("start-match: section 4")
sec2=c("start-match: section 2")
case6=c("[case6-force-start]")
hsel=c("[hangar-sel]")
inj=c("[fs-pipe-inject]")
rec=log.count("76B768")
t12=log.count("entry=0x800495FC")
g1=c("[coalesce-heap-guard]")
g2=c("[coalesce-heap-r2-guard]")
crash="CRASH" if "[CRASH]" in log else "ok"
print(f"gate case6={case6} hangar-sel={hsel} inject_lines={inj} recov76B768~={rec} sec4={sec4} sec2={sec2} thr495FC_creates={t12} coalesce_guard1={g1} coalesce_guard2_r2={g2} crash={crash}", file=sys.stderr)
PY
  if grep -aq '\[CRASH\]' "$LOG"; then
    exit 1
  fi
fi
exit "$RC"
