#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s4001.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s4000_m5_candidate_writers/s4001_m5_candidate_writers/g; s/0x80005258,0x8000525C,0x80005260/0x80005264,0x80005268,0x8000526C/g; s/0x80005258\\|0x8000525C\\|0x80005260/0x80005264|0x80005268|0x8000526C/g' "$ROOT/scratch/agent/run_s4000_m5_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
