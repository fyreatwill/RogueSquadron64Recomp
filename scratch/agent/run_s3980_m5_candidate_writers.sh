#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3980.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3967_m5_candidate_writers/s3980_m5_candidate_writers/g; s/0x80005168,0x8000516C,0x80005170/0x800051C8,0x800051CC,0x800051D0/g; s/0x80005168\|0x8000516C\|0x80005170/0x800051C8|0x800051CC|0x800051D0/g' "$ROOT/scratch/agent/run_s3967_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
