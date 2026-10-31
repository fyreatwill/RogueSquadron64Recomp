# NEXT: G1c dd4 frame cost - optimise the -O0 code (Debug build)
HYPOTHESIS-ID: g1c-dd4-gfx-task-cost

s6698: store-hook gate (g_rs64_store_diag) + cached RT64 getenv: lvl5 dd4 24.4 fps / 23.9 ms per task with hooks off
(18.4 / 38.0 on). Gfx thread is now the bottleneck (71% busy). The build is CMAKE_BUILD_TYPE=Debug: RT64 and the ucode
get -O2 (CMakeLists.txt:61, :292) but src/ (dpc_bridge.cpp rsp_dpc_submit: std::vector helpers as frames) and
RecompiledFuncs are -O0.
Hypotheses: H-src-O0 (Gfx-thread cost is our -O0 host code in src/rsp + main.cpp hooks: -O2 on those TUs cuts send_dl),
H-guest-O0 (RecompiledFuncs -O0 bounds the game thread once the Gfx thread is faster), H-ucode (the rest is genuine
LLE ucode cost already at -O2: nothing moves).
Arms, built in separate build dirs (cp -c build to build_o2src / build_o2all; one game at a time, sequential runs):
  A baseline build/, B src/ -O2 (set_source_files_properties on src/rsp/*.cpp + src/main/*.cpp COMPILE_OPTIONS -O2,
  option ROGUESQ_SRC_OPT default OFF), C B + RecompiledFuncs -O2 (option ROGUESQ_FUNCS_OPT; watch compile time and any
  behaviour change: 300 s hold, 0 crash, fb dump sane).
Recipe per arm (add ROGUESQ_STORE_DIAG=0):
env ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA="ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_STORE_DIAG=0 " HOLD_S=200 LEVEL=5 BUILD=$PWD/build_o2src TAG_SUFFIX=sNNNN_o2src zsh scratch/agent/g1_level_coverage_common.zsh
Fold: python3 tools/g3d_toggle_fold.py <run.log> --skip 60 (pre-toggle row). Profile with `sample <pid> 8` + tools/sample_self.py.
Owner: judge turning feel on the fixed build; send s6694/s6695 21:9 level-select frames.
