#!/bin/zsh
# s607: same dual-target as s606, but re-roll post-engagement deaths at
# material noise guest PC 0x8000e29c (findOrCreateMaterial via
# emitMaterialTexturedDL). HYPOTHESIS-ID: m3-post-exit-fs-stall
#
# s606 scored E0: force6=1 case6=1 hangar-sel=1 ace80=1, thr11 create,
# inject_max_n=450, recov76B768=0 recov76BA90=0, thr11_destroy=0,
# crash 0x8000e29c / findOrCreateMaterial+776 (2nd occ after s605).
# s605 had recov76B768~=7920 + same crash; s602 (no force6) survived
# recov=0 path to HOLD end without thr11 destroy. Material death is
# independent of 76B768 presence and aborts thr11→sec4 before handoff.
#
# Discriminating outcomes (scored = engaged AND not material-noise death):
#   A) thr11_destroy + sec4_post + g2 + ok → -361 confirm 1/2
#   B) thr11_destroy + sec4_post + crash 0x8000247c → r2 path
#   C) thr11_destroy + sec4_post + other crash → file
#   D) recov76BA90>=1 thr11_destroy=0 → handoff insufficient
#   E) recov76B768>0 no 76BA90 non-material crash → gap H-handoff1 variant
#   F) engaged survive HOLD thr11_destroy=0 (like s602) → cutscene not finishing
#   G) budget exhaust: only material noise / pre-eng deaths
#   H) 76BA90 + thr11_destroy (any crash) → handoff sufficiency hit
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
GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1"

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
  TAG="s607_handoff_matnoise_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
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
    # Material noise: guest PC 0x8000e29c (delay-slot before findOrCreateMaterial)
    # OR host symbol findOrCreateMaterial+NNN. 2nd occ s605/s606; discard+reroll.
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
rec768 = raw.count("76B768")
recA90 = sum(1 for l in post if "76BA90" in l)
last_768_rel = -1
first_a90_rel = -1
for i, l in enumerate(post):
    if "76B768" in l:
        last_768_rel = i
    if first_a90_rel < 0 and "76BA90" in l:
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
afa0 = 1 if re.search(r"0x8000afa0", raw, re.I) else 0
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
print(
    f"gate force6={force6} case6={case6} hangar-sel={hsel} ace80={ace80} "
    f"inject_lines={inj_lines} inject_max_n={inj_max} "
    f"recov76B768~={rec768} recov76BA90~={recA90} "
    f"last_768_rel={last_768_rel} first_a90_rel={first_a90_rel} "
    f"thr11_destroy_rel={thr11_destroy_rel} crash_rel={crash_rel} "
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
    cls = "G_force6_miss"
elif thr11_destroy and sec4_post >= 1 and g2 >= 1 and crash == "ok":
    cls = "A_item361_confirm"
elif thr11_destroy and sec4_post >= 1 and crash_pc.lower() == "0x8000247c":
    cls = "B_r2_path"
elif thr11_destroy and sec4_post >= 1 and crash == "CRASH":
    cls = "C_sec4_other_crash"
elif recA90 >= 1 and thr11_destroy == 0:
    cls = "D_handoff_no_thr11"
elif recA90 >= 1 and thr11_destroy == 1:
    cls = "H_handoff_thr11"
elif last_768_rel > 0 and recA90 == 0 and crash == "CRASH":
    cls = "E_gap_crash_no_handoff"
elif thr11_destroy == 0 and crash == "ok" and hsel:
    cls = "F_survive_no_thr11"
elif thr11_destroy == 0 and hsel:
    cls = "E_thr11_still_live"
else:
    cls = "G_other"
print(f"class_hint={cls}", file=sys.stderr)
PY

# exit code mirrors scored crash
if [ -f "$SCORED_LOG" ] && grep -aq '\[CRASH\]' "$SCORED_LOG"; then
  exit 1
fi
exit 0
