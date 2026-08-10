#!/usr/bin/env python3
"""Re-apply s639 freelist zero-node writer instruments (idempotent)."""
from pathlib import Path
import os, sys

FUNCS = Path(os.environ.get(
    "RECOMP_FUNCS",
    str(Path.home() / "Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c"),
))

FL_HDR_FREE = '    { // PATCH: fl-hdr-write free (s639, item -391) -- see fixup_game_funcs.py comment\n        static int s_fl_hdr_en = -1;\n        if (s_fl_hdr_en < 0) { const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH"); s_fl_hdr_en = (e && e[0] && e[0] != \'0\') ? 1 : 0; }\n        if (s_fl_hdr_en) {\n            uint32_t fl_addr = U32(ctx->r4);\n            uint16_t fl_f = (uint16_t)U32(ctx->r9);\n            uint32_t fl_sz = U32(MEM_W(0X4, ctx->r4));\n            static int s_fl_hdr_n = 0;\n            int fl_bad = (fl_f == 0 || fl_sz == 0);\n            if (fl_bad || s_fl_hdr_n < 20 || (s_fl_hdr_n % 200) == 0) {\n                fprintf(stderr, "[fl-hdr-write] n=%d site=free flags=0x%X size=0x%X addr=0x%08X ra=0x%08X\\n",\n                    s_fl_hdr_n, (unsigned)fl_f, fl_sz, fl_addr, U32(ctx->r31));\n                fflush(stderr);\n            }\n            s_fl_hdr_n++;\n        }\n    }\n'

FL_HDR_SPLIT = '    { // PATCH: fl-hdr-write split residual (s639, item -391) -- see fixup_game_funcs.py comment\n        static int s_fl_spl_en = -1;\n        if (s_fl_spl_en < 0) { const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH"); s_fl_spl_en = (e && e[0] && e[0] != \'0\') ? 1 : 0; }\n        if (s_fl_spl_en) {\n            uint32_t fl_addr = U32(ctx->r4);\n            uint16_t fl_f = (uint16_t)MEM_HU(0X0, ctx->r4);\n            uint32_t fl_sz = U32(ctx->r2); /* just written residual size */\n            static int s_fl_spl_n = 0;\n            int fl_bad = (fl_f == 0 || fl_sz == 0);\n            if (fl_bad || s_fl_spl_n < 20 || (s_fl_spl_n % 200) == 0) {\n                fprintf(stderr, "[fl-hdr-write] n=%d site=split_res flags=0x%X size=0x%X addr=0x%08X ra=0x%08X\\n",\n                    s_fl_spl_n, (unsigned)fl_f, fl_sz, fl_addr, U32(ctx->r31));\n                fflush(stderr);\n            }\n            s_fl_spl_n++;\n        }\n    }\n'

FL_ZERO_FREE = '    { // PATCH: fl-zero-watch E8 scan site=free (s639, item -391) -- see fixup_game_funcs.py comment\n        static int s_flz_en = -1;\n        if (s_flz_en < 0) { const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH"); s_flz_en = (e && e[0] && e[0] != \'0\') ? 1 : 0; }\n        if (s_flz_en) {\n            static int s_flz_ctrl = 0;\n            static int s_flz_hit = 0;\n            gpr flz_base = S32(0x8011 << 16);\n            uint32_t flz_head = U32(MEM_W(flz_base, -0xE8));\n            if (flz_head >= 0x80000000u && flz_head < 0x80800000u) {\n                uint32_t flz_node = flz_head;\n                uint32_t flz_maxf = 0;\n                int flz_nfree = 0, flz_nnodes = 0;\n                int flz_found = 0;\n                uint32_t flz_bad = 0, flz_prev = 0, flz_prev_sz = 0;\n                uint16_t flz_prev_f = 0, flz_bad_f = 0;\n                for (int flz_i = 0; flz_i < 256; flz_i++) {\n                    if (flz_node < 0x80000000u || flz_node >= 0x80800000u) break;\n                    gpr flz_n = S32(flz_node);\n                    uint16_t flz_f = (uint16_t)MEM_HU(0x0, flz_n);\n                    if (flz_f & 0x8u) break;\n                    uint32_t flz_sz = U32(MEM_W(0x4, flz_n));\n                    flz_nnodes++;\n                    if ((flz_f & 0x1u) && flz_sz > 0u && flz_sz <= 0x800000u) {\n                        flz_nfree++;\n                        if (flz_sz > flz_maxf) flz_maxf = flz_sz;\n                    }\n                    /* s638 signature: !term, size==0 (flags often 0) */\n                    if (flz_sz == 0u) {\n                        flz_found = 1;\n                        flz_bad = flz_node;\n                        flz_bad_f = flz_f;\n                        break;\n                    }\n                    uint32_t flz_next = flz_node + flz_sz + 0x10u;\n                    if (flz_next <= flz_node) break;\n                    flz_prev = flz_node;\n                    flz_prev_sz = flz_sz;\n                    flz_prev_f = flz_f;\n                    flz_node = flz_next;\n                }\n                if (s_flz_ctrl < 3 && flz_maxf >= 0x1000u) {\n                    fprintf(stderr,\n                        "[fl-zero-watch] event=control n=%d site=free maxfree=0x%X nnodes=%d nfree=%d head=0x%08X\\n",\n                        s_flz_ctrl, flz_maxf, flz_nnodes, flz_nfree, flz_head);\n                    fflush(stderr);\n                    s_flz_ctrl++;\n                }\n                if (flz_found && s_flz_hit < 8) {\n                    fprintf(stderr,\n                        "[fl-zero-watch] event=zero_node n=%d site=free bad=0x%08X bad_f=0x%X "\n                        "prev=0x%08X prev_f=0x%X prev_sz=0x%X ra=0x%08X maxfree=0x%X nnodes=%d\\n",\n                        s_flz_hit, flz_bad, (unsigned)flz_bad_f,\n                        flz_prev, (unsigned)flz_prev_f, flz_prev_sz, U32(ctx->r31),\n                        flz_maxf, flz_nnodes);\n                    fflush(stderr);\n                    s_flz_hit++;\n                }\n            }\n        }\n    }\n'

FL_ZERO_MALLOC = '    { // PATCH: fl-zero-watch E8 scan site=malloc (s639, item -391) -- see fixup_game_funcs.py comment\n        static int s_flz_en = -1;\n        if (s_flz_en < 0) { const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH"); s_flz_en = (e && e[0] && e[0] != \'0\') ? 1 : 0; }\n        if (s_flz_en) {\n            static int s_flz_ctrl = 0;\n            static int s_flz_hit = 0;\n            gpr flz_base = S32(0x8011 << 16);\n            uint32_t flz_head = U32(MEM_W(flz_base, -0xE8));\n            if (flz_head >= 0x80000000u && flz_head < 0x80800000u) {\n                uint32_t flz_node = flz_head;\n                uint32_t flz_maxf = 0;\n                int flz_nfree = 0, flz_nnodes = 0;\n                int flz_found = 0;\n                uint32_t flz_bad = 0, flz_prev = 0, flz_prev_sz = 0;\n                uint16_t flz_prev_f = 0, flz_bad_f = 0;\n                for (int flz_i = 0; flz_i < 256; flz_i++) {\n                    if (flz_node < 0x80000000u || flz_node >= 0x80800000u) break;\n                    gpr flz_n = S32(flz_node);\n                    uint16_t flz_f = (uint16_t)MEM_HU(0x0, flz_n);\n                    if (flz_f & 0x8u) break;\n                    uint32_t flz_sz = U32(MEM_W(0x4, flz_n));\n                    flz_nnodes++;\n                    if ((flz_f & 0x1u) && flz_sz > 0u && flz_sz <= 0x800000u) {\n                        flz_nfree++;\n                        if (flz_sz > flz_maxf) flz_maxf = flz_sz;\n                    }\n                    /* s638 signature: !term, size==0 (flags often 0) */\n                    if (flz_sz == 0u) {\n                        flz_found = 1;\n                        flz_bad = flz_node;\n                        flz_bad_f = flz_f;\n                        break;\n                    }\n                    uint32_t flz_next = flz_node + flz_sz + 0x10u;\n                    if (flz_next <= flz_node) break;\n                    flz_prev = flz_node;\n                    flz_prev_sz = flz_sz;\n                    flz_prev_f = flz_f;\n                    flz_node = flz_next;\n                }\n                if (s_flz_ctrl < 3 && flz_maxf >= 0x1000u) {\n                    fprintf(stderr,\n                        "[fl-zero-watch] event=control n=%d site=malloc maxfree=0x%X nnodes=%d nfree=%d head=0x%08X\\n",\n                        s_flz_ctrl, flz_maxf, flz_nnodes, flz_nfree, flz_head);\n                    fflush(stderr);\n                    s_flz_ctrl++;\n                }\n                if (flz_found && s_flz_hit < 8) {\n                    fprintf(stderr,\n                        "[fl-zero-watch] event=zero_node n=%d site=malloc bad=0x%08X bad_f=0x%X "\n                        "prev=0x%08X prev_f=0x%X prev_sz=0x%X ra=0x%08X maxfree=0x%X nnodes=%d\\n",\n                        s_flz_hit, flz_bad, (unsigned)flz_bad_f,\n                        flz_prev, (unsigned)flz_prev_f, flz_prev_sz, U32(ctx->r31),\n                        flz_maxf, flz_nnodes);\n                    fflush(stderr);\n                    s_flz_hit++;\n                }\n            }\n        }\n    }\n'

def main():
    text = FUNCS.read_text()
    report = []
    changed = False

    if "fl-hdr-write free (s639" not in text:
        free_start = text.find("RECOMP_FUNC void rs_free(uint8_t* rdram, recomp_context* ctx) {")
        free_end = text.find("RECOMP_FUNC void buildHeapFreeList", free_start)
        body = text[free_start:free_end]
        needle = "    MEM_H(0X0, ctx->r4) = ctx->r9;\n"
        if body.count(needle) != 2:
            print("ERROR free flag count=%d" % body.count(needle), file=sys.stderr)
            return 1
        body2 = body.replace(needle, needle + FL_HDR_FREE)
        text = text[:free_start] + body2 + text[free_end:]
        changed = True
        report.append("fl-hdr-write free x2")
    else:
        report.append("fl-hdr-write free already present")

    if "fl-hdr-write split residual (s639" not in text:
        split_anchor = (
            "    // 0x80001C48: sw          $v0, 0x4($a0)\n"
            "    MEM_W(0X4, ctx->r4) = ctx->r2;\n"
        )
        if text.count(split_anchor) != 1:
            print("ERROR split count=%d" % text.count(split_anchor), file=sys.stderr)
            return 1
        text = text.replace(split_anchor, split_anchor + FL_HDR_SPLIT, 1)
        changed = True
        report.append("fl-hdr-write split x1")
    else:
        report.append("fl-hdr-write split already present")

    if "fl-zero-watch E8 scan site=free" not in text:
        free_start = text.find("RECOMP_FUNC void rs_free(uint8_t* rdram, recomp_context* ctx) {")
        free_end = text.find("RECOMP_FUNC void buildHeapFreeList", free_start)
        body = text[free_start:free_end]
        idx = body.rfind("    return;\n")
        if idx < 0:
            print("ERROR free return", file=sys.stderr)
            return 1
        body2 = body[:idx] + FL_ZERO_FREE + body[idx:]
        text = text[:free_start] + body2 + text[free_end:]
        changed = True
        report.append("fl-zero-watch free")
    else:
        report.append("fl-zero-watch free already present")

    if "fl-zero-watch E8 scan site=malloc" not in text:
        malloc_start = text.find("RECOMP_FUNC void rs_malloc(uint8_t* rdram, recomp_context* ctx) {")
        malloc_end = text.find("RECOMP_FUNC void rs_free", malloc_start)
        body = text[malloc_start:malloc_end]
        idx = body.rfind("    return;\n")
        if idx < 0:
            print("ERROR malloc return", file=sys.stderr)
            return 1
        body2 = body[:idx] + FL_ZERO_MALLOC + body[idx:]
        text = text[:malloc_start] + body2 + text[malloc_end:]
        changed = True
        report.append("fl-zero-watch malloc")
    else:
        report.append("fl-zero-watch malloc already present")

    if changed:
        FUNCS.write_text(text)
    print("apply_s639:", "; ".join(report), "; wrote" if changed else "; no change")
    return 0

if __name__ == "__main__":
    sys.exit(main())
