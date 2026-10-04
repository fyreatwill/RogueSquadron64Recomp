#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3926.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3925_m5_remaining_candidate_writers/s3926_m5_remaining_candidate_writers/g; s/0x80004FF4,0x80004FF8,0x80004FFC/0x80005000,0x80005004,0x80005008/g; s/0x80004ff4\|0x80004ff8\|0x80004ffc/0x80005000|0x80005004|0x80005008/g' "$ROOT/scratch/agent/run_s3925_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
