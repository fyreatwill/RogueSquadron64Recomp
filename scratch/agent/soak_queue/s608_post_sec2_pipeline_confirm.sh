#!/bin/zsh
# s608: re-confirm thr11→sec4→sec2 pipeline (s607 scored first hit) and
# classify post-sec2 outcome. HYPOTHESIS-ID: m3-post-exit-fs-stall
#
# s607/s608 fold: force6+inject engaged without material noise; thr11_destroy=1
# recov76B768~=92 recov76BA90=0 sec4_post=1 sec2_post=1; crash post-sec2 in
# packTlutEntriesRgba5551 via loadDebugAssets (item -373). H-handoff2 REFUTED.
#
# Discard: pre-engagement deaths + material noise 0x8000e29c / findOrCreateMaterial.
# Score first engaged non-noise attempt; classify by sec2 + crash identity.
#
# Discriminating outcomes (scored = engaged AND not material-noise):
#   A) sec2_post + ok → in-mission hold
#   B) sec2_post + packTlut/loadDebugAssets stack → -373 2nd
#   C) sec2_post + other crash → new breadcrumb
#   D) thr11_destroy+sec4, sec2=0 → regression
#   E/F) budget exhaust material/pre-eng only
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no non-noise engagement, 3 force miss.
set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=580
MAX_ATTEMPTS=8
HOLD_S=180
START_FLOOR_S=100
GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""
MATERIAL_NOISE_N=0
PRE_ENG_N=0

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
  TAG="s608_post_sec2_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  sleep 0.3
  echo "[fast-retry] attempt $ATTEMPT starting, ${REMAIN}s left in budget, HOLD_S=$HOLD_S tag=$TAG"
  env PROBE_MODE=start_only HOLD_S=$HOLD_S STICK_SCHEDULE="999:sr" \
    GAME_EXTRA_ENV="$GAME_EXTRA_ENV_BASE" \
    zsh "$ROOT/scratch/s73_post_a_scene/run_mission_keys.sh" "$TAG" 5 12
  RC=$?
  LOG="$OUT/run.log"
  CASE6=0; HSEL=0; CRASH=0; ACE80=0; FORCE6=0; MATNOISE=0
  if [ -f "$LOG" ]; then
    grep -aq '\[case6-force-start\]' "$LOG" && CASE6=1
    grep -aq '\[hangar-sel\]' "$LOG" && HSEL=1
    grep -aq '\[CRASH\]' "$LOG" && CRASH=1
    grep -aq 'site=0x800ACE80' "$LOG" && ACE80=1
    grep -aq '\[case5-force-state6\]' "$LOG" && FORCE6=1
    if grep -aqi 'last-guest-pc\] pc=0x8000e29c' "$LOG" || \
       grep -aq 'findOrCreateMaterial+' "$LOG"; then
      MATNOISE=1
    fi
  fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[fast-retry] attempt $ATTEMPT done rc=$RC dur=${DUR}s force6=$FORCE6 case6=$CASE6 hangar_sel=$HSEL ace80=$ACE80 crash=$CRASH matnoise=$MATNOISE log=$LOG"
  if [ "$CASE6" -eq 1 ] && [ "$HSEL" -eq 1 ]; then
    if [ "$MATNOISE" -eq 1 ]; then
      MATERIAL_NOISE_N=$(( MATERIAL_NOISE_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but material-noise death (0x8000e29c) -- discard, reroll (noise_n=$MATERIAL_NOISE_N)"
      continue
    fi
    SCORED_LOG="$LOG"
    SCORED_RC=$RC
    echo "[fast-retry] attempt $ATTEMPT reached engagement WITHOUT material noise -- scoring, no further rerolls"
    break
  fi
  PRE_ENG_N=$(( PRE_ENG_N + 1 ))
  echo "[fast-retry] attempt $ATTEMPT died pre-engagement -- fast reroll (pre_eng_n=$PRE_ENG_N)"
done

if [ -z "$SCORED_LOG" ]; then
  echo "[fast-retry] no non-noise engagement within budget (attempts=$ATTEMPT pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N)"
  exit 2
fi

echo "[fast-retry] === scored attempt analysis: $SCORED_LOG ==="
echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N attempts=$ATTEMPT"
python3 - "$SCORED_LOG" <<'PY'
import re, sys
path = sys.argv[1]
raw = open(path, errors="replace").read()
lines = raw.splitlines()

def c(pat):
    return sum(1 for l in lines if pat in l)

force6 = 1 if "[case5-force-state6]" in raw else 0
case6 = 1 if "[case6-force-start]" in raw else 0
hsel = 1 if "[hangar-sel]" in raw else 0
ace80 = 1 if "site=0x800ACE80" in raw else 0
inj_lines = c("[fs-pipe-inject]")
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

# post hangar-sel window for thr11
hsel_i = next((i for i, l in enumerate(lines) if "[hangar-sel]" in l), 0)
post = lines[hsel_i:]
last_768_rel = -1
first_a90_rel = -1
for i, l in enumerate(post):
    if "0x0076B768" in l and "rdp-fullsync" in l:
        last_768_rel = i
    if first_a90_rel < 0 and "0x0076BA90" in l and "rdp-fullsync" in l:
        first_a90_rel = i

t12 = sum(1 for l in lines if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x800495FC" in l)
thr11_create = sum(1 for l in post if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x8006F2CC" in l)
created_rdram = set()
for l in post:
    if "[thr-create]" in l and "thr-create-id" not in l and "entry=0x8006F2CC" in l:
        m = re.search(r"thr_rdram=(0x[0-9A-Fa-f]+)", l)
        if m:
            created_rdram.add(m.group(1))
thr11_destroy = 0
thr11_destroy_rel = -1
for i, l in enumerate(post):
    if "[thr-destroy]" in l and "self" not in l:
        m = re.search(r"thr_rdram=(0x[0-9A-Fa-f]+)", l)
        if m and m.group(1) in created_rdram:
            thr11_destroy = 1
            thr11_destroy_rel = i
            break
sec4_post = sum(1 for l in post if "start-match: section 4" in l)
sec2_post = sum(1 for l in post if "start-match: section 2" in l)

g1 = c("[coalesce-heap-guard]")
g2 = c("[coalesce-heap-r2-guard]")
bf = c("[beginframe-s0-guard]")
m_pc = re.search(r"\[CRASH\]\[last-guest-pc\] pc=(0x[0-9a-fA-F]+)", raw)
m_sym = re.search(r"\[CRASH\]\[pc-symbol\][^\n]*", raw)
crash_pc = m_pc.group(1) if m_pc else "-"
crash_sym = m_sym.group(0) if m_sym else "-"
crash = "CRASH" if "[CRASH]" in raw else "ok"
crash_rel = -1
for i, l in enumerate(post):
    if "[CRASH] caught" in l:
        crash_rel = i
        break

packtlut = 1 if re.search(r"packTlutEntriesRgba5551", raw) and crash == "CRASH" else 0
loaddebug = 1 if re.search(r"loadDebugAssets", raw) and crash == "CRASH" else 0
# host stack markers in crash dump region
stack_blob = raw[raw.find("[CRASH] caught"): raw.find("[CRASH] caught") + 4000] if "[CRASH] caught" in raw else ""
stack_pack = 1 if "packTlutEntriesRgba5551" in stack_blob else 0
stack_debug = 1 if "loadDebugAssets" in stack_blob else 0

print(
    f"gate force6={force6} case6={case6} hangar-sel={hsel} ace80={ace80} "
    f"inject_lines={inj_lines} inject_max_n={inj_max} "
    f"recov76B768~={rec768} recov76BA90~={recA90} "
    f"last_768_rel={last_768_rel} first_a90_rel={first_a90_rel} "
    f"thr11_destroy_rel={thr11_destroy_rel} crash_rel={crash_rel} "
    f"sec4={sec4} sec4_post={sec4_post} sec2={sec2} sec2_post={sec2_post} "
    f"thr495FC_creates={t12} thr11_create={thr11_create} thr11_destroy={thr11_destroy} "
    f"coalesce_guard1={g1} coalesce_guard2_r2={g2} beginframe_s0_guard={bf} "
    f"tex_guards={tex_g} mat_guards={mat_g} vi24={vi24} "
    f"stack_packtlut={stack_pack} stack_loaddebug={stack_debug} "
    f"crash={crash} crash_pc={crash_pc}",
    file=sys.stderr,
)
if m_sym:
    print(f"crash_sym={crash_sym}", file=sys.stderr)

cls = "?"
if force6 == 0:
    cls = "G_force6_miss"
elif sec2_post >= 1 and crash == "ok":
    cls = "A_sec2_survive"
elif sec2_post >= 1 and stack_pack and stack_debug:
    cls = "B_sec2_packtlut_373"
elif sec2_post >= 1 and crash == "CRASH":
    cls = "C_sec2_other_crash"
elif thr11_destroy and sec4_post >= 1 and sec2_post == 0:
    cls = "D_sec4_no_sec2"
elif thr11_destroy == 0 and crash == "ok" and hsel:
    cls = "F_survive_no_thr11"
elif thr11_destroy == 0 and hsel:
    cls = "E_thr11_still_live"
else:
    cls = "G_other"
print(f"class_hint={cls}", file=sys.stderr)
PY

if [ -f "$SCORED_LOG" ] && grep -aq '\[CRASH\]' "$SCORED_LOG"; then
  exit 1
fi
exit 0
