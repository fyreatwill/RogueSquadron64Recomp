// s6775 G1e: same-run A/B arm for the constant DMEM base. This compiles the fixed-up gfx ucode a second time with the default
// RS64_DMEM_BASE (the thread-local g_dmem_cur) and the stock RSP type, renamed factor5_ucode_tls. The primary factor5_ucode TU
// gets -DRS64_DMEM_BASE=dmem -DRSP=RS64_RSP_GFX (CMakeLists). main.cpp picks one per gfx task: ROGUESQ_G1E_DMEMBASE=0 runs
// this arm, ROGUESQ_G1E_DMEMBASE_TOGGLE=<sec> flips between them ([g1e-dmembase] lines).
#define factor5_ucode factor5_ucode_tls
#include "../../build/factor5_ucode/factor5_ucode_recompiled.c"
