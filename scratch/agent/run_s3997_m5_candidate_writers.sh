#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3997.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3989_m5_candidate_writers/s3997_m5_candidate_writers/g; s/0x8000521C,0x80005220,0x80005224/0x80005234,0x80005238,0x8000523C/g; s/0x8000521C\\|0x80005220\\|0x80005224/0x80005234|0x80005238|0x8000523C/g' "$ROOT/scratch/agent/run_s3989_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
