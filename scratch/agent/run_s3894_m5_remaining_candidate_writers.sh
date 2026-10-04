#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3893_m5_remaining_candidate_writers/s3894_m5_remaining_candidate_writers/g; s/0x80004AD4,0x80004AE0,0x80004AE4/0x80004AE8,0x80004AF0,0x80004BE8/g; s/0x80004ad4\|0x80004ae0\|0x80004ae4/0x80004ae8|0x80004af0|0x80004be8/g' \
  "$ROOT/scratch/agent/run_s3893_m5_remaining_candidate_writers.sh" > "$TMP"
zsh "$TMP"
