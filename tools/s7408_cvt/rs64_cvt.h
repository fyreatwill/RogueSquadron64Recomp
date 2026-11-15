/* s7408 class BR: live per-site FP->int conversion census (build_cvt only; tools/s7408_cvt_transform.py wraps every
 * CVT_W_S/CVT_W_D/TRUNC_W_S/TRUNC_W_D operand in a transformed copy of RecompiledFuncs). Per site: calls, max |x|,
 * out-of-int32 (VR4300 UNIMPL) count + first values, in-range host-vs-model mismatches (live comparator). */
#pragma once
#include <stdint.h>
struct rs64_cvsite { uint32_t pc; int kind; const char* fn; int idx; };
void rs64_cvt_note(struct rs64_cvsite* s, double x, int32_t host);
#define RS64_CVT(pcv, kindv, MAC, e) ({ __typeof__(e) _cx = (e); int32_t _ch = MAC(_cx); \
    static struct rs64_cvsite _cs = { pcv, kindv, __func__, -1 }; rs64_cvt_note(&_cs, (double)_cx, _ch); _ch; })
