#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3984.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3967_m5_candidate_writers/s3984_m5_candidate_writers/g; s/0x80005168,0x8000516C,0x80005170/0x800051EC,0x800051F0,0x800051F4/g; s/0x80005168\\|0x8000516C\\|0x80005170/0x800051EC|0x800051F0|0x800051F4/g; s/ROGUESQ_AUDIO_UCODE=1 /ROGUESQ_AUDIO_UCODE=1 ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1 /' "$ROOT/scratch/agent/run_s3967_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
