#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3909.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3908_m5_remaining_candidate_writers/s3909_m5_remaining_candidate_writers/g; s/0x80004F58,0x80004F5C,0x80004F60/0x80004F64,0x80004F68,0x80004F6C/g; s/0x80004f58\|0x80004f5c\|0x80004f60/0x80004f64|0x80004f68|0x80004f6c/g' "$ROOT/scratch/agent/run_s3908_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
