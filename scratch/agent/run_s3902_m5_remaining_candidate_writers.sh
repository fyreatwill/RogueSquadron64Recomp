#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3902.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3901_m5_remaining_candidate_writers/s3902_m5_remaining_candidate_writers/g; s/0x80004D68,0x80004D74,0x80004D78/0x80004D7C,0x80004D84,0x80004E74/g; s/0x80004d68\|0x80004d74\|0x80004d78/0x80004d7c|0x80004d84|0x80004e74/g' "$ROOT/scratch/agent/run_s3901_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
