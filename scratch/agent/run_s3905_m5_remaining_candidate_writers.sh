#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3905.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3903_m5_remaining_candidate_writers/s3905_m5_remaining_candidate_writers/g; s/0x80004E8C,0x80004E90,0x80004E94/0x80004F30,0x80004F34,0x80004F38/g; s/0x80004e8c\|0x80004e90\|0x80004e94/0x80004f30|0x80004f34|0x80004f38/g' "$ROOT/scratch/agent/run_s3903_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
