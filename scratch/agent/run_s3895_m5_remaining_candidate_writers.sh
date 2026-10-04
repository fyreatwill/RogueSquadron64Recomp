#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3894_m5_remaining_candidate_writers/s3895_m5_remaining_candidate_writers/g; s/0x80004AE8,0x80004AF0,0x80004BE8/0x80004C74,0x80004C88,0x80004C8C/g; s/0x80004ae8\|0x80004af0\|0x80004be8/0x80004c74|0x80004c88|0x80004c8c/g' \
  "$ROOT/scratch/agent/run_s3894_m5_remaining_candidate_writers.sh" > "$TMP"
zsh "$TMP"
