#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s4004.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s4003_m5_candidate_writers/s4004_m5_candidate_writers/g; s/0x80005270,0x80005274,0x80005278/0x8000527C,0x80005280,0x80005284/g; s/0x80005270\\|0x80005274\\|0x80005278/0x8000527C|0x80005280|0x80005284/g' "$ROOT/scratch/agent/run_s4003_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
