#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s4037-fixed.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s4011_m5_candidate_writers/s4037_m5_candidate_writers/g; s/0x80005294,0x80005298,0x8000529C/0x800052C4,0x800052C8,0x800052CC/g; s/0x80005294\\|0x80005298\\|0x8000529C/0x800052C4|0x800052C8|0x800052CC/g' "$ROOT/scratch/agent/run_s4011_m5_candidate_writers_qualified.sh" > "$TMP"
exec zsh "$TMP"
