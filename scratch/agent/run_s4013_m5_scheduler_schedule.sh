#!/bin/zsh
set -u
ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
export ROGUESQ_SPIN_YIELD=0
export RS64_BOUNDARY_OUT=$ROOT/scratch/agent/s4013_m5_scheduler_schedule
exec zsh "$ROOT/scratch/agent/run_s4012_m5_scheduler_boundary.sh"
