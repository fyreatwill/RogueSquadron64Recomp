/* s7389 framebuffer-load watch (build_fbld only: cmake -DROGUESQ_FB_LDWATCH=ON puts this dir BEFORE the upstream
 * include path for RecompiledFuncs). Wraps every MEM_W/H/HU/B/BU guest access: when the physical page was named by
 * an RDP SetColorImage / SetZImage (marked by src/rsp/s7389_fbld.cpp from the gfx RDP stream) the access is reported
 * with __FILE__/__LINE__ (one generated line = one MIPS instruction, so the line itself says load vs store).
 * Not covered: load_doubleword / do_lwl / do_lwr (inline helpers above, bound to the upstream macros). Diagnostic. */
#include_next "recomp.h"
#ifdef RS64_FB_LDWATCH
#ifndef RS64_FBLD_OVERRIDE
#define RS64_FBLD_OVERRIDE
extern uint32_t rs64_fbpg[4096];
void rs64_fbld_hit(uint32_t phys, const char *file, int line, int width);
static inline uint8_t *rs64_fbld_chk(uint8_t *rdram, uint8_t *p, const char *f, int l, int w) {
    uint32_t a = (uint32_t)(p - rdram) & 0x1FFFFFFFu;
    if (a < 0x1000000u && rs64_fbpg[a >> 12]) rs64_fbld_hit(a, f, l, w);
    return p;
}
#undef MEM_W
#undef MEM_H
#undef MEM_HU
#undef MEM_B
#undef MEM_BU
#undef MEM_WU
#define MEM_WU(offset, reg) \
    (*(uint32_t*)rs64_fbld_chk(rdram, rdram + ((((reg) + (offset))) - 0xFFFFFFFF80000000), __FILE__, __LINE__, 4))
#define MEM_W(offset, reg) \
    (*(int32_t*)rs64_fbld_chk(rdram, rdram + ((((reg) + (offset))) - 0xFFFFFFFF80000000), __FILE__, __LINE__, 4))
#define MEM_H(offset, reg) \
    (*(int16_t*)rs64_fbld_chk(rdram, rdram + ((((reg) + (offset)) ^ 2) - 0xFFFFFFFF80000000), __FILE__, __LINE__, 2))
#define MEM_HU(offset, reg) \
    (*(uint16_t*)rs64_fbld_chk(rdram, rdram + ((((reg) + (offset)) ^ 2) - 0xFFFFFFFF80000000), __FILE__, __LINE__, 2))
#define MEM_B(offset, reg) \
    (*(int8_t*)rs64_fbld_chk(rdram, rdram + ((((reg) + (offset)) ^ 3) - 0xFFFFFFFF80000000), __FILE__, __LINE__, 1))
#define MEM_BU(offset, reg) \
    (*(uint8_t*)rs64_fbld_chk(rdram, rdram + ((((reg) + (offset)) ^ 3) - 0xFFFFFFFF80000000), __FILE__, __LINE__, 1))
#endif
#endif
