#!/bin/zsh
# s6711 G1e per-frame timeline (ROGUESQ_G1E_TL ring -> binary file, tools/g1e_tl.py) at lvl5 FPS60 dd4, ASYNC=1 NODRAIN=1 (s6709 opt-in arm).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
arm=${1:-tl}; lvl=${2:-5}; dd=${3:-4}
TL=$PWD/scratch/agent/s6711_tl_${arm}_lvl${lvl}.bin; rm -f $TL.*
X="ROGUESQ_STORE_DIAG=0 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=$dd ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=1 ROGUESQ_G1E_TL=$TL "
env ROGUESQ_G1B=1 FBD_EVERY_V=600 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' \
  XENV_EXTRA="$X" HOLD_S=240 LEVEL=$lvl TAG_SUFFIX=s6711_$arm zsh scratch/agent/g1_level_coverage_common.zsh > /tmp/s6711_$arm.out 2>&1
cat scratch/agent/m6/g1_lvl${lvl}s6711_$arm/summary; ls -la $TL.*
