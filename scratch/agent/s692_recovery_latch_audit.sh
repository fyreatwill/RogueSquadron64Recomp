#!/bin/zsh
# HYPOTHESIS-ID: m3-recovery-latch-readiness
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
RUNNER=$ROOT/scratch/agent/s670_run_mission_keys_postsec2.sh
S689_COMMIT=0f2cd78e
STAMP=$(date +%Y%m%d%H%M%S)
OUT=$ROOT/scratch/s73_post_a_scene/s692_recovery_latch_audit_$STAMP
SAVED=$ROOT/scratch/s73_post_a_scene/s670_postsec2_pulse_1_20260812051415/run.log
mkdir -p "$OUT"

CURRENT_BASE=$(sed -n 's/^GAME_EXTRA_ENV_BASE="\(.*\)"$/\1/p' "$ROOT/scratch/agent/s670_postsec2_pulse_freeroll.sh")
S689_BASE=$(git show "${S689_COMMIT}:scratch/agent/s670_postsec2_pulse_freeroll.sh" | sed -n 's/^GAME_EXTRA_ENV_BASE="\(.*\)"$/\1/p')

{
  print "[s692] stamp=$STAMP"
  print "[s692] historical_commit=$S689_COMMIT"
  print "[s692] current_freeroll_sha=$(shasum "$ROOT/scratch/agent/s670_postsec2_pulse_freeroll.sh" | awk '{print $1}')"
  print "[s692] historical_freeroll_sha=$(git show "${S689_COMMIT}:scratch/agent/s670_postsec2_pulse_freeroll.sh" | shasum | awk '{print $1}')"
  print "[s692] current_runner_sha=$(shasum "$RUNNER" | awk '{print $1}')"
  print "[s692] historical_runner_sha=$(git show "${S689_COMMIT}:scratch/agent/s670_run_mission_keys_postsec2.sh" | shasum | awk '{print $1}')"
  print "[s692] s689_base=$S689_BASE"
  print "[s692] current_base=$CURRENT_BASE"
  print "[s692] inherited_roguesq_begin"
  env | LC_ALL=C sort | grep '^ROGUESQ_' || true
  print "[s692] inherited_roguesq_end"
} > "$OUT/audit.txt"

score() {
  local label=$1 log=$2
  local literal fullsync slot control
  literal=$(grep -ac '0x0076B768' "$log" 2>/dev/null || true)
  fullsync=$(grep -ac '\[rdp-fullsync\].*addr=0x0076B768' "$log" 2>/dev/null || true)
  slot=$(grep -ac '\[fs-slot\].*fs_addr=0x0076B768' "$log" 2>/dev/null || true)
  control=$(grep -ac '\[e9-prov\].*scope=control.*guest=1.*dispatch=1' "$log" 2>/dev/null || true)
  print "[s692-score] arm=$label literal_76B768=$literal fullsync_76B768=$fullsync fs_slot_76B768=$slot boot_e9_controls=$control" | tee -a "$OUT/audit.txt"
}

if [[ ! -f "$SAVED" || -z "$CURRENT_BASE" || -z "$S689_BASE" ]]; then
  print "[s692] ERROR missing saved control or effective environment" | tee -a "$OUT/audit.txt"
  exit 2
fi
score saved_s689 "$SAVED"

launch_arm() {
  local label=$1
  local extra=$2
  local tag="s692_${label}_$STAMP"
  print "[s692] launch arm=$label tag=$tag" >> "$OUT/audit.txt"
  env PROBE_MODE=start_only SEC2_PULSE=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 \
    GAME_EXTRA_ENV="$extra" zsh "$RUNNER" "$tag" 5 12 >"$OUT/${label}.stdout" 2>"$OUT/${label}.stderr" &
  LAUNCH_PID=$!
}

launch_arm s689_compat "$S689_BASE"
P1=$LAUNCH_PID
launch_arm current "$CURRENT_BASE"
P2=$LAUNCH_PID
print "[s692] launcher_pids s689_compat=$P1 current=$P2" >> "$OUT/audit.txt"

wait "$P1"; R1=$?
wait "$P2"; R2=$?
score s689_compat "$ROOT/scratch/s73_post_a_scene/s692_s689_compat_$STAMP/run.log"
score current "$ROOT/scratch/s73_post_a_scene/s692_current_$STAMP/run.log"
print "[s692] launcher_rc s689_compat=$R1 current=$R2" >> "$OUT/audit.txt"
print "[s692] outputs=$OUT" | tee -a "$OUT/audit.txt"
