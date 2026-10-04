#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3890.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3889_m5_remaining_candidate_writers/s3890_m5_remaining_candidate_writers/g; s/0x80003A48,0x80003A50,0x80003AFC/0x80003B98,0x800044C8,0x80004AB0/g; s/0x80003a48\|0x80003a50\|0x80003afc/0x80003b98|0x800044c8|0x80004ab0/g' "$ROOT/scratch/agent/run_s3889_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
