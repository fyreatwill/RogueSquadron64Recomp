#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
TMP=$(mktemp /tmp/rs64-s3931.XXXXXX)
trap 'rm -f "$TMP"' EXIT INT TERM
perl -pe 's/s3927_m5_remaining_candidate_writers/s3931_m5_remaining_candidate_writers/g; s/0x8000500C,0x80005010,0x80005014/0x80005018,0x8000501C,0x80005020/g; s/0x8000500c\|0x80005010\|0x80005014/0x80005018|0x8000501c|0x80005020/g' "$ROOT/scratch/agent/run_s3927_m5_remaining_candidate_writers.sh" > "$TMP"
exec zsh "$TMP"
