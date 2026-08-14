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

text = path.read_text()
if '[vi-predecessor-entry]' not in text:
    predecessor_entry = '''    /* PATCH: s1149 predecessor entry probe. */
    static int vi_pred_entry_n = 0;
    static uint32_t vi_pred_entry_prev_width = 0xFFFFFFFFu;
    uint32_t vi_pred_entry_width = U32(MEM_W(0x8, S32(0x8013 << 16) - 0x7370));
    if (vi_sel_en && (vi_pred_entry_n < 8 || vi_pred_entry_width != vi_pred_entry_prev_width)) {
        fprintf(stderr, "[vi-predecessor-entry] n=%d width=%u\\n", vi_pred_entry_n, (unsigned)vi_pred_entry_width);
        fflush(stderr);
    }
    vi_pred_entry_prev_width = vi_pred_entry_width;
    ++vi_pred_entry_n;
'''
    selector_counter = '    vi_sel_prev = vi_sel_key;\n    ++vi_sel_n;\n'
    if text.count(selector_counter) != 1:
        raise SystemExit('selector function count mismatch for predecessor entry')
    text = text.replace(selector_counter, selector_counter + predecessor_entry, 1)
    path.write_text(text)

caller = Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c')
caller_text = caller.read_text()
if 'extern uint32_t rs64_vi_committed_width(void);' not in caller_text:
    caller_text = caller_text.replace('#include "funcs.h"\n', '#include "funcs.h"\n\nextern uint32_t rs64_vi_committed_width(void);\n', 1)
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
if '[vi-predecessor-edge]' not in caller_text:
    edge_probe = ('    /* PATCH: s1149 exact predecessor edge probe. */\n'
                  '    static int vi_pred_edge_n = 0;\n'
                  '    if (vi_call_en && vi_pred_edge_n < 16) {\n'
                  '        uint32_t vi_pred_edge_width = U32(MEM_W(0x8, S32(0x8013 << 16) - 0x7370));\n'
                  '        fprintf(stderr, "[vi-predecessor-edge] n=%d width=%u\\n", vi_pred_edge_n, (unsigned)vi_pred_edge_width);\n'
                  '        fflush(stderr);\n'
                  '    }\n'
                  '    ++vi_pred_edge_n;\n')
    marker = '    static int vi_call_en = -1, vi_call_n = 0;\n'
    if caller_text.count(marker) != 1:
        raise SystemExit('selector call probe count mismatch for predecessor edge')
    caller_text = caller_text.replace(marker, edge_probe + marker, 1)

def writer_callsite(callsite, callee):
    return '''    { /* PATCH: s1156 selector-writer callsite. */
        static int vi_w_en = -1, vi_w_n = 0;
        if (vi_w_en < 0) {
            const char* a = getenv("ROGUESQ_LOG_ALL");
            const char* e = getenv("ROGUESQ_LOG_VI_WRITERS");
            vi_w_en = ((a && *a && *a != '0') || (e && *e && *e != '0')) ? 1 : 0;
        }
        uint32_t vi_w_before_a = U32(MEM_BU(S32(0x8012 << 16), -0x579B));
        uint32_t vi_w_before_b = U32(MEM_BU(S32(0x8012 << 16), -0x579C));
        uint32_t vi_w_before_c = U32(MEM_BU(S32(0x8012 << 16), -0x579E));
        uint32_t vi_w_phase = rs64_vi_committed_width();
        ''' + callee + '''
        uint32_t vi_w_after_a = U32(MEM_BU(S32(0x8012 << 16), -0x579B));
        uint32_t vi_w_after_b = U32(MEM_BU(S32(0x8012 << 16), -0x579C));
        uint32_t vi_w_after_c = U32(MEM_BU(S32(0x8012 << 16), -0x579E));
        if (vi_w_en && vi_w_n < 512) {
            fprintf(stderr, "[vi-selector-writer] site=0x''' + callsite + ''' committed_width=%u old=%02X/%02X/%02X new=%02X/%02X/%02X n=%d\\n",
                    (unsigned)vi_w_phase, (unsigned)vi_w_before_a, (unsigned)vi_w_before_b,
                    (unsigned)vi_w_before_c, (unsigned)vi_w_after_a, (unsigned)vi_w_after_b,
                    (unsigned)vi_w_after_c, vi_w_n);
            fflush(stderr);
        }
        ++vi_w_n;
    }
'''

if '[vi-selector-writer] site=0x800183F8' not in caller_text:
    for callsite, callee in (
        ('800183F8', 'buildAndRegisterDefaultMaterial(rdram, ctx);'),
        ('800185DC', 'buildAndRegisterDefaultMaterial(rdram, ctx);'),
        ('80019914', 'applyPendingViChanges(rdram, ctx);'),
    ):
        label = '    // 0x' + callsite + ': jal'
        try:
            label_pos = caller_text.index(label)
            call_pos = caller_text.index('    ' + callee + '\n', label_pos)
        except ValueError:
            raise SystemExit('writer callsite count mismatch for ' + callsite)
        end = call_pos + len('    ' + callee + '\n')
        caller_text = caller_text[:call_pos] + writer_callsite(callsite, callee) + caller_text[end:]
    caller.write_text(caller_text)
print(path)
