/* s7406 class BP: per-guest-PC FPSR attribution (build_fpat only; tools/s7406_fpat_transform.py includes this in a
 * transformed copy of RecompiledFuncs). Every guest FP statement is wrapped as { snapshot 2 source regs; stmt; check }
 * and every call line as { call; check }. The check reads the arm64 sticky FPSR and, if IOC/DZC/OFC/UFC/IDC is set,
 * reports (site pc, function, kind, operands) and clears FPSR. Statement hits = guest float code produced the flag;
 * call hits = the callee's host code (shim / runtime) produced it after its last instrumented statement. */
#pragma once
#include <stdint.h>
struct rs64_fpsite { uint32_t pc; int line; const char* fn; const char* what; int idx; };
void rs64_fpat_hit(struct rs64_fpsite* s, uint64_t f, uint64_t a, uint64_t b);
void rs64_fpat_plant(void);
#define RS64_FPSR_MASK 0x8Full /* IOC DZC OFC UFC IDC (IXC excluded: ~80% of blocks) */
#define RS64_FPCHK(pcv, whatv, a, b) do { uint64_t _f; __asm__ volatile("mrs %0, fpsr" : "=r"(_f) :: "memory"); \
    if (__builtin_expect((_f & RS64_FPSR_MASK) != 0, 0)) { static struct rs64_fpsite _s = { pcv, __LINE__, __func__, whatv, -1 }; \
    rs64_fpat_hit(&_s, _f, a, b); } } while (0)
