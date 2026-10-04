#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3998.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3997_m5_candidate_writers/s3998_m5_candidate_writers/g; s/0x80005234,0x80005238,0x8000523C/0x80005240,0x80005244,0x80005248/g; s/0x80005234\\|0x80005238\\|0x8000523C/0x80005240|0x80005244|0x80005248/g' "$ROOT/scratch/agent/run_s3997_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
