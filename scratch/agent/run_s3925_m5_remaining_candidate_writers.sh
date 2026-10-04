#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3925.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3924_m5_remaining_candidate_writers/s3925_m5_remaining_candidate_writers/g; s/0x80004FE8,0x80004FEC,0x80004FF0/0x80004FF4,0x80004FF8,0x80004FFC/g; s/0x80004fe8\|0x80004fec\|0x80004ff0/0x80004ff4|0x80004ff8|0x80004ffc/g' "$ROOT/scratch/agent/run_s3924_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
