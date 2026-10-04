#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3988.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3987_m5_candidate_writers/s3988_m5_candidate_writers/g; s/0x80005204,0x80005208,0x8000520C/0x80005210,0x80005214,0x80005218/g; s/0x80005204\|0x80005208\|0x8000520C/0x80005210|0x80005214|0x80005218/g' "$ROOT/scratch/agent/run_s3987_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
