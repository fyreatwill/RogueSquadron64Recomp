#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3968.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3967_m5_candidate_writers/s3968_m5_candidate_writers/g; s/0x80005168,0x8000516C,0x80005170/0x80005174,0x80005178,0x8000517C/g; s/0x80005168\|0x8000516C\|0x80005170/0x80005174|0x80005178|0x8000517C/g' "$ROOT/scratch/agent/run_s3967_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
