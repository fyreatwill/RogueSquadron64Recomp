#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3999.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3998_m5_candidate_writers/s3999_m5_candidate_writers/g; s/0x80005240,0x80005244,0x80005248/0x8000524C,0x80005250,0x80005254/g; s/0x80005240\\|0x80005244\\|0x80005248/0x8000524C|0x80005250|0x80005254/g' "$ROOT/scratch/agent/run_s3998_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
