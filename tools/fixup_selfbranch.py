#!/usr/bin/env python3
"""s7081: repair N64Recomp's backward out-of-function branch miscompile (s6871).

N64Recomp prints each label at the first instruction whose vram >= label, so
`goto L_T` with T below the function's first instruction lands inside the
function itself (s6871: the voice resampler helpers restart with $t1 rewound
instead of leaving into the caller's "sample finished" tail).

Retail semantics: helper F is a leaf entered by `jal` from caller G; on a
finished one-shot sample it branches straight into G's code at T (store the
last packed word, zero-fill the rest of the buffer, G's epilogue). F has no
frame, so $sp is G's and G's epilogue returns to G's caller.

Fix: F stores T in g_rs64_sbx_target and returns; G checks it after every call
to F and jumps to a new label rs64_sbx_T placed at T inside G. Only pairs where
T lies in a function G that calls F are patched; any other out-of-function goto
(decoded data: data_gap_*) is reported and left alone.
ROGUESQ_SELFBRANCH_FIX=0 (g_rs64_sbx_on = 0) keeps the old miscompiled path.
Idempotent. Usage: fixup_selfbranch.py <RecompiledFuncs dir>
"""
import pathlib, re, sys

TAG = "/* PATCH: s7081 selfbranch */"
DECL = ("extern __thread uint32_t g_rs64_sbx_target; extern int g_rs64_sbx_on; "
        "extern void rs64_sbx_hit(uint32_t fn, uint32_t target); " + TAG + "\n")
FN = re.compile(r'^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{\n')
INS = re.compile(r'^\s*// 0x([0-9A-F]{8}): ')
GO = re.compile(r'goto L_([0-9A-F]{8});')
EXPECT_PAIRS = 16  # s6871 census: 4 helpers x 4 exits


def split_funcs(lines):
    funcs, cur = [], None
    for i, l in enumerate(lines):
        m = FN.match(l)
        if m:
            if cur: cur['end'] = i; funcs.append(cur)
            cur = {'name': m.group(1), 'start': i, 'ins': []}
            continue
        if cur:
            m = INS.match(l)
            if m: cur['ins'].append(int(m.group(1), 16))
    if cur: cur['end'] = len(lines); funcs.append(cur)
    for f in funcs:
        f['lo'] = min(f['ins']) if f['ins'] else 0
        f['hi'] = max(f['ins']) if f['ins'] else 0
    return funcs


def patch_file(p):
    lines = p.read_text().splitlines(keepends=True)
    funcs = split_funcs(lines)
    # (helper, caller, target, line index of goto)
    pairs, skipped = [], []
    for f in funcs:
        for i in range(f['start'], f['end']):
            for m in GO.finditer(lines[i]):
                t = int(m.group(1), 16)
                if f['lo'] <= t <= f['hi']:
                    continue
                g = next((g for g in funcs if g['lo'] <= t <= g['hi'] and g is not f), None)
                call = f"    {f['name']}(rdram, ctx);\n"
                if g is None or not any(lines[j] == call for j in range(g['start'], g['end'])):
                    skipped.append((f['name'], t))
                    continue
                pairs.append((f, g, t, i))
    already = sum(1 for l in lines if TAG in l and 'g_rs64_sbx_target = 0x' in l)
    if not pairs:
        return 0, already, skipped
    ins = {}  # line index -> text to insert before
    after = {}  # line index -> text to insert after
    for f, g, t, i in pairs:
        l = lines[i]
        old = f"goto L_{t:08X};"
        new = (f"{{ if (g_rs64_sbx_on) {{ g_rs64_sbx_target = 0x{t:08X}u; return; }} goto L_{t:08X}; }} {TAG}")
        if TAG in l:
            continue
        lines[i] = l.replace(old, new, 1)
    # caller labels + dispatch, grouped per (caller, helper)
    by_cg = {}
    for f, g, t, i in pairs:
        by_cg.setdefault((g['name'], f['name']), (g, f, set()))[2].add(t)
    for (gn, fn), (g, f, ts) in by_cg.items():
        for t in sorted(ts):
            lab = f"rs64_sbx_{t:08X}:"
            if any(l.startswith(lab) for l in lines[g['start']:g['end']]):
                continue
            j = next(j for j in range(g['start'], g['end'])
                     if lines[j].lstrip().startswith(f"// 0x{t:08X}:"))
            ins.setdefault(j, []).append(f"{lab} {TAG}\n")
        call = f"    {fn}(rdram, ctx);\n"
        cases = " ".join(f"case 0x{t:08X}u: goto rs64_sbx_{t:08X};" for t in sorted(ts))
        disp = (f"    if (__builtin_expect(g_rs64_sbx_target != 0, 0)) {{ uint32_t _sbx = g_rs64_sbx_target; "
                f"g_rs64_sbx_target = 0; rs64_sbx_hit(0x{f['lo']:08X}u, _sbx); switch (_sbx) {{ {cases} "
                f"default: __builtin_trap(); }} }} {TAG}\n")
        for j in range(g['start'], g['end']):
            if lines[j] == call and TAG not in lines[j + 1]:
                after.setdefault(j, []).append(disp)
    out = []
    for j, l in enumerate(lines):
        out += ins.get(j, [])
        out.append(l)
        out += after.get(j, [])
    s = ''.join(out)
    if DECL not in s:
        s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
        if DECL not in s:
            sys.exit(f"s7081 {p.name}: funcs.h anchor missing")
    p.write_text(s)
    return len(pairs), already, skipped


def main():
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
    total, skipped = 0, []
    for p in sorted(base.glob("funcs_*.c")):
        s = p.read_text()
        if 'goto L_' not in s:
            continue
        n, _, sk = patch_file(p)
        total += n
        skipped += [(p.name,) + x for x in sk]
    # count patched helper exits (idempotent re-runs find them already rewritten)
    patched = sum(p.read_text().count('g_rs64_sbx_target = 0x') for p in base.glob("funcs_*.c"))
    for x in skipped:
        print(f"[s7081] left alone (no calling function owns the target): {x[0]} {x[1]} -> 0x{x[2]:08X}")
    if patched != EXPECT_PAIRS:
        sys.exit(f"[s7081] selfbranch: {patched} helper exits patched, expected {EXPECT_PAIRS}")
    print(f"[s7081] selfbranch exits patched: {patched} (pairs found this pass {total}), left alone {len(skipped)}")


if __name__ == '__main__':
    main()
