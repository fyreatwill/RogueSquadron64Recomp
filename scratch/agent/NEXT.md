# Next work unit
HYPOTHESIS-ID: movz-movn-recompiler-support
Implement MIPS movz/movn in N64Recomp (/Users/williambuckley/Documents/Tools/N64Recomp/src: find where SPECIAL ops map to emitted C and why they fall through to do_break; rabbitizer already decodes cpu_movz/cpu_movn). Semantics: movz rd,rs,rt => if (rt==0) rd=rs; movn => if (rt!=0) rd=rs (64-bit compare on rt).
Plan: (1) read the emit path, add both ops; (2) regen into a SCRATCH dir, never over live RecompiledFuncs, in order make_elf.py -> N64Recomp -> fixup_game_funcs.py; (3) run tools/census_movz_movn.py on the scratch output: expect 0 do_break bodies for movz/movn; positive control = the pre-change census still shows its current count; (4) diff scratch vs live: only movz/movn sites may differ; (5) only then swap in, cmake build, and run one title+hangar smoke (crash=0).
Any edit under lib/ needs submodule-patches/export.sh + commit. Generated-code fixes go through tools/fixup_*.py.
Rollback: keep the pre-change RecompiledFuncs backup; revert if smoke regresses.
