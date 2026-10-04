#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s4006.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s4005_m5_candidate_writers/s4006_m5_candidate_writers/g; s/0x80005288,0x8000528C,0x80005290/0x80005294,0x80005298,0x8000529C/g; s/0x80005288\\|0x8000528C\\|0x80005290/0x80005294|0x80005298|0x8000529C/g' "$ROOT/scratch/agent/run_s4005_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
