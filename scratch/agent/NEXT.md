# NEXT: G1c - qualify the -O2 build (ROGUESQ_SRC_OPT + ROGUESQ_FUNCS_OPT), then default decision
HYPOTHESIS-ID: g1c-o2-build-qualify

s6699: -O2 host+guest code takes lvl5 dd4 from ~22 to 30.5 game fps (retail cap), 203 s clean, fb sane. Options are OFF by
default; build/ is configured OFF. The -O2 binary lives in build_s6699_o2/ (symlinked ROM/saves/mods).
1. Fold SOAK-RESULTS lines for s6699_o2_lvl1_dd1 / s6699_o2_lvl10_dd4 (summary + fold line in their logs).
2. Run on build_s6699_o2: the hangar route (s5378/m6 hangar recipe) and lvl7 dd1 300 s, plus a retail-settings lvl1
   framebuffer compare vs -O0 at the same game frame index (phase-gated) to catch render deltas.
   env ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA="ROGUESQ_STORE_DIAG=0 " HOLD_S=300 LEVEL=7 BUILD=$PWD/build_s6699_o2 TAG_SUFFIX=s6700_o2 zsh scratch/agent/g1_level_coverage_common.zsh
Outcomes: all clean -> set both options default ON in CMakeLists.txt (build flags, not game behaviour), rebuild build/,
note in OWNER-OPT-INS/CURRENT-TRUTH. A crash only on -O2 -> lldb backtrace on build_s6699_o2, find the UB in the recompiled
function (likely signed overflow / uninit) and fix in N64Recomp output via fixup or -fwrapv; try -fwrapv first if arithmetic.
If any binary under build/ is rebuilt, refresh build_s6699_o2 with: cmake -DROGUESQ_SRC_OPT=ON -DROGUESQ_FUNCS_OPT=ON, build,
copy, then reconfigure OFF (or once qualified, just flip the default).
