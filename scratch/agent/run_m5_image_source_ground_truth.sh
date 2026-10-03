#!/bin/zsh
set -u
cd "$(dirname "$0")/../.." || exit 2
exec env ROGUESQ_M5_IMAGE_ONLY=1 zsh scratch/agent/run_m5_source_input_writer.sh
