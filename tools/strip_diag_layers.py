#!/usr/bin/env python3
"""s5535: replay step after the vendored fixer. Drops whole-line, side-effect-free
diagnostic layers (store watches, swl/swr hook, node/target-store watches, vol /
strncpy-caller / status-table probes) that the live RecompiledFuncs tree does not carry
but the apply_* scripts re-add. Usage: strip_diag_layers.py <dir>"""
import re, sys, pathlib

# a line is stripped only if it is a single-line statement/decl calling one of these hooks
HOOKS = r"(rs64_s(4222|4299|4597|4601|4602)_\w+|rs64_s4222_store_watch|rs64_s4601_target_store|rs64_s4299_swlr|" \
        r"rs64_s\d+_vol|rs64_s\d+_strncpy_caller|rs64_m\d+_status_table_store|rs64_s4299_nodewatch\w*)"
TAGS = r"PATCH: s(4222|4299|4597|4601|4602|4680)\b"
EXEMPT = {"funcs_23.c", "funcs_24.c"}
LINE = re.compile(HOOKS)
TAG = re.compile(TAGS)

def strip(text):
    out, n = [], 0
    for ln in text.split("\n"):
        hdr = LINE.search(ln) and ln.startswith(("extern void rs64_s", "#define do_swl(", "#define do_swr("))  # s5536: untagged header decls
        if hdr or (TAG.search(ln) and LINE.search(ln) and (ln.lstrip().startswith(("{", "rs64_", "extern", "#define")))):
            n += 1
            continue
        out.append(ln)
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
