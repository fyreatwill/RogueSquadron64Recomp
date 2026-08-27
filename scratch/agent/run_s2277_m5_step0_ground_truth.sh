#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec zsh "$ROOT/scratch/agent/run_s2288_m5_audio_default_step2.sh" "${1:-s2277_m5_step0_ground_truth}"
