#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3916.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3888_m5_remaining_candidate_writers/s3916_m5_remaining_candidate_writers/g; s/0x8006EFAC,0x80006C2C,0x80006C34/0x80004FA0,0x80004FA4,0x80004FA8/g; s/0x8006efac\|0x80006c2c\|0x80006c34/0x80004fa0|0x80004fa4|0x80004fa8/g' "$ROOT/scratch/agent/run_s3888_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
