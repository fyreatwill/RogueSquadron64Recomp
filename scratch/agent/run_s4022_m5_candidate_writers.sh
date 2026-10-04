#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s4022-fixed.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s4011_m5_candidate_writers/s4022_m5_candidate_writers/g; s/0x80005294,0x80005298,0x8000529C/0x800052B8,0x800052BC,0x800052C0/g; s/0x80005294\\|0x80005298\\|0x8000529C/0x800052B8|0x800052BC|0x800052C0/g' "$ROOT/scratch/agent/run_s4011_m5_candidate_writers_qualified.sh" > "$TMP"
exec zsh "$TMP"
