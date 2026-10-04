#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3924.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3923_m5_remaining_candidate_writers/s3924_m5_remaining_candidate_writers/g; s/0x80004FDC,0x80004FE0,0x80004FE4/0x80004FE8,0x80004FEC,0x80004FF0/g; s/0x80004fdc\|0x80004fe0\|0x80004fe4/0x80004fe8|0x80004fec|0x80004ff0/g' "$ROOT/scratch/agent/run_s3923_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
