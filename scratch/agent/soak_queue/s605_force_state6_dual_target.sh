#!/bin/zsh
# s605: force-write hangar state=6 after N case5 frames, then dual-target
# HOLD_S=180 for items -338/-361 (HYPOTHESIS-ID m3-post-exit-fs-stall).
#
# s604 (rc=137 hard-cap 600s): budget fix started A3, but 0/3 engagement.
# All hangar-reaching attempts stuck at state=5 (0 ACE80). A1/A2 pre-
# engagement crashes (0x800ab068 hangarTickCameraOrbit; 0x80054750
# tickWrappingTimerAccumulatorList). A3 alive through hold but never
# ACE80 (c5≈186, FS stalled). Combined s603+s604 = 0/5 ACE80 at state=5.
# s602 E pivot: force-write state=6 after N case5 frames so FORCE_CASE6
# (ACE94) can run. Landed ROGUESQ_FORCE_STATE6_AFTER (default off).
#
# Recipe: FORCE_STATE6_AFTER=40 + FORCE_CASE6_START=5 + FS_PIPE_INJECT +
# HOLD_S=180 + START_FLOOR=100 + no-sticks. Early abort: if hangarbay
# reached and force-state6 did not fire within path, still score on
# case6+hangar-sel (force may fire late).
#
# Discriminating outcomes (scored = case6+hangar-sel):
#   A) force6 fires + case6 + hangar-sel + beginframe_s0_guard>=1 + no
#      0x8000afa0 → -338 confirm 1/2 under forced engagement
#   B) thr11_destroy=1 + sec4_post>=1 + coalesce_guard2_r2>=1 + no crash
#      at 0x8000247c → -361 confirm 1/2
#   C) force6 fires + case6 + hangar-sel but thr11_destroy=0 at HOLD end
#      → E pivot (recovery-cell); force unlocked engagement only
#   D) force6 fires + case6 + hangar-sel + other crash → file breadcrumb
#   E) force6 fires but case6=0/hangar-sel=0 → state write insufficient
#      (case6 path needs more than the byte)
#   F) force6 never fires despite case5-entry n>=40 → env/build miss
#      (positive control fail)
#   G) 0 engagement after >=4 attempts with force armed → deeper block
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no engagement, 3 force miss.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=580
MAX_ATTEMPTS=8
HOLD_S=180
START_FLOOR_S=100
GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""

while :; do
  NOW=$(date +%s)
  ELAPSED=$(( NOW - START_EPOCH ))
  REMAIN=$(( BUDGET_S - ELAPSED ))
  if [ "$REMAIN" -lt "$START_FLOOR_S" ]; then
    echo "[fast-retry] budget exhausted (${ELAPSED}s used of ${BUDGET_S}s, remain=${REMAIN}<${START_FLOOR_S}), stopping without engagement"
    break
  fi
  ATTEMPT=$(( ATTEMPT + 1 ))
  if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
    echo "[fast-retry] hit MAX_ATTEMPTS=$MAX_ATTEMPTS, stopping without engagement"
    break
  fi
  TAG="s605_force_state6_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  sleep 0.3
  echo "[fast-retry] attempt $ATTEMPT starting, ${REMAIN}s left in budget, HOLD_S=$HOLD_S tag=$TAG"
  env PROBE_MODE=start_only HOLD_S=$HOLD_S STICK_SCHEDULE="999:sr" \
    GAME_EXTRA_ENV="$GAME_EXTRA_ENV_BASE" \
    zsh "$ROOT/scratch/s73_post_a_scene/run_mission_keys.sh" "$TAG" 5 12
  RC=$?
  LOG="$OUT/run.log"
  CASE6=0; HSEL=0; CRASH=0; ACE80=0; FORCE6=0
  if [ -f "$LOG" ]; then
    grep -aq '\[case6-force-start\]' "$LOG" && CASE6=1
    grep -aq '\[hangar-sel\]' "$LOG" && HSEL=1
    grep -aq '\[CRASH\]' "$LOG" && CRASH=1
    grep -aq 'site=0x800ACE80' "$LOG" && ACE80=1
    grep -aq '\[case5-force-state6\]' "$LOG" && FORCE6=1
  fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[fast-retry] attempt $ATTEMPT done rc=$RC dur=${DUR}s force6=$FORCE6 case6=$CASE6 hangar_sel=$HSEL ace80=$ACE80 crash=$CRASH log=$LOG"
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
  # Positive-control note: if any attempt had case5 but never force6, flag it
  exit 2
fi

echo "[fast-retry] === scored attempt analysis: $SCORED_LOG ==="
python3 - "$SCORED_LOG" <<'PY'
import sys, re
raw = open(sys.argv[1], "rb").read().decode("utf-8", "replace")
lines = raw.splitlines()
def c(s): return raw.count(s)

hsel_i = next((i for i, l in enumerate(lines) if "[hangar-sel]" in l), None)
post = lines[hsel_i:] if hsel_i is not None else []

sec4 = c("start-match: section 4")
sec2 = c("start-match: section 2")
case6 = c("[case6-force-start]")
hsel = c("[hangar-sel]")
ace80 = c("site=0x800ACE80")
force6 = c("[case5-force-state6]")
inj_ns = [int(m) for m in re.findall(r"\[fs-pipe-inject\] n=(\d+)", raw)]
inj_lines = len(inj_ns)
inj_max = max(inj_ns) if inj_ns else 0
rec = raw.count("76B768")
t12 = sum(1 for l in lines if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x800495FC" in l)
thr11_create = sum(1 for l in post if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x8006F2CC" in l)
created_rdram = set()
for l in post:
    if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x8006F2CC" in l:
        m = re.search(r"thr_rdram=(0x[0-9A-Fa-f]+)", l)
        if m:
            created_rdram.add(m.group(1))
thr11_destroy = 0
for l in post:
    if "[thr-destroy]" in l and "self" not in l:
        m = re.search(r"thr_rdram=(0x[0-9A-Fa-f]+)", l)
        if m and m.group(1) in created_rdram:
            thr11_destroy = 1
            break
sec4_post = sum(1 for l in post if "start-match: section 4" in l)
sec2_post = sum(1 for l in post if "start-match: section 2" in l)

g1 = c("[coalesce-heap-guard]")
g2 = c("[coalesce-heap-r2-guard]")
bf = c("[beginframe-s0-guard]")
afa0 = 1 if re.search(r"0x8000afa0", raw, re.I) else 0
m_pc = re.search(r"\[CRASH\]\[last-guest-pc\] pc=(0x[0-9a-fA-F]+)", raw)
m_sym = re.search(r"\[CRASH\]\[pc-symbol\][^\n]*", raw)
crash_pc = m_pc.group(1) if m_pc else "-"
crash_sym = m_sym.group(0) if m_sym else "-"
crash = "CRASH" if "[CRASH]" in raw else "ok"
print(
    f"gate force6={force6} case6={case6} hangar-sel={hsel} ace80={ace80} "
    f"inject_lines={inj_lines} inject_max_n={inj_max} recov76B768~={rec} "
    f"sec4={sec4} sec4_post={sec4_post} sec2={sec2} sec2_post={sec2_post} "
    f"thr495FC_creates={t12} thr11_create={thr11_create} thr11_destroy={thr11_destroy} "
    f"coalesce_guard1={g1} coalesce_guard2_r2={g2} beginframe_s0_guard={bf} "
    f"last_guest_afa0={afa0} crash={crash} crash_pc={crash_pc}",
    file=sys.stderr,
)
if m_sym:
    print(f"crash_sym={crash_sym}", file=sys.stderr)
cls = "?"
if force6 == 0:
    cls = "F_force6_miss"
elif thr11_destroy and sec4_post >= 1 and g2 >= 1 and crash == "ok":
    cls = "B_item361_confirm"
elif thr11_destroy and sec4_post >= 1 and crash_pc.lower() == "0x8000247c" and g2 == 0:
    cls = "C_r2_guard_miss"
elif thr11_destroy and sec4_post >= 1 and crash == "CRASH":
    cls = "D_sec4_other_crash"
elif thr11_destroy == 0 and hsel:
    cls = "E_thr11_still_live"
elif bf >= 1 and afa0 == 0:
    cls = "A_beginframe_confirm"
elif force6 and case6 and hsel and crash == "ok":
    cls = "C_engaged_no_thr11"
elif force6 and (case6 == 0 or hsel == 0):
    cls = "E_force6_no_case6"
else:
    cls = "F_neither_path"
print(f"class_hint={cls}", file=sys.stderr)
PY

if grep -aq '\[CRASH\]' "$SCORED_LOG"; then
  exit 1
fi
exit "$SCORED_RC"
