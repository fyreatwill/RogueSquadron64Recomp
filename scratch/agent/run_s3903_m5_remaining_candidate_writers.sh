#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3903.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3902_m5_remaining_candidate_writers/s3903_m5_remaining_candidate_writers/g; s/0x80004D7C,0x80004D84,0x80004E74/0x80004E8C,0x80004E90,0x80004E94/g; s/0x80004d7c\|0x80004d84\|0x80004e74/0x80004e8c|0x80004e90|0x80004e94/g' "$ROOT/scratch/agent/run_s3902_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
