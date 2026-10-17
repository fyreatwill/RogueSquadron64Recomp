#!/usr/bin/env python3
"""Consolidated indirect-control-flow idiom table (s5357, M3).

Classes over RecompiledFuncs/funcs_*.c:
  jr ra            returns (counted)
  jr jump-table    each `switch (jr_addend_X >> 2)` must: (1) have contiguous cases 0..n-1,
                   (2) goto only labels defined in the SAME function, (3) end in a
                   switch_error default, (4) have jr_addend_X assigned in the same function.
  jr/jalr other    register / $zero sites (loud-fail via LOOKUP_FUNC, see s4821)
  Positive control: selftest feeds synthetic bad switches; each defect must be flagged.
"""
import re, sys, collections
from pathlib import Path

FN = re.compile(r'^RECOMP_FUNC void (\w+)\(')
SW = re.compile(r'switch \((jr_addend_\w+) >> 2\)')
CASE = re.compile(r'case (\d+): goto (\w+);')
OP = re.compile(r'// 0x[0-9A-F]{8}: (?:\.word\s+\S+\s+# )?(jr|jalr)\s+\$(\w+)')


def audit_lines(lines):
    """Return (stats Counter, defects list of (fn, addend, reason))."""
    st = collections.Counter()
    bad = []
    funcs = []
    cur = None
    for l in lines:
        m = FN.match(l)
        if m:
            cur = (m.group(1), [])
            funcs.append(cur)
        if cur:
            cur[1].append(l)
    for name, body in funcs:
        text = "\n".join(body)
        labels = set(re.findall(r'^\s*(L_\w+):', text, re.M))
        for i, l in enumerate(body):
            m = OP.search(l)
            if m:
                op, r = m.groups()
                if op == 'jr' and r == 'ra':
                    st['jr_ra'] += 1
                elif r == 'zero':
                    st['zero'] += 1
                else:
                    st['reg_or_table'] += 1
            m = SW.search(l)
            if not m:
                continue
            st['tables'] += 1
            add = m.group(1)
            cases = []
            err = False
            j = i + 1
            while j < len(body) and not body[j].startswith('    }'):
                c = CASE.search(body[j])
                if c:
                    cases.append((int(c.group(1)), c.group(2)))
                if 'switch_error(' in body[j]:
                    err = True
                j += 1
            st['cases'] += len(cases)
            if [c for c, _ in cases] != list(range(len(cases))):
                bad.append((name, add, 'noncontiguous'))
            miss = {t for _, t in cases if t not in labels}
            if miss:
                bad.append((name, add, 'label-not-in-fn:' + ','.join(sorted(miss))))
            if not err:
                bad.append((name, add, 'no-switch_error-default'))
            if not re.search(r'\b' + add + r'\s*=', text):
                bad.append((name, add, 'addend-unassigned'))
            if not cases:
                bad.append((name, add, 'empty'))
    return st, bad


SELF_OK = "\n".join([
    "RECOMP_FUNC void f(a) {",
    "    jr_addend_1 = ctx->r2;",
    "    // 0x80000000: jr          $v0",
    "    switch (jr_addend_1 >> 2) {",
    "        case 0: goto L_A; break;",
    "        case 1: goto L_A; break;",
    "        default: switch_error(__func__, 0x1, 0x2);",
    "    }",
    "L_A:",
    "}",
])


def selftest():
    ok_st, ok_bad = audit_lines(SELF_OK.splitlines())
    assert ok_st['tables'] == 1 and not ok_bad, (ok_st, ok_bad)
    muts = {
        'label-not-in-fn': lambda s: s.replace('L_A:', 'L_B:'),
        'no-switch_error-default': lambda s: s.replace('switch_error', 'nothing'),
        'noncontiguous': lambda s: s.replace('case 1:', 'case 3:'),
        'addend-unassigned': lambda s: s.replace('jr_addend_1 =', 'x ='),
    }
    for want, f in muts.items():
        _, bad = audit_lines(f(SELF_OK).splitlines())
        assert any(want in r for _, _, r in bad), (want, bad)
    print("selftest: clean synthetic passes; 4/4 injected defects flagged")


if __name__ == '__main__':
    selftest()
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '../N64Recomp/RecompiledFuncs')
    tot = collections.Counter()
    allbad = []
    for p in sorted(root.glob('funcs_*.c')):
        s, b = audit_lines(p.read_text(errors='replace').splitlines())
        tot.update(s)
        allbad += b
    print(dict(tot))
    print("defects:", len(allbad))
    for d in allbad[:40]:
        print(d)
