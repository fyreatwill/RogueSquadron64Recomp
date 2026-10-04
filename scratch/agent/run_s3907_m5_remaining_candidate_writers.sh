#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3907.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3906_m5_remaining_candidate_writers/s3907_m5_remaining_candidate_writers/g; s/0x80004F3C,0x80004F44,0x80004F48/0x80004F4C,0x80004F50,0x80004F54/g; s/0x80004f3c\|0x80004f44\|0x80004f48/0x80004f4c|0x80004f50|0x80004f54/g' "$ROOT/scratch/agent/run_s3906_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
