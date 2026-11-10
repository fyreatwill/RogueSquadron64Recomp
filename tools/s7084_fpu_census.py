#!/usr/bin/env python3
"""s7084 N64Recomp FPU-lowering census over the pristine front-end output (scratch/s7082/regen,
regenerate with tools/regen_front.sh).

For every FPU instruction site (the generator's "// 0xADDR: mnemonic" comment) it takes the first
lowered statement after the comment (CHECK_FR / NAN_CHECK lines skipped) and checks it against the
lowering shape that is correct for the R4300 op. It also reports:
  * rounding-mode windows: every cvt.w/cvt.l site, and whether it sits between a set_cop1_cs(x)
    and the restoring set_cop1_cs in the same function (the only non-default FCSR.RM writes);
  * cfc1 results masked with FCSR flag/cause bits (get_cop1_cs returns RM only, so flags read 0);
  * odd-FPR direct accesses (ctx->fODD.*): each must be preceded by CHECK_FR(ctx, ODD), an assert
    that is live in this build (Debug, no NDEBUG), so an FR=0 execution aborts loudly, plus which
    functions toggle Status.FR themselves (cop0_status_write);
  * likely branches bc1tl/bc1fl: delay slot inside the taken block, followed by goto skip_N.
Positive control: convertMat3x4ToN64Mtx's cvt.w.s sites must be listed in default mode.
Negative control: one CVT_W_S lowering is mutated to TRUNC_W_S in memory; the shape check must
flag exactly that site. Exit 0 iff both controls pass and no unexplained shape mismatch remains.
"""
import collections, glob, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REGEN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'scratch', 's7082', 'regen')

FR = r'ctx->f(\d+)\.(?:fl|d)'
FI = r'(?:ctx->f(\d+)\.u32l|ctx->f_odd\[\((\d+) - 1\) \* 2\])'
SHAPES = {
    'add.s': r'ctx->f\d+\.fl = ctx->f\d+\.fl \+ ctx->f\d+\.fl;', 'add.d': r'ctx->f\d+\.d = ctx->f\d+\.d \+ ctx->f\d+\.d;',
    'sub.s': r'ctx->f\d+\.fl = ctx->f\d+\.fl - ctx->f\d+\.fl;', 'sub.d': r'ctx->f\d+\.d = ctx->f\d+\.d - ctx->f\d+\.d;',
    'mul.s': r'ctx->f\d+\.fl = MUL_S\(ctx->f\d+\.fl, ctx->f\d+\.fl\);', 'mul.d': r'ctx->f\d+\.d = MUL_D\(ctx->f\d+\.d, ctx->f\d+\.d\);',
    'div.s': r'ctx->f\d+\.fl = DIV_S\(ctx->f\d+\.fl, ctx->f\d+\.fl\);', 'div.d': r'ctx->f\d+\.d = DIV_D\(ctx->f\d+\.d, ctx->f\d+\.d\);',
    'sqrt.s': r'ctx->f\d+\.fl = sqrtf\(ctx->f\d+\.fl\);', 'abs.s': r'ctx->f\d+\.fl = fabsf\(ctx->f\d+\.fl\);',
    'abs.d': r'ctx->f\d+\.d = fabs\(ctx->f\d+\.d\);', 'neg.s': r'ctx->f\d+\.fl = -ctx->f\d+\.fl;',
    'neg.d': r'ctx->f\d+\.d = -ctx->f\d+\.d;', 'mov.s': r'ctx->f\d+\.fl = ctx->f\d+\.fl;', 'mov.d': r'ctx->f\d+\.d = ctx->f\d+\.d;',
    'cvt.s.w': r'ctx->f\d+\.fl = CVT_S_W\(' + FI + r'\);', 'cvt.d.w': r'ctx->f\d+\.d = CVT_D_W\(' + FI + r'\);',
    'cvt.s.d': r'ctx->f\d+\.fl = CVT_S_D\(ctx->f\d+\.d\);', 'cvt.d.s': r'ctx->f\d+\.d = CVT_D_S\(ctx->f\d+\.fl\);',
    'cvt.w.s': FI + r' = CVT_W_S\(ctx->f\d+\.fl\);', 'cvt.w.d': FI + r' = CVT_W_D\(ctx->f\d+\.d\);',
    'trunc.w.s': FI + r' = TRUNC_W_S\(ctx->f\d+\.fl\);', 'trunc.w.d': FI + r' = TRUNC_W_D\(ctx->f\d+\.d\);',
    'ceil.w.d': FI + r' = S32\(ceil\(ctx->f\d+\.d\)\);',
    'c.lt.s': r'c1cs = ctx->f\d+\.fl < ctx->f\d+\.fl;', 'c.lt.d': r'c1cs = ctx->f\d+\.d < ctx->f\d+\.d;',
    'c.le.s': r'c1cs = ctx->f\d+\.fl <= ctx->f\d+\.fl;', 'c.le.d': r'c1cs = ctx->f\d+\.d <= ctx->f\d+\.d;',
    'c.ole.s': r'c1cs = ctx->f\d+\.fl <= ctx->f\d+\.fl;',
    'c.eq.s': r'c1cs = ctx->f\d+\.fl == ctx->f\d+\.fl;', 'c.eq.d': r'c1cs = ctx->f\d+\.d == ctx->f\d+\.d;',
    'bc1t': r'if \(c1cs\) \{', 'bc1f': r'if \(!c1cs\) \{', 'bc1tl': r'if \(c1cs\) \{', 'bc1fl': r'if \(!c1cs\) \{',
    'mfc1': r'ctx->r\d+ = \(int32_t\)' + FI + ';', 'mtc1': FI + r' = (?:ctx->r\d+|0);',
    'lwc1': FI + r' = MEM_W\(', 'swc1': r'MEM_W\(.*\) = ' + FI + ';',
    'ldc1': r'ctx->f\d+\.u64 = LD\(', 'sdc1': r'SD\(ctx->f\d+\.u64,',
    'cfc1': r'ctx->r\d+ = get_cop1_cs\(\);', 'ctc1': r'set_cop1_cs\(ctx->r\d+\);',
}
FPU_OP = re.compile(r'// 0x([0-9A-F]{8}): ([a-z0-9.]+)\s')
FUNC = re.compile(r'^RECOMP_FUNC void (\w+)\(')
SKIP = re.compile(r'^\s*(CHECK_FR|NAN_CHECK|$)')
ODD = re.compile(r'ctx->f(1|3|5|7|9|11|13|15|17|19|21|23|25|27|29|31)\.(fl|d|u32l|u32h|u64)')


def load():
    files = sorted(glob.glob(os.path.join(REGEN, 'funcs_*.c')))
    if not files:
        sys.exit(f'no regen output in {REGEN} (run tools/regen_front.sh)')
    out = []
    for f in files:
        with open(f, errors='replace') as h:
            out.append((os.path.basename(f), h.read().split('\n')))
    return out


def sites(files):
    """yield (file, func, line_no, addr, op, first_lowered_stmt, comment_index) for FPU ops."""
    for fn, lines in files:
        func = None
        for i, ln in enumerate(lines):
            m = FUNC.match(ln)
            if m:
                func = m.group(1); continue
            m = FPU_OP.search(ln + ' ')
            if not m or m.group(2) not in SHAPES:
                continue
            # first lowered statement (delay-slot copies of a branch are lowered after the branch).
            # MEM_W stores can carry a writer-parity prefix in later passes; here regen is pristine.
            j = i + 1
            while j < len(lines) and SKIP.match(lines[j]):
                j += 1
            stmt = lines[j].strip() if j < len(lines) else ''
            stmt = stmt.lstrip('{ ').split(';')[0] + ';' if stmt else stmt
            yield fn, func, i, m.group(1), m.group(2), stmt, j


def census(files, mutate=None):
    per = collections.defaultdict(lambda: [0, 0]); bad = []
    rnd = []; cfc1 = []; mpos = []
    for fn, func, i, addr, op, stmt, j in sites(files):
        if mutate and (fn, j) == mutate:
            stmt = stmt.replace('CVT_W_S', 'TRUNC_W_S')
        ok = re.search(SHAPES[op], stmt) is not None
        if op == 'mtc1' and not ok:               # mtc1 $zero lowers to "= 0"; mtc1 from a GPR
            ok = re.search(FI + r' = ', stmt) is not None and 'ctx->r' in stmt
        per[op][0 if ok else 1] += 1
        if not ok:
            bad.append((fn, i + 1, func, addr, op, stmt))
        if op in ('cvt.w.s', 'cvt.w.d', 'cvt.l.s', 'cvt.l.d'):
            rnd.append((fn, i + 1, func, addr, op))
    return per, bad, rnd


def windows(files):
    """set_cop1_cs windows per function: list of (func, set_line, restore_line)."""
    res = []
    for fn, lines in files:
        func = None; open_at = None
        for i, ln in enumerate(lines):
            m = FUNC.match(ln)
            if m:
                func = m.group(1); open_at = None; continue
            if 'set_cop1_cs(' in ln:
                if open_at is None:
                    open_at = i
                else:
                    res.append((fn, func, open_at, i))
                    # a second set before the restore stays in the same window
            if 'get_cop1_cs()' in ln:
                nxt = ' '.join(lines[i + 1:i + 6])
                if re.search(r'& 0X(78|7C|3F|F80|1F000|3F000)', nxt):
                    res.append((fn, func, i, -1))
    return res


def odd_access(files):
    per_func = collections.defaultdict(lambda: [0, 0, 0, 0])  # direct, guarded, f_odd, status_writes
    for fn, lines in files:
        func = None
        for i, ln in enumerate(lines):
            m = FUNC.match(ln)
            if m:
                func = m.group(1); continue
            if 'cop0_status_write' in ln:
                per_func[func][3] += 1
            if 'f_odd[' in ln:
                per_func[func][2] += 1
            for mo in ODD.finditer(ln):
                per_func[func][0] += 1
                n = mo.group(1)
                back = lines[max(0, i - 6):i]
                if any(f'CHECK_FR(ctx, {n});' in b for b in back):
                    per_func[func][1] += 1
    return per_func


def likely(files):
    good = badl = 0; badl_sites = []
    for fn, lines in files:
        for i, ln in enumerate(lines):
            m = FPU_OP.search(ln + ' ')
            if not m or m.group(2) not in ('bc1tl', 'bc1fl'):
                continue
            blk = lines[i + 1:i + 14]
            txt = '\n'.join(blk)
            # shape: if (cond) { <delay slot> goto L; } goto skip_N; <dead copy> skip_N:
            if re.search(r'if \(!?c1cs\) \{.*?goto L_[0-9A-F]+;\s*\}\s*goto skip_\d+;', txt, re.S):
                good += 1
            else:
                badl += 1; badl_sites.append((fn, i + 1))
    return good, badl, badl_sites


def main():
    files = load()
    per, bad, rnd = census(files)
    print('== FPU op lowering shapes (op: matched / unmatched)')
    for op in sorted(per, key=lambda o: -sum(per[o])):
        print(f'  {op:10s} {per[op][0]:6d} / {per[op][1]}')
    print(f'  unmatched sites: {len(bad)}')
    for b in bad[:25]:
        print('   ', *b)
    w = windows(files)
    print('== FCSR windows / flag reads')
    for fn, func, a, b in w:
        print(f'  {fn}:{a + 1} {func} ' + ('flag-mask read (get_cop1_cs returns RM only -> 0)' if b < 0 else f'RM window to line {b + 1}'))
    print('== cvt.w/cvt.l sites (rounding-mode sensitive)')
    pc = 0
    for fn, ln, func, addr, op in rnd:
        inside = any(f == fn and a < ln - 1 < b for f, _, a, b in w if b >= 0)
        mode = 'RM window (RZ, mode 1)' if inside else 'default RM=0 (nearest-even)'
        print(f'  {addr} {op:8s} {func:32s} {mode}')
        if func == 'convertMat3x4ToN64Mtx' and not inside:
            pc += 1
    po = odd_access(files)
    print('== odd-FPR accesses per function (direct, CHECK_FR-guarded, f_odd, status writes)')
    tot_d = tot_g = 0
    for func, (d, g, fo, sw) in sorted(po.items(), key=lambda kv: -kv[1][0] - kv[1][2]):
        if d or fo:
            print(f'  {func:36s} direct={d:4d} guarded={g:4d} f_odd={fo:3d} status_writes={sw}')
            tot_d += d; tot_g += g
    print(f'  total direct={tot_d} guarded={tot_g} unguarded={tot_d - tot_g}')
    g, bl, bls = likely(files)
    print(f'== likely branches bc1tl/bc1fl: shape ok {g}, other {bl}', bls[:5])
    # negative control: mutate the first convertMat3x4ToN64Mtx cvt.w.s lowering
    tgt = next(((fn, j) for fn, func, i, a, op, s, j in sites(files)
                if func == 'convertMat3x4ToN64Mtx' and op == 'cvt.w.s'), None)
    _, bad2, _ = census(files, mutate=tgt)
    neg = len(bad2) == len(bad) + 1
    print(f'== controls: positive convertMat3x4ToN64Mtx cvt.w.s in default mode = {pc} (need 3); '
          f'negative mutation flagged = {neg}')
    sys.exit(0 if pc == 3 and neg and tot_d == tot_g and bl == 0 else 1)


if __name__ == '__main__':
    main()
