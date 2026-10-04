#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s4000.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3999_m5_candidate_writers/s4000_m5_candidate_writers/g; s/0x8000524C,0x80005250,0x80005254/0x80005258,0x8000525C,0x80005260/g; s/0x8000524C\\|0x80005250\\|0x80005254/0x80005258|0x8000525C|0x80005260/g' "$ROOT/scratch/agent/run_s3999_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
