#!/bin/zsh
# Runs the N64Recomp step of the regen pipeline (make_elf.py -> N64Recomp ->
# fixup_game_funcs.py -> cmake). N64Recomp must run with cwd set to its own
# checkout (rogue_squadron.toml and relative paths inside it are relative to
# that directory) -- see docs/CURRENT-TRUTH.md / scratch/agent/NEXT.md.
echo "DANGER (s5049): this regenerates the LIVE N64Recomp/RecompiledFuncs in place and its fixup step fails; it destroyed the live tree once. Use scratch dirs + tools/fixup_game_funcs_vendored.py." >&2
exit 99
set -e
cd /Users/williambuckley/Documents/Tools/N64Recomp
./build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
python3 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/apply_s3500_m5_selector_caller.py
python3 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/apply_s3501_m5_selector_precall.py
python3 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/apply_s3509_m5_selector_table.py
python3 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/apply_s3516_m5_selector_store_context.py
python3 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/apply_s4432_audioloop_witness.py
