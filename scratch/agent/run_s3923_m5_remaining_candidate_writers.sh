#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3923.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3888_m5_remaining_candidate_writers/s3923_m5_remaining_candidate_writers/g; s/0x8006EFAC,0x80006C2C,0x80006C34/0x80004FDC,0x80004FE0,0x80004FE4/g; s/0x8006efac\|0x80006c2c\|0x80006c34/0x80004fdc|0x80004fe0|0x80004fe4/g' "$ROOT/scratch/agent/run_s3888_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
