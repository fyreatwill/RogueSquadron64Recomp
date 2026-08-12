#!/bin/zsh
set -euo pipefail

ROOT="/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp"
cd "$ROOT"

exec env BUDGET_S=600 MAX_ATTEMPTS=3 TARGET_PULSED=1 SEC2_SETTLE_S=8 \
  POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 \
  zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
