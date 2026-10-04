#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3975.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3974_m5_candidate_writers/s3975_m5_candidate_writers/g; s/0x80005198,0x8000519C,0x800051A0/0x800051A4,0x800051A8,0x800051AC/g; s/0x80005198\|0x8000519C\|0x800051A0/0x800051A4|0x800051A8|0x800051AC/g' "$ROOT/scratch/agent/run_s3974_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
