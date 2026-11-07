// s6940 G1e: lean arm of the gfx ucode. The same fixed-up factor5_ucode_recompiled.c, compiled with the librecomp RSP hook
// gate (RS64_RSP_HOOKS_GATE) and the in-ucode probe gate (RS64_G1E_PROBES_ON) as constant 0, so every cold diagnostic path
// is deleted at compile time. With them present, their opaque calls (VU ring, vld_note, SDV snapshot, M4 probes taking &rsp)
// force the whole RSP vector register file to live in stack memory: offline, the function drops 47,789 -> 21,047
// instructions and q-register loads+stores per NEON op 0.55 -> 0.26 (tools/g1e_fn_mix.py).
// main.cpp runs this arm only while rs64_rsp_hooks_on == 0 and rs64_g1e_probes == 0, i.e. exactly when the gated code
// would not execute in the main TU either. ROGUESQ_G1E_LEAN=0 runs the main TU, ROGUESQ_G1E_LEAN_TOGGLE=<sec> flips them.
// CMakeLists gives this TU -DRS64_DMEM_BASE=dmem -DRSP=RS64_RSP_LEAN (own type: no template merging with the other TUs).
#define RS64_RSP_HOOKS_GATE 0
#define RS64_G1E_PROBES_ON 0
#define factor5_ucode factor5_ucode_lean
#include "../../build/factor5_ucode/factor5_ucode_recompiled.c"
