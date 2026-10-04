#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3895_m5_remaining_candidate_writers/s3896_m5_remaining_candidate_writers/g; s/0x80004C74,0x80004C88,0x80004C8C/0x80004C90,0x80004D00,0x80004D60/g; s/0x80004c74\|0x80004c88\|0x80004c8c/0x80004c90|0x80004d00|0x80004d60/g' \
  "$ROOT/scratch/agent/run_s3895_m5_remaining_candidate_writers.sh" > "$TMP"
zsh "$TMP"
