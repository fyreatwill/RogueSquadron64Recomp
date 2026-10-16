#!/usr/bin/env python3
"""s5049 DISABLED. The original version ran tools/agent/regen_n64recomp.sh against the LIVE
N64Recomp/RecompiledFuncs tree and destroyed it (53/55 files rewritten; the N64Recomp-local
fixup_game_funcs.py then died at 's4339 C88C descriptor anchor count=0', leaving a half-patched tree).
The live tree is a hand-patched artifact that no pipeline reproduces byte-for-byte (s4970 diff: 275k lines).
Never regenerate in place; use scratch dirs + tools/fixup_game_funcs_vendored.py (see scratch/agent/s4814_regen.sh)."""
import sys
sys.exit("s5049_regen_diff.py is disabled: it clobbers the live RecompiledFuncs tree")
