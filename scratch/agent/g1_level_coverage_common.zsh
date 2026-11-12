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
FL=""; t=${FL_START:-95}
for i in $(seq 1 100); do
  for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done
  (( t > 520 )) && break
done
FL=${FL%,}
export AP_OVERRIDE="${EARLY}${FL}"
export TAG="g1_lvl${LEVEL}${TAG_SUFFIX}" STOP=0 HOLD=${HOLD_S:-300}
export MISSION_INIT=${MISSION_INIT:-1} WAITN=${WAITN:-60}  # s6865: 60 x 5 s; lvl5/10 reach initMission at ~187 s, past the old 150 s wait
export XENV="ROGUESQ_FORCE_SAVE_MISSION=${LEVEL} ROGUESQ_FORCE_UNLOCK=${LEVEL} ${NSW_ENV-ROGUESQ_NO_SAVE_WRITE=1} ROGUESQ_AUTOPILOT_HOLD_MS=1800 ${LOG_ENV-ROGUESQ_LOG_OBJBOOL=1 ROGUESQ_LOG_HUDBIT=1} ${XENV_EXTRA:-}"
# s7229: a timing/present arm (PRESENT_RING or G1B in XENV_EXTRA) without OWNER_TIMING timed the diagnostic ucode path
# (G1E_PROBES via LOG_PHASE): L4 t=77-97 gfx task 21.95 ms -> rigid 30/s for 21 s, vs 12.95 ms / 60/s on the owner path.
# Such arms now default to OWNER_TIMING=1; pass OWNER_TIMING=0 to time the diagnostic path on purpose.
if [[ -z "${OWNER_TIMING:-}" && "${XENV_EXTRA:-}" == *(ROGUESQ_PRESENT_RING|ROGUESQ_G1B=1)* ]]; then
  export OWNER_TIMING=1; echo "[s7229] timing arm: OWNER_TIMING=1 (owner gfx path)"
fi
exec zsh scratch/agent/m6_god_common.sh
