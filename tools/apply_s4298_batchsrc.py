#!/usr/bin/env python3
"""s4298: extend the submitDmaRequestBatch [dma-ring-producer] row with the source array (s0), the entry index (t0)
and 12 words of the source array (marker s4298-batch), plus a host backtrace of the first 3 rows (marker s4298b), so a
text-valued devAddr can be traced to its source struct and guest caller. Diagnostic only; needs
ROGUESQ_LOG_DMA_RING=1. Two independent idempotent steps."""
from pathlib import Path
p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_1.c")
s = p.read_text()
a = '''            s_dma_ring_prod_n++;
        }
    }
    ctx->r2 = S32(SIGNED(ctx->r5) >> 8);
    // 0x8000576C'''
assert s.count(a) == 1
COND = "MEM_W(ctx->r3, 0X4) != 0 && ((uint32_t)MEM_W(ctx->r3, 0X4) >> 24) != 0xB0u"
if "s4298-batch]" not in s:
    b = '''            if (''' + COND + ''') fprintf(stderr, "[s4298-batch] n=%d arr=0x%08X ent_idx=%d cnt=%d ra=0x%08X src12=%08X %08X %08X %08X %08X %08X %08X %08X %08X %08X %08X %08X\\n",
                    s_dma_ring_prod_n, (uint32_t)ctx->r16, (int)ctx->r8, (int)ctx->r17, (uint32_t)MEM_W(0X34, ctx->r29),
                    (uint32_t)MEM_W(0, ctx->r16), (uint32_t)MEM_W(4, ctx->r16), (uint32_t)MEM_W(8, ctx->r16), (uint32_t)MEM_W(12, ctx->r16), (uint32_t)MEM_W(16, ctx->r16), (uint32_t)MEM_W(20, ctx->r16),
                    (uint32_t)MEM_W(24, ctx->r16), (uint32_t)MEM_W(28, ctx->r16), (uint32_t)MEM_W(32, ctx->r16), (uint32_t)MEM_W(36, ctx->r16), (uint32_t)MEM_W(40, ctx->r16), (uint32_t)MEM_W(44, ctx->r16));
'''
    s = s.replace(a, b + a, 1)
if "s4298b" not in s:
    b = '''            if (''' + COND + ''') { /* s4298b: host backtrace names the guest caller (recomp keeps no ra) */
                extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int);
                static int bt_rows = 0;
                if (bt_rows++ < 3) { void* bt[12]; int bn = backtrace(bt, 12); fprintf(stderr, "[s4298-batch-bt] n=%d\\n", s_dma_ring_prod_n); backtrace_symbols_fd(bt, bn, 2); }
            }
'''
    s = s.replace(a, b + a, 1)
if "s4298c" not in s:
    b = '''            { /* s4298c: where does the text-valued devAddr live in RDRAM? (first 4 text rows) */
                uint32_t dv = (uint32_t)MEM_W(ctx->r3, 0X4); static int sc_rows = 0;
                if ((dv >> 24) >= 0x20u && (dv >> 24) < 0x7Fu && sc_rows < 4) {
                    sc_rows++; int hits = 0;
                    for (uint32_t ra_ = 0; ra_ + 4 <= 0x800000u && hits < 6; ra_ += 4) {
                        if (*(uint32_t*)(rdram + ra_) == dv) {
                            hits++;
                            fprintf(stderr, "[s4298c] devAddr=0x%08X at rdram 0x%06X words:", dv, ra_);
                            for (int k = -8; k < 8; k++) { uint32_t q = ra_ + k * 4; if (q + 4 <= 0x800000u) fprintf(stderr, " %08X", *(uint32_t*)(rdram + q)); }
                            fprintf(stderr, "\\n");
                        }
                    }
                    fprintf(stderr, "[s4298c] devAddr=0x%08X hits=%d\\n", dv, hits);
                }
            }
'''
    s = s.replace(a, b + a, 1)
p.write_text(s)
print("ok")
