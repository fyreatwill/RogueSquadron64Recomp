#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3976.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3967_m5_candidate_writers/s3976_m5_candidate_writers/g; s/0x80005168,0x8000516C,0x80005170/0x800051B0,0x800051B4,0x800051B8/g; s/0x80005168\|0x8000516C\|0x80005170/0x800051B0|0x800051B4|0x800051B8/g' "$ROOT/scratch/agent/run_s3967_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
