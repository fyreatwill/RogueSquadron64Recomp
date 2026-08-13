#!/usr/bin/env python3
from pathlib import Path

path = Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_5.c')
text = path.read_text()
start = 'RECOMP_FUNC void selectAndApplyViMode(uint8_t* rdram, recomp_context* ctx) {\n'
entry = start + '''    /* PATCH: s802 VI selector probe; regenerate through this script. */
    static int vi_sel_en = -1;
    static int vi_sel_n = 0;
    static uint32_t vi_sel_prev = 0xFFFFFFFFu;
    if (vi_sel_en < 0) {
        const char* a = getenv("ROGUESQ_LOG_ALL");
        const char* e = getenv("ROGUESQ_LOG_VI_SELECTOR");
        vi_sel_en = ((a && *a && *a != '0') || (e && *e && *e != '0')) ? 1 : 0;
    }
    uint32_t vi_sel_key = (U32(MEM_BU(S32(0x8012 << 16), -0x579B)) << 16) |
                          (U32(MEM_BU(S32(0x8012 << 16), -0x579C)) << 8) |
                          U32(MEM_BU(S32(0x8012 << 16), -0x579E));
    if (vi_sel_en && (vi_sel_n < 8 || vi_sel_key != vi_sel_prev)) {
        fprintf(stderr, "[vi-selector-control] n=%d selector_phys=0x0011A865..67 values=%02X/%02X/%02X\\n",
                vi_sel_n, (unsigned)((vi_sel_key >> 16) & 0xFF),
                (unsigned)((vi_sel_key >> 8) & 0xFF), (unsigned)(vi_sel_key & 0xFF));
        fflush(stderr);
    }
    vi_sel_prev = vi_sel_key;
    ++vi_sel_n;
'''
if 'PATCH: s802 VI selector probe' not in text:
    if text.count(start) != 1:
        raise SystemExit('selector function count mismatch')
    text = text.replace(start, entry, 1)
    label = 'L_8001BBC4:\n'
    selected = label + ('    if (vi_sel_en && vi_sel_n <= 8) {\n'
                        '        fprintf(stderr, "[vi-selector-selected] n=%d table=0x%08X table_width=%u copied_mode=0x80128C90\\n",\n'
                        '                vi_sel_n, U32(ctx->r3), (unsigned)U32(MEM_W(0x8, ctx->r3)));\n'
                        '        fflush(stderr);\n'
                        '    }\n')
    if text.count(label) != 1:
        raise SystemExit('selector label count mismatch')
    text = text.replace(label, selected, 1)
path.write_text(text)

caller = Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c')
caller_text = caller.read_text()
call_needle = '    selectAndApplyViMode(rdram, ctx);\n'
call_probe = ('    static int vi_call_en = -1, vi_call_n = 0;\n'
              '    if (vi_call_en < 0) { const char* e = getenv("ROGUESQ_LOG_VI_SELECTOR"); vi_call_en = (e && *e && *e != \'0\') ? 1 : 0; }\n'
              '    if (vi_call_en && vi_call_n < 8) {\n'
              '        fprintf(stderr, "[vi-selector-callsite] n=%d ra=0x%08X\\n", vi_call_n, U32(ctx->r31));\n'
              '        fflush(stderr);\n'
              '    }\n'
              '    ++vi_call_n;\n'
              '    selectAndApplyViMode(rdram, ctx);\n')
if caller_text.count(call_needle) != 1:
    raise SystemExit('selector callsite count mismatch')
if '[vi-selector-callsite]' not in caller_text:
    caller_text = caller_text.replace(call_needle, call_probe, 1)
    caller.write_text(caller_text)
print(path)
