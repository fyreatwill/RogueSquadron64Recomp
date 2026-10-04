#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3913.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3912_m5_remaining_candidate_writers/s3913_m5_remaining_candidate_writers/g; s/0x80004F7C,0x80004F80,0x80004F84/0x80004F88,0x80004F8C,0x80004F90/g; s/0x80004f7c\|0x80004f80\|0x80004f84/0x80004f88|0x80004f8c|0x80004f90/g' "$ROOT/scratch/agent/run_s3912_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
