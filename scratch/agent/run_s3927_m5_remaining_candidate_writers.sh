#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3927.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3926_m5_remaining_candidate_writers/s3927_m5_remaining_candidate_writers/g; s/0x80005000,0x80005004,0x80005008/0x8000500C,0x80005010,0x80005014/g; s/0x80005000\|0x80005004\|0x80005008/0x8000500c|0x80005010|0x80005014/g' "$ROOT/scratch/agent/run_s3926_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
