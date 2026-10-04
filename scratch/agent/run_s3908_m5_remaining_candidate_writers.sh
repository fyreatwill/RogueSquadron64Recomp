#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3908.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3907_m5_remaining_candidate_writers/s3908_m5_remaining_candidate_writers/g; s/0x80004F4C,0x80004F50,0x80004F54/0x80004F58,0x80004F5C,0x80004F60/g; s/0x80004f4c\|0x80004f50\|0x80004f54/0x80004f58|0x80004f5c|0x80004f60/g' "$ROOT/scratch/agent/run_s3907_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
