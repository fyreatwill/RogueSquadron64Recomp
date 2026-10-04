#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
source_script="$ROOT/scratch/agent/run_s3937_m5_candidate_writers.sh"
run_script="$(mktemp /tmp/rs64-s3938-XXXXXX.sh)"
trap 'rm -f "$run_script"' EXIT
sed -e 's/s3937_m5_candidate_writers/s3938_m5_candidate_writers/g' \
    -e 's/0x80005054,0x80005058,0x8000505C/0x80005060,0x80005064,0x80005068/g' \
    -e 's/0x80005054|0x80005058|0x8000505c/0x80005060|0x80005064|0x80005068/g' \
    "$source_script" > "$run_script"
zsh "$run_script"
