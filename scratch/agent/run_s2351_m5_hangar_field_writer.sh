#!/bin/zsh
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2351_m5_hangar_field_writer}
export RS64_ORACLE="$ROOT/scratch/agent/s2351_m5_hangar_field_writer_oracle_fixed.log"
exec zsh "$ROOT/scratch/agent/run_s2350_m5_hangar_writer.sh" "$TAG"
