/* s7410 class BT: live callee-saved preservation probe (build_fsv only; tools/s7410_fsv_transform.py). */
#pragma once
#include <stdint.h>
struct rs64_fsvsite { const char* fn; int idx; };
struct rs64_fsvsnap { uint64_t f[12]; uint32_t odd[6]; uint64_t r[11]; int mode; };
void rs64_fsv_enter(struct rs64_fsvsnap* s, void* ctx);
void rs64_fsv_ret(struct rs64_fsvsite* site, struct rs64_fsvsnap* s, void* ctx);
#define RS64_FSV_ENTER() static struct rs64_fsvsite _fsvs = { __func__, -1 }; struct rs64_fsvsnap _fsvn; rs64_fsv_enter(&_fsvn, ctx);
#define RS64_FSV_RET() rs64_fsv_ret(&_fsvs, &_fsvn, ctx)
