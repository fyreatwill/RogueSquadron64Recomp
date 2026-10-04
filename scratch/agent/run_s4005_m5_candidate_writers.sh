#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s4005.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s4004_m5_candidate_writers/s4005_m5_candidate_writers/g; s/0x8000527C,0x80005280,0x80005284/0x80005288,0x8000528C,0x80005290/g; s/0x8000527C\\|0x80005280\\|0x80005284/0x80005288|0x8000528C|0x80005290/g' "$ROOT/scratch/agent/run_s4004_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
