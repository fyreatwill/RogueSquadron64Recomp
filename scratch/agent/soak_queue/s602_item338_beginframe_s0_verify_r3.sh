#!/bin/zsh
# s602 requeue of BEGINFRAME_S0_GUARD live verify (HYPOTHESIS-ID m3-post-exit-fs-stall).
# s601 r2: budget exhausted 0/2 engagement (rc=2). Offline diagnosis (s602):
#   - FORCE_CASE6_START injects Start at ACE94, which only runs in hangar state 6.
#   - 5→6 is an automatic camera-settle write at ACE80 (not a button edge).
#   - A2 survived full HOLD at state=5 with 0 ACE80 / 0 ACE94; stick probes
#     (default STICK_SCHEDULE 10:sr 25:sl 40:su) co-timed with the stuck-at-5
#     window. Successful engagements (s590/s592_a/s598/s600) all hit ACE80 and
#     engaged within ~3s of p1-start — before any stick pulse.
# Recipe change vs s601 r2: STICK_SCHEDULE=999:sr (past HOLD_S → no stick
# pulses during settle). Same arms + fast-retry otherwise.
#
# Discriminating outcomes (scored attempt that reaches case6+hangar-sel):
#   A) guard fires (n>=1) AND no crash at 0x8000afa0 AND sec4>=2
#   B) guard fires, no 0x8000afa0 crash, dies on a DIFFERENT crash (or sec4 still 1)
#   C) still dies at 0x8000afa0 with 0 guard fires
#   D) 0 guard fires, no 0x8000afa0 crash (path not exercised)
#   E) budget exhausted without engagement AGAIN despite no-sticks
#      → ACE80 settle nondet independent of sticks; next pivot is force-write
#        state=6 under FORCE_CASE6_START after N case5 frames.
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no engagement.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=560
MAX_ATTEMPTS=8
GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""

while :; do
  NOW=$(date +%s)
  ELAPSED=$(( NOW - START_EPOCH ))
  REMAIN=$(( BUDGET_S - ELAPSED ))
  if [ "$REMAIN" -lt 30 ]; then
    echo "[fast-retry] budget exhausted (${ELAPSED}s used of ${BUDGET_S}s), stopping without engagement"
    break
  fi
  ATTEMPT=$(( ATTEMPT + 1 ))
  if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
    echo "[fast-retry] hit MAX_ATTEMPTS=$MAX_ATTEMPTS, stopping without engagement"
    break
  fi
  TAG="s602_item338_verify_r3_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  sleep 0.3
  echo "[fast-retry] attempt $ATTEMPT starting, ${REMAIN}s left in budget, tag=$TAG"
  # STICK_SCHEDULE=999:sr → no stick pulse in hold 1..HOLD_S (see s602 diagnosis)
  env PROBE_MODE=start_only HOLD_S=90 STICK_SCHEDULE="999:sr" \
    GAME_EXTRA_ENV="$GAME_EXTRA_ENV_BASE" \
    zsh "$ROOT/scratch/s73_post_a_scene/run_mission_keys.sh" "$TAG" 5 12
  RC=$?
  LOG="$OUT/run.log"
  CASE6=0; HSEL=0; CRASH=0; ACE80=0
  if [ -f "$LOG" ]; then
    grep -aq '\[case6-force-start\]' "$LOG" && CASE6=1
    grep -aq '\[hangar-sel\]' "$LOG" && HSEL=1
    grep -aq '\[CRASH\]' "$LOG" && CRASH=1
    grep -aq 'site=0x800ACE80' "$LOG" && ACE80=1
  fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[fast-retry] attempt $ATTEMPT done rc=$RC dur=${DUR}s case6=$CASE6 hangar_sel=$HSEL ace80=$ACE80 crash=$CRASH log=$LOG"
  if [ "$CASE6" -eq 1 ] && [ "$HSEL" -eq 1 ]; then
    echo "[fast-retry] attempt $ATTEMPT reached engagement -- scoring this one, no further rerolls"
    SCORED_LOG="$LOG"
    SCORED_RC="$RC"
    break
  fi
  echo "[fast-retry] attempt $ATTEMPT died pre-engagement -- fast reroll (not scored)"
done

if [ -z "$SCORED_LOG" ]; then
  echo "[fast-retry] no attempt reached engagement within budget (${ATTEMPT} attempts)"
  exit 2
fi

echo "[fast-retry] === scored attempt analysis: $SCORED_LOG ==="
python3 - "$SCORED_LOG" <<'PY'
import sys, re
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
bf=c("[beginframe-s0-guard]")
ace80=c("site=0x800ACE80")
afa0 = 1 if "0x8000afa0" in log.lower() or "0x8000AFA0" in log else 0
m_pc = re.search(r"\[CRASH\]\[last-guest-pc\] pc=(0x[0-9a-fA-F]+)", log)
m_sym = re.search(r"\[CRASH\]\[pc-symbol\][^\n]*", log)
crash_pc = m_pc.group(1) if m_pc else "-"
crash_sym = m_sym.group(0) if m_sym else "-"
crash="CRASH" if "[CRASH]" in log else "ok"
print(
  f"gate case6={case6} hangar-sel={hsel} ace80={ace80} inject_lines={inj} recov76B768~={rec} "
  f"sec4={sec4} sec2={sec2} thr495FC_creates={t12} coalesce_guard1={g1} "
  f"coalesce_guard2_r2={g2} beginframe_s0_guard={bf} last_guest_afa0={afa0} "
  f"crash={crash} crash_pc={crash_pc}",
  file=sys.stderr,
)
if m_sym:
  print(f"crash_sym={crash_sym}", file=sys.stderr)
PY

if grep -aq '\[CRASH\]' "$SCORED_LOG"; then
  exit 1
fi
exit "$SCORED_RC"
