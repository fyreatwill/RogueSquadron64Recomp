#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3892.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3888_m5_remaining_candidate_writers/s3892_m5_remaining_candidate_writers/g; s/0x8006EFAC,0x80006C2C,0x80006C34/0x80004AB8,0x80004AC0,0x80004AC8/g; s/0x8006efac\|0x80006c2c\|0x80006c34/0x80004ab8|0x80004ac0|0x80004ac8/g' "$ROOT/scratch/agent/run_s3888_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
