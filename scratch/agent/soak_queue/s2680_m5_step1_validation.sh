#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT" || exit 2
exec zsh scratch/agent/run_s2618_hangar_pcm_boundary.sh
