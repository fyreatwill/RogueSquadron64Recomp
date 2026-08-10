#!/bin/zsh
# s609: recovery-cell gate on force6+inject path.
# HYPOTHESIS-ID: m3-post-exit-fs-stall
#
# s608 confirm fold (attempt 3 scored offline after hard-cap):
#   force6=1 case6=1 hangar-sel=1 ace80=1 inject_max_n=750 thr11_create=1
#   recov76B768=0 recov76BA90=0 thr11_destroy=0 sec4_post=0 sec2_post=0
#   crash=ok (hard-killed mid-hold). Post-hangar-sel FULL_SYNC mono-cell
#   0x0076DF60×474 — never diversifies to 0x0076B768 (s607 had ×46 76B768
#   + multi-cell family after comparable inject volume). Class =
#   F_recovery_silent_no_thr11_destroy. H-recov1 necessity SUPPORTED.
# Pre-eng A1/A2 free rerolls; A1 breadcrumb setByteAcrossEntryList/0x800aafa8.
#
# New discard class: engaged + inject alive but no 0x0076B768 within
# RECOV_WAIT_S after hangar-sel → SIGKILL free reroll (do not spend full HOLD
# scoring a dead recovery path). Score only recovery-active attempts.
#
# Discriminating outcomes (scored = eng + recov76B768≥1 + not matnoise):
#   A) sec2_post + ok → in-mission hold
#   B) sec2_post + packTlut/loadDebugAssets → -373 2nd
#   C) sec2_post + other crash → new breadcrumb
#   D) thr11_destroy+sec4, sec2=0 → regression
#   E) recov≥1 but thr11 never destroyed by EOF
#   F) budget exhaust: only pre-eng / matnoise / recovery-silent
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no recovery-active engagement, 3 force miss.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=560
MAX_ATTEMPTS=8
HOLD_S=180
START_FLOOR_S=90
# After hangar-sel, if no recovery cell within this window, kill+reroll.
# s607 first 76B768 was ~inject+~56k log lines (~tens of seconds post-inject);
# 100s is generous vs that and leaves room for multi-reroll under 560s.
RECOV_WAIT_S=100
POLL_S=3

GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""
MATERIAL_NOISE_N=0
PRE_ENG_N=0
RECOV_SILENT_N=0

kill_game() {
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  /usr/bin/pkill -9 -f 'run_mission_keys.sh' 2>/dev/null || true
}

while :; do
  NOW=$(date +%s)
  ELAPSED=$(( NOW - START_EPOCH ))
  REMAIN=$(( BUDGET_S - ELAPSED ))
  if [ "$REMAIN" -lt "$START_FLOOR_S" ]; then
    echo "[fast-retry] budget exhausted (${ELAPSED}s used of ${BUDGET_S}s, remain=${REMAIN}<${START_FLOOR_S}), stopping"
    break
  fi
  ATTEMPT=$(( ATTEMPT + 1 ))
  if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
    echo "[fast-retry] hit MAX_ATTEMPTS=$MAX_ATTEMPTS, stopping"
    break
  fi
  TAG="s609_recov_reroll_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  LOG="$OUT/run.log"
  kill_game
  sleep 0.3
  echo "[fast-retry] attempt $ATTEMPT starting, ${REMAIN}s left, HOLD_S=$HOLD_S RECOV_WAIT_S=$RECOV_WAIT_S tag=$TAG"
  mkdir -p "$OUT"
  env PROBE_MODE=start_only HOLD_S=$HOLD_S STICK_SCHEDULE="999:sr" \
    GAME_EXTRA_ENV="$GAME_EXTRA_ENV_BASE" \
    zsh "$ROOT/scratch/s73_post_a_scene/run_mission_keys.sh" "$TAG" 5 12 \
    >"$OUT/launcher.stdout" 2>"$OUT/launcher.stderr" &
  LAUNCH_PID=$!

  HSEL_T=0
  RECOV_SEEN=0
  EARLY_KILL=0
  EARLY_REASON=""
  while kill -0 "$LAUNCH_PID" 2>/dev/null; do
    sleep "$POLL_S"
    # Global budget hard stop
    NOW2=$(date +%s)
    if [ $(( NOW2 - START_EPOCH )) -ge "$BUDGET_S" ]; then
      EARLY_KILL=1
      EARLY_REASON=budget
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
    [ -f "$LOG" ] || continue
    if [ "$HSEL_T" -eq 0 ] && grep -aq '\[hangar-sel\]' "$LOG" 2>/dev/null; then
      HSEL_T=$NOW2
      echo "[fast-retry] attempt $ATTEMPT hangar-sel seen at +$((NOW2-NOW))s — starting RECOV_WAIT_S=${RECOV_WAIT_S}"
    fi
    if [ "$HSEL_T" -gt 0 ] && [ "$RECOV_SEEN" -eq 0 ]; then
      if grep -aq '0x0076B768' "$LOG" 2>/dev/null && grep -aq '\[rdp-fullsync\].*0x0076B768\|0x0076B768.*rdp-fullsync\|addr=0x0076B768' "$LOG" 2>/dev/null; then
        RECOV_SEEN=1
        echo "[fast-retry] attempt $ATTEMPT recovery 76B768 seen at +$((NOW2-NOW))s — letting HOLD finish"
      elif [ $(( NOW2 - HSEL_T )) -ge "$RECOV_WAIT_S" ]; then
        # Also accept any non-76DF60 post-exit fullsync diversification as recovery signal
        # but primary gate is 76B768 (s607 control).
        EARLY_KILL=1
        EARLY_REASON=recovery_silent
        echo "[fast-retry] attempt $ATTEMPT RECOV_WAIT expired (${RECOV_WAIT_S}s post hangar-sel, 0×76B768) — SIGKILL free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
    # Material noise can fire before recovery window ends — free reroll immediately
    if grep -aqi 'last-guest-pc\] pc=0x8000e29c' "$LOG" 2>/dev/null || \
       grep -aq 'findOrCreateMaterial+' "$LOG" 2>/dev/null; then
      if grep -aq '\[CRASH\]' "$LOG" 2>/dev/null; then
        EARLY_KILL=1
        EARLY_REASON=matnoise
        echo "[fast-retry] attempt $ATTEMPT material-noise crash mid-run — SIGKILL free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
  done
  if kill -0 "$LAUNCH_PID" 2>/dev/null; then
    wait "$LAUNCH_PID" 2>/dev/null || true
  fi
  RC=$?
  # If we SIGKILL'd the game under run_mission_keys, launcher may still report non-zero
  if [ "$EARLY_KILL" -eq 1 ]; then
    RC=137
  fi

  CASE6=0; HSEL=0; CRASH=0; ACE80=0; FORCE6=0; MATNOISE=0; RECOV=0
  if [ -f "$LOG" ]; then
    grep -aq '\[case6-force-start\]' "$LOG" && CASE6=1
    grep -aq '\[hangar-sel\]' "$LOG" && HSEL=1
    grep -aq '\[CRASH\]' "$LOG" && CRASH=1
    grep -aq 'site=0x800ACE80' "$LOG" && ACE80=1
    grep -aq '\[case5-force-state6\]' "$LOG" && FORCE6=1
    if grep -aq 'addr=0x0076B768' "$LOG" && grep -aq '\[rdp-fullsync\]' "$LOG"; then
      # count properly below; presence gate here
      if grep -aqE '\[rdp-fullsync\].*0x0076B768|addr=0x0076B768' "$LOG"; then
        RECOV=1
      fi
    fi
    if grep -aqi 'last-guest-pc\] pc=0x8000e29c' "$LOG" || \
       grep -aq 'findOrCreateMaterial+' "$LOG"; then
      MATNOISE=1
    fi
  fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[fast-retry] attempt $ATTEMPT done rc=$RC dur=${DUR}s force6=$FORCE6 case6=$CASE6 hangar_sel=$HSEL ace80=$ACE80 recov768=$RECOV crash=$CRASH matnoise=$MATNOISE early=$EARLY_REASON log=$LOG"

  if [ "$CASE6" -eq 1 ] && [ "$HSEL" -eq 1 ]; then
    if [ "$MATNOISE" -eq 1 ] && [ "$CRASH" -eq 1 ]; then
      MATERIAL_NOISE_N=$(( MATERIAL_NOISE_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but material-noise -- discard (noise_n=$MATERIAL_NOISE_N)"
      continue
    fi
    if [ "$RECOV" -eq 0 ]; then
      RECOV_SILENT_N=$(( RECOV_SILENT_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but recovery-silent (0×76B768) -- free reroll (silent_n=$RECOV_SILENT_N)"
      continue
    fi
    SCORED_LOG="$LOG"
    SCORED_RC=$RC
    echo "[fast-retry] attempt $ATTEMPT recovery-active engagement -- scoring, no further rerolls"
    break
  fi
  PRE_ENG_N=$(( PRE_ENG_N + 1 ))
  echo "[fast-retry] attempt $ATTEMPT died pre-engagement -- fast reroll (pre_eng_n=$PRE_ENG_N)"
done

if [ -z "$SCORED_LOG" ]; then
  echo "[fast-retry] no recovery-active engagement within budget (attempts=$ATTEMPT pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N)"
  exit 2
fi

echo "[fast-retry] === scored attempt analysis: $SCORED_LOG ==="
echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N attempts=$ATTEMPT"
python3 - "$SCORED_LOG" <<'PY'
import re, sys
from collections import Counter
path = sys.argv[1]
raw = open(path, errors="replace").read()
lines = raw.splitlines()

def c(pat):
    return sum(1 for l in lines if pat in l)

force6 = 1 if "[case5-force-state6]" in raw else 0
case6 = 1 if "[case6-force-start]" in raw else 0
hsel = 1 if "[hangar-sel]" in raw else 0
ace80 = 1 if "site=0x800ACE80" in raw else 0
inj_max = 0
for l in lines:
    m = re.search(r"\[fs-pipe-inject\].*\bn=(\d+)", l)
    if m:
        inj_max = max(inj_max, int(m.group(1)))
rec768 = sum(1 for l in lines if "0x0076B768" in l and "rdp-fullsync" in l)
recA90 = sum(1 for l in lines if "0x0076BA90" in l and "rdp-fullsync" in l)
sec4 = sum(1 for l in lines if "start-match: section 4" in l)
sec2 = sum(1 for l in lines if "start-match: section 2" in l)
tex_g = c("[texdata-table-guard]") + c("[texdata-ptr-array-guard]")
mat_g = c("[material-array-ptr-guard]")
vi24 = 1 if re.search(r"width=24", raw) else 0

hsel_i = next((i for i, l in enumerate(lines) if "[hangar-sel]" in l), 0)
post = lines[hsel_i:]
addrs = Counter()
for l in post:
    if "[rdp-fullsync]" in l:
        m = re.search(r"addr=(0x[0-9A-Fa-f]+)", l)
        if m:
            addrs[m.group(1)] += 1
top = ",".join(f"{a}:{n}" for a, n in addrs.most_common(6))

created_rdram = set()
for l in post:
    if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x8006F2CC" in l:
        m = re.search(r"thr_rdram=(0x[0-9A-Fa-f]+)", l)
        if m:
            created_rdram.add(m.group(1))
thr11_create = len(created_rdram)
thr11_destroy = 0
for l in post:
    if "[thr-destroy]" in l and "self" not in l:
        m = re.search(r"thr_rdram=(0x[0-9A-Fa-f]+)", l)
        if m and m.group(1) in created_rdram:
            thr11_destroy = 1
            break
sec4_post = sum(1 for l in post if "start-match: section 4" in l)
sec2_post = sum(1 for l in post if "start-match: section 2" in l)
t12_post = sum(1 for l in post if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x800495FC" in l)

m_pc = re.search(r"\[CRASH\]\[last-guest-pc\] pc=(0x[0-9a-fA-F]+)", raw)
m_sym = re.search(r"\[CRASH\]\[pc-symbol\][^\n]*", raw)
crash_pc = m_pc.group(1) if m_pc else "-"
crash = "CRASH" if "[CRASH]" in raw else "ok"
stack_blob = raw[raw.find("[CRASH] caught"): raw.find("[CRASH] caught") + 4000] if "[CRASH] caught" in raw else ""
stack_pack = 1 if "packTlutEntriesRgba5551" in stack_blob else 0
stack_debug = 1 if "loadDebugAssets" in stack_blob else 0

print(
    f"gate force6={force6} case6={case6} hangar-sel={hsel} ace80={ace80} "
    f"inject_max_n={inj_max} recov76B768~={rec768} recov76BA90~={recA90} "
    f"thr11_create={thr11_create} thr11_destroy={thr11_destroy} "
    f"sec4={sec4} sec4_post={sec4_post} sec2={sec2} sec2_post={sec2_post} "
    f"thr495FC_post={t12_post} tex_guards={tex_g} mat_guards={mat_g} vi24={vi24} "
    f"post_fs_top={top} stack_packtlut={stack_pack} stack_loaddebug={stack_debug} "
    f"crash={crash} crash_pc={crash_pc}",
    file=sys.stderr,
)
if m_sym:
    print(f"crash_sym={m_sym.group(0)}", file=sys.stderr)

if sec2_post >= 1 and crash == "ok":
    cls = "A_sec2_survive"
elif sec2_post >= 1 and stack_pack and stack_debug:
    cls = "B_sec2_packtlut_373"
elif sec2_post >= 1 and crash == "CRASH":
    cls = "C_sec2_other_crash"
elif thr11_destroy and sec4_post >= 1 and sec2_post == 0:
    cls = "D_sec4_no_sec2"
elif thr11_destroy == 0:
    cls = "E_recov_but_thr11_live"
else:
    cls = "G_other"
print(f"class_hint={cls}", file=sys.stderr)
PY

if [ -f "$SCORED_LOG" ] && grep -aq '\[CRASH\]' "$SCORED_LOG"; then
  exit 1
fi
exit 0
