/* s7409 class BS: live FR-mode / odd-FPR view probe (build_fodd only; tools/s7409_fodd_transform.py). */
#pragma once
#include <stdint.h>
struct rs64_frsite { const char* fn; const char* where; int expect; int idx; };
void rs64_frp_note(struct rs64_frsite* s, void* ctx);
#define RS64_FRP(wherev, expv) do { static struct rs64_frsite _fs = { __func__, wherev, expv, -1 }; rs64_frp_note(&_fs, ctx); } while (0)
