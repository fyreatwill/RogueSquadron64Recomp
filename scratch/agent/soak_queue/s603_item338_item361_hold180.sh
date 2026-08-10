#!/bin/zsh
# s603: dual-target hold after s602 r3 scored D (path not exercised) + clean
# post-engagement survival (HYPOTHESIS-ID m3-post-exit-fs-stall).
#
# s602 r3 attempt 4 gate (scored):
#   case6=1 hangar-sel=1 ace80=1 inject_lines=31 (max_n=550) recov76B768=0
#   sec4=1 sec2=0 thr495FC_creates=2 (FALSE: double-count of one boot create)
#   beginframe_s0_guard=0 last_guest_afa0=0 crash=ok
#
# Offline vs s592_a (sole historical sec4=2):
#   thr-11 = saveServiceWorker entry=0x8006F2CC (NOT thr495FC).
#   Pipeline: post-hsel thr-11 create → (cutscene) → thr-11 destroy ↔ sec4
#   reload → initSceneForMission coalesce R2 @0x8000247c (item -361 site).
#   s592_a: thr-11 destroy @~100s post-hsel → sec4=2 → CRASH 0x8000247c.
#   s602 r3: thr-11 still live at HOLD end (~post-hsel window too short under
#   HOLD_S=90); inject restores syncs (767 post task_end syncs>0) without
#   recovery cell 0x76B768; no sec4=2.
#
# Recipe change vs s602 r3: HOLD_S=180 (cap 210) so post-exit cutscene can
# reach thr-11 destroy. STICK_SCHEDULE=999:sr kept (no-sticks engagement OK).
# Gate fixed: thr11_destroy post-hsel, inject max_n, thr495FC unique creates.
#
# Discriminating outcomes (scored attempt = case6+hangar-sel):
#   A) beginframe_s0_guard>=1 AND no 0x8000afa0  → -338 live confirm 1/2
#   B) thr11_destroy=1 AND sec4>=2 AND coalesce_guard2_r2>=1 AND no crash
#      at 0x8000247c → -361 live confirm 1/2
#   C) thr11_destroy=1 AND sec4>=2 AND crash at 0x8000247c with 0 r2 guard
#      → R2 guard miss
#   D) thr11_destroy=1 AND sec4>=2 AND crash elsewhere → file breadcrumb; progress
#   E) thr11_destroy=0 at HOLD end (still live) → time alone not enough; next
#      probe recovery-cell reliability (H12c), not longer HOLD
#   F) beginframe 0 fires, no thr11 destroy, no 0x8000afa0 → D-class for both;
#      do NOT requeue same HOLD again (3rd non-discriminating for -338; pivot)
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no engagement.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=560
MAX_ATTEMPTS=6
HOLD_S=180
GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""

while :; do
  NOW=$(date +%s)
  ELAPSED=$(( NOW - START_EPOCH ))
  REMAIN=$(( BUDGET_S - ELAPSED ))
  # need ~boot+menu+HOLD headroom; refuse start if < HOLD_S+90
  NEED=$(( HOLD_S + 90 ))
  if [ "$REMAIN" -lt "$NEED" ]; then
    echo "[fast-retry] budget exhausted (${ELAPSED}s used of ${BUDGET_S}s, need ${NEED}s), stopping without engagement"
    break
  fi
  ATTEMPT=$(( ATTEMPT + 1 ))
  if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
    echo "[fast-retry] hit MAX_ATTEMPTS=$MAX_ATTEMPTS, stopping without engagement"
    break
  fi
  TAG="s603_item338_item361_hold180_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  sleep 0.3
  echo "[fast-retry] attempt $ATTEMPT starting, ${REMAIN}s left in budget, HOLD_S=$HOLD_S tag=$TAG"
  env PROBE_MODE=start_only HOLD_S=$HOLD_S STICK_SCHEDULE="999:sr" \
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
# inject: log is rate-limited; report max n=
inj_ns = [int(m) for m in re.findall(r"\[fs-pipe-inject\] n=(\d+)", raw)]
inj_lines = len(inj_ns)
inj_max = max(inj_ns) if inj_ns else 0
rec = raw.count("76B768")
# thr495FC: unique thr-create lines only (not thr-create-id double-count)
t12 = sum(1 for l in lines if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x800495FC" in l)
# thr-11 post-hsel: saveServiceWorker entry=0x8006F2CC
thr11_create = sum(1 for l in post if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x8006F2CC" in l)
# destroy: match thr-destroy lines after hsel that are not "self"; id alone is
# unstable across runs, so also accept any thr-destroy whose thr_rdram was seen
# created post-hsel with entry 0x8006F2CC
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
# also count post-hsel sec4 (total sec4 includes boot)
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
    f"gate case6={case6} hangar-sel={hsel} ace80={ace80} "
    f"inject_lines={inj_lines} inject_max_n={inj_max} recov76B768~={rec} "
    f"sec4={sec4} sec4_post={sec4_post} sec2={sec2} sec2_post={sec2_post} "
    f"thr495FC_creates={t12} thr11_create={thr11_create} thr11_destroy={thr11_destroy} "
    f"coalesce_guard1={g1} coalesce_guard2_r2={g2} beginframe_s0_guard={bf} "
    f"last_guest_afa0={afa0} crash={crash} crash_pc={crash_pc}",
    file=sys.stderr,
)
if m_sym:
    print(f"crash_sym={crash_sym}", file=sys.stderr)
# classify hint
cls = "?"
if thr11_destroy and sec4_post >= 1 and g2 >= 1 and crash == "ok":
    cls = "B_item361_confirm"
elif thr11_destroy and sec4_post >= 1 and crash_pc.lower() == "0x8000247c" and g2 == 0:
    cls = "C_r2_guard_miss"
elif thr11_destroy and sec4_post >= 1 and crash == "CRASH":
    cls = "D_sec4_other_crash"
elif thr11_destroy == 0 and hsel:
    cls = "E_thr11_still_live"
elif bf >= 1 and afa0 == 0:
    cls = "A_beginframe_confirm"
elif bf == 0 and afa0 == 0 and crash == "ok":
    cls = "F_neither_path"
print(f"class_hint={cls}", file=sys.stderr)
PY

if grep -aq '\[CRASH\]' "$SCORED_LOG"; then
  exit 1
fi
exit "$SCORED_RC"
