#!/usr/bin/env python3
"""s5535: replay step after the vendored fixer. Drops whole-line, side-effect-free
diagnostic layers (store watches, swl/swr hook, node/target-store watches, vol /
strncpy-caller / status-table probes) that the live RecompiledFuncs tree does not carry
but the apply_* scripts re-add. s5539 adds brace/paren-balanced scratch-only diagnostic
blocks (s3556, s4466, s4471, s4298, s4561, s4694, m5 callback events, filter-voice probes).
Usage: strip_diag_layers.py <dir>"""
import re, sys, pathlib

# a line is stripped only if it is a single-line statement/decl calling one of these hooks
HOOKS = r"(rs64_s(4222|4299|4597|4601|4602)_\w+|rs64_s4222_store_watch|rs64_s4601_target_store|rs64_s4299_swlr|" \
        r"rs64_s\d+_vol|rs64_s\d+_strncpy_caller|rs64_m\d+_status_table_store|rs64_s4299_nodewatch\w*)"
TAGS = r"PATCH: s(4222|4299|4597|4601|4602|4680)\b"
EXEMPT = {"funcs_23.c", "funcs_24.c"}
LINE = re.compile(HOOKS)
TAG = re.compile(TAGS)

# s5539: statements/blocks the live tree never carried.
BLOCK_START = re.compile(
    r"^\s*\{ (/\* PATCH: (s3556|s4471|s4694)\b|extern void rs64_m5_callback_(transfer|writer)_event|"
    r"static uint32_t s_hd_ptrs|static int s_nd_ctl|extern volatile uint32_t g_rs64_last_guest_pc|"
    r"extern volatile uint32_t g_s4561_synth_n|/\* s4298c)"
    r"|^\s*if \(g_a14_act\) \{"
    r"|^\s*if \(MEM_W\(ctx->r3, 0X4\) != 0 && \(\(uint32_t\)MEM_W\(ctx->r3, 0X4\) >> 24\) != 0xB0u\) (\{ /\* s4298b|fprintf)")
ONE_LINE = re.compile(
    r"^\s*rs64_(s4714_rec|s4223_stk|filter_voice_\w+)\(|"
    r"^extern void rs64_(s4714_rec|s4223_stk|filter_voice_\w+|m5_status_table_store)\(|"
    r"^#include <execinfo\.h>$|^static unsigned long g_a14_call|^\s*\+\+g_a14_reads;|"
    r"^\s*/\* PATCH: s4329 direct D740 witness \*/$")
STR = re.compile(r'"(\\.|[^"\\])*"')

def _bal(ln, op, cl):
    ln = STR.sub('""', ln)
    return ln.count(op) - ln.count(cl)

def strip(text):
    out, n = [], 0
    lines = text.split("\n"); i = 0
    while i < len(lines):
        ln = lines[i]
        hdr = LINE.search(ln) and ln.startswith(("extern void rs64_s", "#define do_swl(", "#define do_swr("))  # s5536: untagged header decls
        if hdr or (TAG.search(ln) and LINE.search(ln) and (ln.lstrip().startswith(("{", "rs64_", "extern", "#define")))) or ONE_LINE.search(ln):
            n += 1; i += 1; continue
        if BLOCK_START.search(ln):
            paren = ln.rstrip().endswith("fprintf(") or (ln.lstrip().startswith("if (MEM_W") and not ln.rstrip().endswith("{ /* s4298b: host backtrace names the guest caller (recomp keeps no ra) */") and "{ /*" not in ln)
            op, cl = ("(", ")") if paren else ("{", "}")
            d = _bal(ln, op, cl); j = i
            while (d > 0 or (paren and not lines[j].rstrip().endswith(";"))) and j + 1 < len(lines):
                j += 1; d += _bal(lines[j], op, cl)
            n += j - i + 1; i = j + 1; continue
        out.append(ln); i += 1
    return "\n".join(out), n

def main():
    d = pathlib.Path(sys.argv[1]); total = 0
    for p in sorted(d.glob("*.c")):
        if p.name in EXEMPT:  # s5536: live funcs_23/24 keep their hooks (s4653 restores them)
            continue
        s = p.read_text(errors="surrogateescape")
        t, n = strip(s)
        if n:
            p.write_text(t, errors="surrogateescape"); total += n
    print(f"strip_diag_layers: removed {total} lines")

if __name__ == "__main__":
    main()
