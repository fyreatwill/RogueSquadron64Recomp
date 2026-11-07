#!/bin/zsh
# s6932: owner recipe flight run for present measurements: FPS60, dd, ASPECT, FULLSCREEN, no ASYNC/NODRAIN, no recipe logging.
# scratch/s6890/bridge.zsh forces ASYNC+NODRAIN, which the owner does not run. Same key schedule as that bridge.
# usage: env HOLD_S=240 zsh tools/g1e_owner_bridge.zsh LEVEL DD ARM "EXTRA ENV"   (ASPECT env: OWNER_ASPECT, default 16:9; OWNER_FS, default 1)
cd "$(git rev-parse --show-toplevel)" || exit 1
lvl=${1:-1}; dd=${2:-4}; arm=${3:-x}; EX=${4:-}
EARLY=""; e=10
for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; EARLY="$EARLY$e:$k,"; e=$((e+4)); done
FL=""; t=95
for i in $(seq 1 100); do for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 520 )) && break; done
export AP_OVERRIDE="${EARLY}${FL%,}" TAG="g1_lvl${lvl}s6932_$arm" STOP=0 HOLD=${HOLD_S:-200}
export XENV="ROGUESQ_FORCE_SAVE_MISSION=$lvl ROGUESQ_FORCE_UNLOCK=$lvl ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_STORE_DIAG=0 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=$dd ROGUESQ_ASPECT=${OWNER_ASPECT:-16:9} ROGUESQ_FULLSCREEN=${OWNER_FS:-1} ROGUESQ_G1E_AQ=2 ROGUESQ_G1E_FAST=1 ROGUESQ_G1E_PROBES=0 $EX"
env ROGUESQ_G1B=1 FBD_EVERY_V=600 FBH_V=0 TRI_V=0 DRAWN_V=0 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' zsh scratch/agent/m6_god_common.sh > /tmp/s6932_$arm.out 2>&1
cat scratch/agent/m6/$TAG/summary
