#!/bin/zsh
# G1 forced-level coverage. The caller supplies LEVEL and TAG_SUFFIX.
# SOAK_TIMEOUT=900
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
LEVEL=${LEVEL:?missing LEVEL}
TAG_SUFFIX=${TAG_SUFFIX:?missing TAG_SUFFIX}
EARLY=""; e=10
for i in $(seq 1 20); do
  if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi
  EARLY="$EARLY$e:$k,"; e=$((e+4))
done
FL=""; t=95
for i in $(seq 1 100); do
  for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done
  (( t > 520 )) && break
done
FL=${FL%,}
export AP_OVERRIDE="${EARLY}${FL}"
export TAG="g1_lvl${LEVEL}${TAG_SUFFIX}" STOP=0 HOLD=300
export XENV="ROGUESQ_FORCE_SAVE_MISSION=${LEVEL} ROGUESQ_FORCE_UNLOCK=${LEVEL} ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_LOG_OBJBOOL=1 ROGUESQ_LOG_HUDBIT=1"
exec zsh scratch/agent/m6_god_common.sh
