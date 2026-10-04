#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3901.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3900_m5_remaining_candidate_writers/s3901_m5_remaining_candidate_writers/g; s/0x80004C90,0x80004D00,0x80004D60/0x80004D68,0x80004D74,0x80004D78/g; s/0x80004c90\|0x80004d00\|0x80004d60/0x80004d68|0x80004d74|0x80004d78/g' "$ROOT/scratch/agent/run_s3900_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
