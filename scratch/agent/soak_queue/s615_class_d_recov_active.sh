#!/bin/zsh
# s614: requeue class-D shadow-guard verify after s613 unscored hang.
# HYPOTHESIS-ID: m3-post-exit-fs-stall
#
# s613_class_d_shadow_guard fold (rc=2, 488s, NO recovery-active engagement):
#   attempt 1: force6=1 case6=0 hangar_sel=0 ace80=0 recov=0 crash=0
#   [case5-force-state6] n=40 old=3 new=6 — force fired while hangar state
#   was NOT 5 (case5-entry logged state=3). Camera-settle ACE80 never ran;
#   FORCE_CASE6_START never engaged; 488s ate the whole BUDGET for 1 attempt.
# Contrast s612 scored path: force old=6 new=6 (no-op) then natural ACE80 5→6
#   + case6 + hangar-sel + thr11d+sec4 + craft-shadow crash.
#
# s614 code change: FORCE_STATE6 only writes when old_st==5 (or no-ops at 6);
#   logs [case5-force-state6-skip] otherwise. Recipe adds ENGAGE_WAIT_S=90s
#   after first [case5-entry]: if no hangar-sel by then, SIGKILL free-reroll
#   so one stuck state=5 hang cannot burn the whole budget.
#
# Discriminating on recovery-active thr11d path (same as s613):
#   A) guard fires + thr12_post>=1 + sec2_post>=1 → class D dissolved
#   B) guard fires + thr12>=1 sec2=0 → residual thr12→sec2 handoff
#   C) guard fires + thr12=0 → still not reaching loadLevelTextureCache
#   D) guard_n=0 + same shadow crash → instrument miss / different fault
# Positive control: thr11d+sec4 => craft_shadow_asset+walk>=1 OR level_tex OR thr12.
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no recovery-active engagement, 3 force miss.

set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=560
MAX_ATTEMPTS=8
HOLD_S=180
START_FLOOR_S=80
RECOV_WAIT_S=100
ENGAGE_WAIT_S=90
POLL_S=3

GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 ROGUESQ_LOG_MAT3INV=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""
MATERIAL_NOISE_N=0
PRE_ENG_N=0
RECOV_SILENT_N=0
MAT3INV_N=0

kill_game() {
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  /usr/bin/pkill -9 -f 'run_mission_keys.sh' 2>/dev/null || true
}

is_mat3inv_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'mat3x3InverseInto' "$log" 2>/dev/null; then
    return 0
  fi
  if grep -aq '\[mat3inv-abnormal\]' "$log" 2>/dev/null && grep -aq 'Abort trap\|signal 6' "$log" 2>/dev/null; then
    return 0
  fi
  return 1
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
  TAG="s615_class_d_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  LOG="$OUT/run.log"
  kill_game
  sleep 0.3
  echo "[fast-retry] attempt $ATTEMPT starting, ${REMAIN}s left, HOLD_S=$HOLD_S RECOV_WAIT_S=$RECOV_WAIT_S ENGAGE_WAIT_S=$ENGAGE_WAIT_S tag=$TAG"
  mkdir -p "$OUT"
  env PROBE_MODE=start_only HOLD_S=$HOLD_S STICK_SCHEDULE="999:sr" \
    GAME_EXTRA_ENV="$GAME_EXTRA_ENV_BASE" \
    zsh "$ROOT/scratch/s73_post_a_scene/run_mission_keys.sh" "$TAG" 5 12 \
    >"$OUT/launcher.stdout" 2>"$OUT/launcher.stderr" &
  LAUNCH_PID=$!

  HSEL_T=0
  C5_T=0
  RECOV_SEEN=0
  EARLY_KILL=0
  EARLY_REASON=""
  while kill -0 "$LAUNCH_PID" 2>/dev/null; do
    sleep "$POLL_S"
    NOW2=$(date +%s)
    if [ $(( NOW2 - START_EPOCH )) -ge "$BUDGET_S" ]; then
      EARLY_KILL=1
      EARLY_REASON=budget
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
    [ -f "$LOG" ] || continue
    # s614: after first case5-entry, demand hangar-sel within ENGAGE_WAIT_S.
    # Prevents s613-style 488s pre-eng hang from burning the whole budget.
    if [ "$C5_T" -eq 0 ] && grep -aq '\[case5-entry\]' "$LOG" 2>/dev/null; then
      C5_T=$NOW2
      echo "[fast-retry] attempt $ATTEMPT case5-entry seen at +$((NOW2-NOW))s — ENGAGE_WAIT_S=${ENGAGE_WAIT_S}"
    fi
    if [ "$C5_T" -gt 0 ] && [ "$HSEL_T" -eq 0 ]; then
      if [ $(( NOW2 - C5_T )) -ge "$ENGAGE_WAIT_S" ]; then
        EARLY_KILL=1
        EARLY_REASON=engage_timeout
        echo "[fast-retry] attempt $ATTEMPT ENGAGE_WAIT expired (${ENGAGE_WAIT_S}s post case5-entry, 0 hangar-sel) — SIGKILL free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
    if [ "$HSEL_T" -eq 0 ] && grep -aq '\[hangar-sel\]' "$LOG" 2>/dev/null; then
      HSEL_T=$NOW2
      echo "[fast-retry] attempt $ATTEMPT hangar-sel seen at +$((NOW2-NOW))s — starting RECOV_WAIT_S=${RECOV_WAIT_S}"
    fi
    if [ "$HSEL_T" -gt 0 ] && [ "$RECOV_SEEN" -eq 0 ]; then
      if grep -aqE '\[rdp-fullsync\].*0x0076B768|addr=0x0076B768' "$LOG" 2>/dev/null; then
        RECOV_SEEN=1
        echo "[fast-retry] attempt $ATTEMPT recovery 76B768 seen at +$((NOW2-NOW))s — letting HOLD finish"
      elif [ $(( NOW2 - HSEL_T )) -ge "$RECOV_WAIT_S" ]; then
        EARLY_KILL=1
        EARLY_REASON=recovery_silent
        echo "[fast-retry] attempt $ATTEMPT RECOV_WAIT expired (${RECOV_WAIT_S}s post hangar-sel, 0×76B768) — SIGKILL free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
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
    if is_mat3inv_crash "$LOG"; then
      EARLY_KILL=1
      EARLY_REASON=mat3inv
      echo "[fast-retry] attempt $ATTEMPT mat3x3InverseInto crash mid-run — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
  done
  if kill -0 "$LAUNCH_PID" 2>/dev/null; then
    wait "$LAUNCH_PID" 2>/dev/null || true
  fi
  RC=$?
  if [ "$EARLY_KILL" -eq 1 ]; then
    RC=137
  fi

  CASE6=0; HSEL=0; CRASH=0; ACE80=0; FORCE6=0; FORCE_SKIP=0; MATNOISE=0; RECOV=0; MAT3INV=0
  if [ -f "$LOG" ]; then
    grep -aq '\[case6-force-start\]' "$LOG" && CASE6=1
    grep -aq '\[hangar-sel\]' "$LOG" && HSEL=1
    grep -aq '\[CRASH\]' "$LOG" && CRASH=1
    grep -aq 'site=0x800ACE80' "$LOG" && ACE80=1
    grep -aqE '\[case5-force-state6\] n=' "$LOG" && FORCE6=1
    grep -aq '\[case5-force-state6-skip\]' "$LOG" && FORCE_SKIP=1
    if grep -aqE '\[rdp-fullsync\].*0x0076B768|addr=0x0076B768' "$LOG"; then
      RECOV=1
    fi
    if grep -aqi 'last-guest-pc\] pc=0x8000e29c' "$LOG" || \
       grep -aq 'findOrCreateMaterial+' "$LOG"; then
      MATNOISE=1
    fi
    if is_mat3inv_crash "$LOG"; then
      MAT3INV=1
    fi
  fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[fast-retry] attempt $ATTEMPT done rc=$RC dur=${DUR}s force6=$FORCE6 force_skip=$FORCE_SKIP case6=$CASE6 hangar_sel=$HSEL ace80=$ACE80 recov768=$RECOV crash=$CRASH matnoise=$MATNOISE mat3inv=$MAT3INV early=$EARLY_REASON log=$LOG"

  if [ "$CASE6" -eq 1 ] && [ "$HSEL" -eq 1 ]; then
    if [ "$MATNOISE" -eq 1 ] && [ "$CRASH" -eq 1 ]; then
      MATERIAL_NOISE_N=$(( MATERIAL_NOISE_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but material-noise -- discard (noise_n=$MATERIAL_NOISE_N)"
      continue
    fi
    if [ "$MAT3INV" -eq 1 ]; then
      MAT3INV_N=$(( MAT3INV_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged+recov-path mat3inv Abort -- free reroll (mat3inv_n=$MAT3INV_N)"
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
  echo "[fast-retry] no recovery-active engagement within budget (attempts=$ATTEMPT pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N mat3inv=$MAT3INV_N)"
  exit 2
fi

echo "[fast-retry] === scored attempt analysis: $SCORED_LOG ==="
echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N mat3inv=$MAT3INV_N attempts=$ATTEMPT"
python3 - "$SCORED_LOG" <<'PY'
import re, sys
from collections import Counter
path = sys.argv[1]
raw = open(path, errors="replace").read()
lines = raw.splitlines()

def c(pat):
    return sum(1 for l in lines if pat in l)

force6 = 1 if re.search(r"\[case5-force-state6\] n=", raw) else 0
force_skip = 1 if "[case5-force-state6-skip]" in raw else 0
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
mat3_abn = c("[mat3inv-abnormal]")
mat3_ent = c("[mat3inv-entry]")

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

# H-ship1: post-hsel isPlayerShipActive ret=1
ship_ret1 = 0
ship_n20 = 0
ship_last = "-"
first_ship_ret1 = -1
for i, l in enumerate(post):
    if "[ship-active]" not in l:
        continue
    m = re.search(
        r"\[ship-active\] n=(\d+) ship=(0x[0-9A-Fa-f]+) ret=(\d+)", l
    )
    if not m:
        continue
    n, ship, ret = int(m.group(1)), m.group(2), int(m.group(3))
    ship_last = f"n={n} ship={ship} ret={ret}"
    if ret == 1:
        ship_ret1 += 1
        if first_ship_ret1 < 0:
            first_ship_ret1 = i
        if n >= 20:
            ship_n20 = 1

# s612 ship-store writer instrument (positive control + post-hsel re-arm)
ship_store_all = sum(1 for l in lines if "[ship-store]" in l)
ship_zero_all = sum(1 for l in lines if "[ship-zero]" in l)
ship_skip_all = sum(1 for l in lines if "[ship-store-skip]" in l)
ship_store_post = 0
ship_store_post_nonzero = 0
ship_zero_post = 0
first_store_post = -1
first_store_post_val = "-"
store_at_hsel = "-"
# store immediately around hangar-sel (±5 lines)
for j in range(max(0, hsel_i - 2), min(len(lines), hsel_i + 8)):
    if "[ship-store]" in lines[j]:
        m = re.search(r"val=(0x[0-9A-Fa-f]+) prev=(0x[0-9A-Fa-f]+)", lines[j])
        if m:
            store_at_hsel = f"val={m.group(1)} prev={m.group(2)}"
for i, l in enumerate(post):
    if "[ship-store]" in l:
        ship_store_post += 1
        m = re.search(r"val=(0x[0-9A-Fa-f]+)", l)
        val = m.group(1) if m else "0x0"
        if val != "0x00000000" and val != "0x0":
            ship_store_post_nonzero += 1
            if first_store_post < 0:
                first_store_post = i
                first_store_post_val = val
    if "[ship-zero]" in l:
        ship_zero_post += 1
ctrl_store = 1 if ship_store_all >= 1 else 0

m_pc = re.search(r"\[CRASH\]\[last-guest-pc\] pc=(0x[0-9a-fA-F]+)", raw)
m_sym = re.search(r"\[CRASH\]\[pc-symbol\][^\n]*", raw)
crash_pc = m_pc.group(1) if m_pc else "-"
crash = "CRASH" if "[CRASH]" in raw else "ok"
stack_blob = raw[raw.find("[CRASH] caught"): raw.find("[CRASH] caught") + 4000] if "[CRASH] caught" in raw else ""
stack_pack = 1 if "packTlutEntriesRgba5551" in stack_blob else 0
stack_debug = 1 if "loadDebugAssets" in stack_blob else 0
stack_mat3 = 1 if "mat3x3InverseInto" in stack_blob else 0

first768 = next((i for i, l in enumerate(post) if "0x0076B768" in l and "rdp-fullsync" in l), -1)
asset_g = sum(1 for l in lines if "[craft-shadow-asset-guard]" in l)
walk_g = sum(1 for l in lines if "[craft-shadow-walk-guard]" in l)
ltc_all = sum(1 for l in lines if "[level-tex-cache]" in l)
ltc_post = sum(1 for l in lines[hsel_i:] if "[level-tex-cache]" in l) if hsel_i else 0
shadow_crash = 1 if ("loadCraftShadowTextures" in stack_blob) else 0
print(
    f"gate force6={force6} force_skip={force_skip} case6={case6} hangar-sel={hsel} ace80={ace80} "
    f"inject_max_n={inj_max} recov76B768~={rec768} recov76BA90~={recA90} "
    f"thr11_create={thr11_create} thr11_destroy={thr11_destroy} "
    f"sec4={sec4} sec4_post={sec4_post} sec2={sec2} sec2_post={sec2_post} "
    f"thr495FC_post={t12_post} tex_guards={tex_g} mat_guards={mat_g} vi24={vi24} "
    f"mat3inv_entry={mat3_ent} mat3inv_abnormal={mat3_abn} first768_post_rel={first768} "
    f"ship_ret1_post={ship_ret1} ship_n20={ship_n20} ship_last={ship_last} "
    f"first_ship_ret1_rel={first_ship_ret1} "
    f"ship_store_all={ship_store_all} ship_zero_all={ship_zero_all} ship_skip_all={ship_skip_all} "
    f"ship_store_post={ship_store_post} ship_store_post_nz={ship_store_post_nonzero} "
    f"ship_zero_post={ship_zero_post} first_store_post_rel={first_store_post} "
    f"first_store_post_val={first_store_post_val} store_at_hsel={store_at_hsel} "
    f"ctrl_ship_store={ctrl_store} craft_shadow_asset={asset_g} craft_shadow_walk={walk_g} "
    f"level_tex_cache={ltc_all} level_tex_post={ltc_post} shadow_crash={shadow_crash} "
    f"post_fs_top={top} stack_packtlut={stack_pack} stack_loaddebug={stack_debug} "
    f"stack_mat3inv={stack_mat3} crash={crash} crash_pc={crash_pc}",
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
    if asset_g + walk_g >= 1 and t12_post >= 1:
        cls = "D_guard_thr12_no_sec2"
    elif asset_g + walk_g >= 1 and t12_post == 0:
        cls = "D_guard_no_thr12"
    elif shadow_crash:
        cls = "D_shadow_crash"
    else:
        cls = "D_sec4_no_sec2"
elif thr11_destroy and ship_ret1 >= 1:
    cls = "G_thr11d_with_ship"  # H-ship1 co-occurrence
elif thr11_destroy == 0 and stack_mat3:
    cls = "E_mat3inv_midwindow"
elif thr11_destroy == 0 and ship_ret1 >= 1:
    cls = "E_ship_stall"  # H-ship1 necessity REFUTED if this scores
elif thr11_destroy == 0 and ship_store_post_nonzero == 0:
    cls = "E_noship"  # no post-hsel re-arm store; H-ship1 still holds
elif thr11_destroy == 0:
    cls = "E_store_no_thr11d"  # store fired but thr11 live — H-ship1b weakened
else:
    cls = "G_other"
if ctrl_store == 0:
    cls = cls + "_NOCTRL"  # instrument never fired — null result
print(f"class_hint={cls}", file=sys.stderr)
PY

if [ -f "$SCORED_LOG" ] && grep -aq '\[CRASH\]' "$SCORED_LOG"; then
  exit 1
fi
exit 0
