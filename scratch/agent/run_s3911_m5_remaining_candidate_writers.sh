#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3911.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3909_m5_remaining_candidate_writers/s3911_m5_remaining_candidate_writers/g; s/0x80004F64,0x80004F68,0x80004F6C/0x80004F70,0x80004F74,0x80004F78/g; s/0x80004f64\|0x80004f68\|0x80004f6c/0x80004f70|0x80004f74|0x80004f78/g' "$ROOT/scratch/agent/run_s3909_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
