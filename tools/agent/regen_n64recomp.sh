#!/bin/zsh
# Runs the N64Recomp step of the regen pipeline (make_elf.py -> N64Recomp ->
# fixup_game_funcs.py -> cmake). N64Recomp must run with cwd set to its own
# checkout (rogue_squadron.toml and relative paths inside it are relative to
# that directory) -- see docs/CURRENT-TRUTH.md / scratch/agent/NEXT.md.
set -e
cd /Users/williambuckley/Documents/Tools/N64Recomp
./build/N64Recomp rogue_squadron.toml
