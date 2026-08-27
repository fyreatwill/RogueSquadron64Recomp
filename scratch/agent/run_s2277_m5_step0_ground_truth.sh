#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec zsh "$ROOT/scratch/agent/run_s2285_m5_step1_contract_pair.sh" "${1:-s2277_m5_step0_ground_truth}"
