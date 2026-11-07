// s6941 G1e: the lean gfx ucode arm (src/rsp/factor5_ucode_lean.cpp) with the native NEON multiply-op bodies
// (RS64_RSP_NEON_MAC=1 in librecomp rsp_vu_impl.hpp: VMUDN/VMUDM/VMUDH, VMADL/VMADN/VMADM/VMADH). Those ops were 45% of
// the lean ucode's host time (s6941 xctrace) and ran the SSE algorithm through sse2neon (3 ops per carry, 8 per clamp).
// Bit-exact against the SSE bodies: tools/g1e_nmac_equiv.zsh (43.2M cases, 0 mismatches; MUTANT=1 fails).
// main.cpp picks it over the lean arm iff ROGUESQ_G1E_NMAC (see there); ROGUESQ_G1E_NMAC_TOGGLE=<sec> flips them.
#define RS64_RSP_HOOKS_GATE 0
#define RS64_G1E_PROBES_ON 0
#define RS64_RSP_NEON_MAC 1
#define factor5_ucode factor5_ucode_nmac
#include "../../build/factor5_ucode/factor5_ucode_recompiled.c"
