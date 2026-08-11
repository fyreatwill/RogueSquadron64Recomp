#!/bin/zsh
# s666: productize DROP_GARBAGE_CIMG default ON + freeroll restore retirement.
# HYPOTHESIS-ID: cimg-origin-desync
#
# Product: drop ON with no env; opt-out DROP_GARBAGE_CIMG=0 or ALLOW_GARBAGE_CIMG=1.
# Arms (same binary, product drop always ON unless C):
#   A: product defaults (drop ON, restore ON) — baseline pipeline scores
#   B: product drop ON + ROGUESQ_FL_HDR_RESTORE=0 — restore-redundant test
#   C: ROGUESQ_DROP_GARBAGE_CIMG=0 + restore OFF — opt-out control (killer+stomp)
#
# Discriminators:
#   [cimg] DROP_GARBAGE_CIMG product ON  → product default LIVE (no env)
#   [cimg-garbage-drop] / kill_drop     → filter acting
#   freelist to_zero 0x2/0x60           → freelist-shaped stomp
#   recov768 / thr11d_new / fail136c    → pipeline score
#   [cimg-raw] OK                       → posctrl
set -u
ROOT="/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

ARM="${1:?arm A|B|C}"
BUDGET_S="${BUDGET_S:-900}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-6}"
HOLD_S="${HOLD_S:-210}"
RECOV_WAIT_S="${RECOV_WAIT_S:-50}"
ENGAGE_WAIT_S="${ENGAGE_WAIT_S:-90}"
START_FLOOR_S=70
POLL_S=3

BASE_ENV="ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_LOG_CIMG_RAW=1 ROGUESQ_LOG_DL_SYNC2=1 ROGUESQ_LOG_CIMG=1 ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_RS_MALLOC_DIAG=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1"

case "$ARM" in
  A|a)
    ARM_TAG="A_prod_restore"
    # product drop ON (no DROP env), product restore ON (no FL_HDR_RESTORE=0)
    EXTRA=""
    ;;
  B|b)
    ARM_TAG="B_prod_norestore"
    EXTRA="ROGUESQ_FL_HDR_RESTORE=0"
    ;;
  C|c)
    ARM_TAG="C_optout_norestore"
    EXTRA="ROGUESQ_DROP_GARBAGE_CIMG=0 ROGUESQ_FL_HDR_RESTORE=0"
    ;;
  *)
    echo "unknown arm $ARM (want A|B|C)" >&2
    exit 2
    ;;
esac

GAME_EXTRA_ENV_BASE="$BASE_ENV $EXTRA"

START_EPOCH=$(date +%s)
ATTEMPT=0
ENGAGED_N=0
RECOV_ACTIVE_N=0
RECOV_SILENT_N=0
PRE_ENG_N=0
MATNOISE_N=0
BEST_LOG=""
SUM_THR11D=0
SUM_FAIL136=0
SUM_FLZ=0
SUM_KILL=0
SUM_KDROP=0
SUM_DROP=0
SUM_BANNER=0
SUM_OK=0

kill_game() {
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  /usr/bin/pkill -9 -f 'run_mission_keys.sh' 2>/dev/null || true
}

echo "[s666-$ARM_TAG] start EXTRA=[$EXTRA] BUDGET_S=$BUDGET_S HOLD_S=$HOLD_S"

while :; do
  NOW=$(date +%s)
  ELAPSED=$(( NOW - START_EPOCH ))
  REMAIN=$(( BUDGET_S - ELAPSED ))
  if [ "$REMAIN" -lt "$START_FLOOR_S" ]; then
    echo "[s666-$ARM_TAG] budget exhausted (${ELAPSED}s used)"
    break
  fi
  ATTEMPT=$(( ATTEMPT + 1 ))
  if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
    echo "[s666-$ARM_TAG] hit MAX_ATTEMPTS=$MAX_ATTEMPTS"
    break
  fi
  TAG="s666_${ARM_TAG}_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  LOG="$OUT/run.log"
  kill_game
  sleep 0.4
  echo "[s666-$ARM_TAG] attempt $ATTEMPT starting, ${REMAIN}s left, tag=$TAG"
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
    if [ "$C5_T" -eq 0 ] && grep -aq '\[case5-entry\]' "$LOG" 2>/dev/null; then
      C5_T=$NOW2
      echo "[s666-$ARM_TAG] attempt $ATTEMPT case5-entry +$((NOW2-NOW))s"
    fi
    if [ "$C5_T" -gt 0 ] && [ "$HSEL_T" -eq 0 ]; then
      if [ $(( NOW2 - C5_T )) -ge "$ENGAGE_WAIT_S" ]; then
        EARLY_KILL=1
        EARLY_REASON=engage_timeout
        echo "[s666-$ARM_TAG] attempt $ATTEMPT ENGAGE_WAIT — free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
    if [ "$HSEL_T" -eq 0 ] && grep -aq '\[hangar-sel\]' "$LOG" 2>/dev/null; then
      HSEL_T=$NOW2
      echo "[s666-$ARM_TAG] attempt $ATTEMPT hangar-sel +$((NOW2-NOW))s"
    fi
    if [ "$HSEL_T" -gt 0 ] && [ "$RECOV_SEEN" -eq 0 ]; then
      if grep -aqE 'addr=0x0076B768' "$LOG" 2>/dev/null; then
        RECOV_SEEN=1
        echo "[s666-$ARM_TAG] attempt $ATTEMPT recovery 76B768 +$((NOW2-NOW))s — HOLD"
      elif [ $(( NOW2 - HSEL_T )) -ge "$RECOV_WAIT_S" ]; then
        EARLY_KILL=1
        EARLY_REASON=recovery_silent
        echo "[s666-$ARM_TAG] attempt $ATTEMPT RECOV_WAIT silent — free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
    if grep -aq '\[CRASH\]' "$LOG" 2>/dev/null; then
      if grep -aqE 'mat3x3InverseInto|findOrCreateMaterial|sinfApprox' "$LOG" 2>/dev/null; then
        EARLY_KILL=1
        EARLY_REASON=matnoise
        echo "[s666-$ARM_TAG] attempt $ATTEMPT matnoise — free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
  done
  wait "$LAUNCH_PID" 2>/dev/null || true

  N_OK=0; N_KILL=0; N_KDROP=0; N_DROP=0; N_BANNER=0; N_BANNER_OFF=0; N_FLZ=0
  N_HIT=0; N_CRASH=0; FORCE6=0; HSEL=0; CASE6=0; RECOV768=0
  THR11D=0; FAIL136=0; CRAFT=0; RESTORE_OK=0; PROD_RESTORE=0
  gcn() { local n; n=$(grep -cE "$1" "$2" 2>/dev/null) || n=0; printf '%s' "${n//$'\n'/}"; }
  if [ -f "$LOG" ]; then
    N_OK=$(gcn '\[cimg-raw\] OK ' "$LOG")
    N_KILL=$(gcn '\[cimg-raw\] KILLER ' "$LOG")
    N_KDROP=$(gcn '\[cimg-raw\] KILLER_DROP|\[cimg-garbage-drop\].*w=1161|\[cimg-garbage-drop\].*0x1F0D74' "$LOG")
    N_DROP=$(gcn '\[cimg-garbage-drop\]' "$LOG")
    N_BANNER=$(gcn 'DROP_GARBAGE_CIMG product ON|DROP_GARBAGE_CIMG=1' "$LOG")
    N_BANNER_OFF=$(gcn 'DROP_GARBAGE_CIMG OFF' "$LOG")
    N_FLZ=$(gcn '\[fl-zero-poll\].*to_zero.*prev_f=0x2.*prev_sz=0x60|to_zero phys=0x1F3CC0 prev_f=0x2 prev_sz=0x60' "$LOG")
    N_HIT=$(gcn '\[fb-fl-writeback\].*addrStart=0x1F0D74|HIT_WRITE.*1F0D74|ALLOW_WILD_FL.*1F0D74|SKIP_WILD_W.*1F0D74|HIT_WRITE_RESTORE.*1F0D74' "$LOG")
    N_CRASH=$(gcn '\[CRASH\]' "$LOG")
    RESTORE_OK=$(grep '\[fb-fl-hdr-restore\]' "$LOG" 2>/dev/null | grep -c 'match=1' || true)
    RESTORE_OK=${RESTORE_OK:-0}
    PROD_RESTORE=$(gcn 'product restore=' "$LOG")
    grep -aq '\[case5-force-state6\]' "$LOG" && FORCE6=1
    grep -aq '\[hangar-sel\]' "$LOG" && HSEL=1
    grep -aq '\[case6-force-start\]' "$LOG" && CASE6=1
    grep -aqE 'addr=0x0076B768' "$LOG" && RECOV768=1
    if grep -aq '\[rs-malloc-diag\] event=fail136c' "$LOG" 2>/dev/null; then FAIL136=1; fi
    # thr11d_new: post-hsel thr-create entry=0x8006F2CC whose id is later destroyed
    hsel_line=$(grep -n '\[hangar-sel\]' "$LOG" 2>/dev/null | head -1 | cut -d: -f1)
    if [ -n "${hsel_line:-}" ]; then
      post=$(sed -n "${hsel_line},\$p" "$LOG")
      create_ids=$(printf '%s\n' "$post" | grep -E '\[thr-create\].*entry=0x8006F2CC' | sed -E 's/.*id=([0-9]+).*/\1/' | sort -u)
      for cid in $create_ids; do
        if printf '%s\n' "$post" | grep -qE "\[thr-destroy\] id=${cid} "; then
          THR11D=$(( THR11D + 1 ))
        fi
      done
    fi
  fi
  N_OK=${N_OK:-0}; N_KILL=${N_KILL:-0}; N_KDROP=${N_KDROP:-0}; N_DROP=${N_DROP:-0}
  N_BANNER=${N_BANNER:-0}; N_BANNER_OFF=${N_BANNER_OFF:-0}; N_FLZ=${N_FLZ:-0}
  N_HIT=${N_HIT:-0}; N_CRASH=${N_CRASH:-0}; RESTORE_OK=${RESTORE_OK:-0}
  PROD_RESTORE=${PROD_RESTORE:-0}

  echo "[s666-$ARM_TAG] attempt $ATTEMPT: ok=$N_OK kill_applied=$N_KILL kill_drop=$N_KDROP drop=$N_DROP banner=$N_BANNER banner_off=$N_BANNER_OFF flz_fl=$N_FLZ fb_hit=$N_HIT restore_ok=$RESTORE_OK prod_restore_banner=$PROD_RESTORE force6=$FORCE6 case6=$CASE6 hsel=$HSEL recov768=$RECOV768 thr11d_new=$THR11D fail136c=$FAIL136 crash=$N_CRASH early=$EARLY_REASON log=$LOG"

  SUM_OK=$(( SUM_OK + ${N_OK:-0} ))
  SUM_KILL=$(( SUM_KILL + ${N_KILL:-0} ))
  SUM_KDROP=$(( SUM_KDROP + ${N_KDROP:-0} ))
  SUM_DROP=$(( SUM_DROP + ${N_DROP:-0} ))
  SUM_BANNER=$(( SUM_BANNER + ${N_BANNER:-0} ))
  SUM_FLZ=$(( SUM_FLZ + ${N_FLZ:-0} ))
  BEST_LOG=$LOG

  if [ "$CASE6" -eq 1 ] && [ "$HSEL" -eq 1 ]; then
    ENGAGED_N=$(( ENGAGED_N + 1 ))
    if [ "$EARLY_REASON" = "matnoise" ]; then
      MATNOISE_N=$(( MATNOISE_N + 1 ))
      continue
    fi
    if [ "$RECOV768" -eq 1 ]; then
      RECOV_ACTIVE_N=$(( RECOV_ACTIVE_N + 1 ))
      SUM_THR11D=$(( SUM_THR11D + THR11D ))
      SUM_FAIL136=$(( SUM_FAIL136 + FAIL136 ))
      # keep going for a second engaged if budget allows; stop after 2 recovery-active
      if [ "$RECOV_ACTIVE_N" -ge 2 ]; then
        echo "[s666-$ARM_TAG] SCORED 2× recovery-active"
        break
      fi
    else
      RECOV_SILENT_N=$(( RECOV_SILENT_N + 1 ))
    fi
  else
    PRE_ENG_N=$(( PRE_ENG_N + 1 ))
  fi
done

echo "[s666-$ARM_TAG] SUMMARY engaged=$ENGAGED_N recov_active=$RECOV_ACTIVE_N recov_silent=$RECOV_SILENT_N pre_eng=$PRE_ENG_N matnoise=$MATNOISE_N thr11d_sum=$SUM_THR11D fail136_sum=$SUM_FAIL136 flz_sum=$SUM_FLZ kill_sum=$SUM_KILL kdrop_sum=$SUM_KDROP drop_sum=$SUM_DROP banner_sum=$SUM_BANNER ok_sum=$SUM_OK best_log=$BEST_LOG"
exit 0
