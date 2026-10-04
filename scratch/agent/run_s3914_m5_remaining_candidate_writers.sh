#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3914.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3913_m5_remaining_candidate_writers/s3914_m5_remaining_candidate_writers/g; s/0x80004F88,0x80004F8C,0x80004F90/0x80004F94,0x80004F98,0x80004F9C/g; s/0x80004f88\|0x80004f8c\|0x80004f90/0x80004f94|0x80004f98|0x80004f9c/g' "$ROOT/scratch/agent/run_s3913_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
